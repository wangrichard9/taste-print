"""Write-once final test for frozen raw co-likes; no training or app changes."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path

import numpy as np
from scipy.sparse import load_npz

from co_like import score_likes
from content_ablation import shuffled_profile_indices, status_counts
from discover_service import load_engine
from download_foodcom import sha256
from prepare_recommendation_data import ROOT, SEED
from recommendation import ranking_metrics
from run_behavior_comparison import load_configuration, old_hashes
from run_content_ablation import measure, comparison_interval, reconstruct_histories
from run_recommendation_experiment import load_protocol

OUT = ROOT / 'data/processed/ml05'
EXPERIMENT = 'ml05-final-raw-v1'
CODE = ('run_final_evaluation.py', 'test_final_evaluation.py', 'co_like.py',
        'recommendation.py', 'content_ablation.py', 'run_content_ablation.py',
        'prepare_recommendation_data.py', 'run_recommendation_experiment.py',
        'run_behavior_comparison.py', 'run_collaborative_experiment.py',
        'collaborative.py', 'discover_service.py', 'ingredient_matching.py',
        'group_recommendation.py', 'download_foodcom.py', 'audit_foodcom.py')
CHOICES = {'primary': ['popularity', 'direct/raw'], 'k': 10, 'profiles': 300,
           'candidates': 5006, 'seed_likes': 6, 'bootstrap_resamples': 2000,
           'seed': SEED, 'control': 'fixed_deranged_seeds_recipient_exclusions',
           'serving': 'existing_discover_positive_then_popularity'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_once(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def previous_hashes():
    hashes = old_hashes()
    hashes.update({f'ml04/{path.name}': sha256(path)
                   for path in sorted((ROOT / 'data/processed/ml04').iterdir()) if path.is_file()})
    return hashes


def implementation_hashes():
    return {name: sha256(Path(__file__).with_name(name)) for name in CODE}


def prepare():
    # These validators hash the reserved file but do not deserialize its labels.
    load_protocol()
    load_configuration()
    selected = read_json(ROOT / 'data/processed/ml04/results.json')
    if selected['provisional_behavioral_nominee'] != 'direct/raw' or selected['test_scored']:
        raise ValueError('Expected the frozen, validation-selected raw nominee')
    OUT.mkdir(parents=True, exist_ok=True)
    write_once(OUT / 'protocol.json', {
        'experiment': EXPERIMENT, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'choices': CHOICES, 'previous_artifact_sha256': previous_hashes(),
        'implementation_sha256': implementation_hashes(),
        'protocol_document_sha256': sha256(ROOT / 'docs/ML_05_PROTOCOL.md'),
        'test_opened_at_registration': False})
    print('Final protocol registered without opening test profiles. No fitting performed.')


def registration():
    receipt = read_json(OUT / 'protocol.json')
    if (receipt['experiment'] != EXPERIMENT or receipt['choices'] != CHOICES
            or receipt['previous_artifact_sha256'] != previous_hashes()
            or receipt['implementation_sha256'] != implementation_hashes()
            or receipt['protocol_document_sha256'] != sha256(ROOT / 'docs/ML_05_PROTOCOL.md')
            or receipt['test_opened_at_registration'] is not False):
        raise ValueError('Registered final choices, code or inputs changed; stop')
    return receipt


def validate_profiles(profiles, ids, validation_keys, expected_count=300):
    if not isinstance(profiles, list) or len(profiles) != expected_count:
        raise ValueError('Unexpected reserved population')
    keys = set()
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError('Invalid profile')
        key = profile.get('user_key')
        if (not isinstance(key, str) or len(key) != 64
                or any(c not in '0123456789abcdef' for c in key)
                or int(key, 16) % 100 < 90 or key in keys or key in validation_keys):
            raise ValueError('Test people must be unique, test-partition and validation-disjoint')
        keys.add(key)
        for field in ('likes', 'seen', 'relevant'):
            entries = profile.get(field)
            if (not isinstance(entries, list) or not entries
                    or any(type(item) is not int or item not in ids for item in entries)
                    or len(entries) != len(set(entries))):
                raise ValueError('Invalid canonical recipe choices/targets')
        if (len(profile['likes']) != 6 or not set(profile['likes']) <= set(profile['seen'])
                or set(profile['seen']) & set(profile['relevant'])
                or not isinstance(profile.get('seed_cutoff_utc'), str)):
            raise ValueError('Six earlier likes and disjoint future targets are required')


def scores_for(catalog, profiles, weights):
    # No relevant/future/rating field is inspected here.
    index = {row['id']: i for i, row in enumerate(catalog)}
    seeds = [[index[recipe_id] for recipe_id in profile['likes']] for profile in profiles]
    return score_likes(weights, seeds)


def summarize_rankings(top_ids, catalog, profiles, histories):
    if not (len(top_ids) == len(profiles) == len(histories)) or not profiles:
        raise ValueError('Rankings and histories must align')
    rows, recommended = [], Counter()
    statuses = Counter({'known_high': 0, 'known_lower': 0, 'unknown': 0})
    head = {row['id'] for row in sorted(catalog, key=lambda row: (-row['training_like_count'], row['id']))[:100]}
    allowed = {row['id'] for row in catalog}
    for ranked, profile, history in zip(top_ids, profiles, histories):
        if len(ranked) != 10 or not set(ranked) <= allowed or set(ranked) & set(profile['seen']):
            raise ValueError('Expected ten eligible unseen recipes')
        rows.append(ranking_metrics(ranked, profile['relevant'], 10))
        recommended.update(ranked)
        statuses.update(status_counts(ranked, {row['recipe_id']: row['rating'] for row in history['future']}))
    return {
        'metrics': {**{name + '@10': float(np.mean([row[name] for row in rows])) for name in rows[0]},
                    'catalog_coverage@10': len(recommended) / len(catalog),
                    'people_with_hit': int(sum(row['hit_rate'] for row in rows))},
        'top10_rating_status': dict(statuses), 'unique_recommended_recipes': len(recommended),
        'recovered_like_slots': statuses['known_high'],
        'largest_single_recipe_recommendation_share': max(recommended.values()) / (len(profiles) * 10),
        'fitting_top100_recommendation_share': sum(count for recipe_id, count in recommended.items() if recipe_id in head) / (len(profiles) * 10),
        'ndcg_per_person': [row['ndcg'] for row in rows]}


def aggregate(result):
    return {key: value for key, value in result.items() if key not in ('ndcg_per_person', 'top_recipe_ids')}


def evaluate():
    configuration = registration()
    if (OUT / 'test-started.json').exists():
        raise ValueError('Test already opened or interrupted: verify receipt; do not score again')
    protocol, catalog = load_protocol()
    if len(catalog) != CHOICES['candidates']:
        raise ValueError('Unexpected candidate catalog')
    weights = load_npz(ROOT / 'data/processed/ml04/direct_raw.npz')
    validation = read_json(ROOT / 'data/processed/ml01/validation.json')
    validation_histories = read_json(ROOT / 'data/processed/ml02/histories.json')
    popularity = np.asarray([row['training_like_count'] for row in catalog], dtype=float)
    old = read_json(ROOT / 'data/processed/ml04/results.json')['metrics_and_diagnostics']
    for name, values in [('direct/raw', scores_for(catalog, validation, weights)),
                         ('popularity', np.broadcast_to(popularity, (len(validation), len(catalog))))]:
        if measure(values, catalog, validation, validation_histories)['metrics'] != old[name]['metrics']:
            raise ValueError('Frozen validation metrics failed exact reproduction')
    engine = load_engine()
    registration()
    write_once(OUT / 'test-started.json', {
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'protocol_sha256': sha256(OUT / 'protocol.json'), 'validation_metrics_reproduced': True})
    print('Validation reproduction passed. Opening the registered final test once.', flush=True)
    profiles = read_json(ROOT / 'data/processed/ml01/test.json')
    validate_profiles(profiles, {row['id'] for row in catalog}, {row['user_key'] for row in validation})
    histories = reconstruct_histories(protocol, catalog, profiles)
    raw = scores_for(catalog, profiles, weights)
    shuffled = shuffled_profile_indices(len(profiles), SEED)
    matrices = {'popularity': np.broadcast_to(popularity, raw.shape),
                'direct/raw': raw, 'shuffled_raw': raw[shuffled]}
    measured = {name: measure(values, catalog, profiles, histories) for name, values in matrices.items()}
    results = {name: {**result, **summarize_rankings(result['top_recipe_ids'], catalog, profiles, histories)}
               for name, result in measured.items()}
    served_ids, fallback_slots = [], 0
    for profile in profiles:
        response = engine.recommend({'likes': [f'foodcom:{i}' for i in profile['likes']],
                                     'passes': [f'foodcom:{i}' for i in sorted(set(profile['seen']) - set(profile['likes']))]})
        top = response['items'][:10]
        served_ids.append([int(item['id'].removeprefix('foodcom:')) for item in top])
        fallback_slots += sum(item['basis'] == 'popularity' for item in top)
    serving = summarize_rankings(served_ids, catalog, profiles, histories)
    all_high = [sum(row['rating'] >= 4 for row in history['future']) for history in histories]
    head = {row['id'] for row in sorted(catalog, key=lambda row: (-row['training_like_count'], row['id']))[:100]}
    in_catalog_high = sum(len(profile['relevant']) for profile in profiles)
    history_diagnostics = {'all_300_profiles_reconstructed': True,
        'future_high_records_all_content': sum(all_high), 'future_high_records_in_catalog': in_catalog_high,
        'pooled_positive_candidate_coverage': in_catalog_high / sum(all_high),
        'mean_person_positive_candidate_coverage': float(np.mean([len(p['relevant']) / n for p, n in zip(profiles, all_high)])),
        'withheld_high_top100_fraction': sum(i in head for p in profiles for i in p['relevant']) / in_catalog_high}
    registration()
    write_once(OUT / 'histories.json', histories)
    write_once(OUT / 'rankings.json', {
        **{name: {'top_recipe_ids': result['top_recipe_ids'], 'ndcg_per_person': result['ndcg_per_person']} for name, result in results.items()},
        'discover_serving': {'top_recipe_ids': served_ids, 'ndcg_per_person': serving['ndcg_per_person']}})
    output = {'experiment': EXPERIMENT, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
        'split': 'test', 'test_scored': True, 'profiles': len(profiles), 'candidates': len(catalog),
        'eligible_test_profiles': protocol['evaluation']['test']['eligible_profiles'],
        'validation_metrics_reproduced': True, 'previous_artifacts_unchanged': True,
        'metrics_and_diagnostics': {name: aggregate(result) for name, result in results.items()},
        'raw_minus_popularity_ndcg': comparison_interval(results['popularity']['ndcg_per_person'], results['direct/raw']['ndcg_per_person']),
        'correct_minus_shuffled_ndcg': comparison_interval(results['shuffled_raw']['ndcg_per_person'], results['direct/raw']['ndcg_per_person']),
        'discover_serving_diagnostic': {**aggregate(serving), 'popularity_fallback_top10_slots': fallback_slots,
            'top10_lists_different_from_frozen_raw': sum(a != b for a, b in zip(served_ids, results['direct/raw']['top_recipe_ids']))},
        'source_history_check': history_diagnostics, 'registration_sha256': sha256(OUT / 'protocol.json'),
        'previous_artifact_sha256': configuration['previous_artifact_sha256'],
        'implementation_sha256': configuration['implementation_sha256'],
        'output_sha256': {name: sha256(OUT / name) for name in ('histories.json', 'rankings.json', 'test-started.json')},
        'packages': {name: version(name) for name in ('numpy', 'scipy', 'pyarrow')},
        'limitations': protocol['limitations'] + [
            'One selected method, no tuning after final evaluation; estimates do not establish visitor or group quality.',
            'Shuffled contrast is a fixed-profile diagnostic, not causal deconfounding.',
            'Existing service health and old training receipts are historical/static, not final-evaluation status.']}
    write_once(OUT / 'results.json', output)
    write_once(OUT / 'completion.json', {'results_sha256': sha256(OUT / 'results.json'),
                                        'registration_sha256': sha256(OUT / 'protocol.json')})
    verify()
    print(json.dumps({key: output[key] for key in ('metrics_and_diagnostics', 'raw_minus_popularity_ndcg',
        'correct_minus_shuffled_ndcg', 'discover_serving_diagnostic', 'source_history_check')}, indent=2))


def verify():
    configuration = registration()
    result = read_json(OUT / 'results.json')
    completion = read_json(OUT / 'completion.json')
    if (completion != {'results_sha256': sha256(OUT / 'results.json'),
                       'registration_sha256': sha256(OUT / 'protocol.json')}
            or result['experiment'] != EXPERIMENT or result['test_scored'] is not True or result['split'] != 'test'
            or result['profiles'] != CHOICES['profiles'] or result['candidates'] != CHOICES['candidates']
            or result['registration_sha256'] != sha256(OUT / 'protocol.json')
            or result['previous_artifact_sha256'] != configuration['previous_artifact_sha256']
            or result['implementation_sha256'] != configuration['implementation_sha256']
            or set(result['output_sha256']) != {'histories.json', 'rankings.json', 'test-started.json'}
            or any(sha256(OUT / name) != expected for name, expected in result['output_sha256'].items())):
        raise ValueError('Incomplete or changed final receipt')
    print('Completed final receipt and unchanged predecessors verified without rescoring.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'evaluate', 'verify'))
    args = parser.parse_args()
    {'prepare': prepare, 'evaluate': evaluate, 'verify': verify}[args.command]()


if __name__ == '__main__':
    main()
