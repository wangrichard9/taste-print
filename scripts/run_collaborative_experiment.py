"""ML 03: train on fitting likes; evaluate validation only; try local profiles."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import time

import numpy as np
import pyarrow.parquet as pq
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from threadpoolctl import threadpool_limits

from collaborative import fit, fold_in, blend_scores
from content_ablation import profile_scores, shuffled_profile_indices
from download_foodcom import sha256
from prepare_recommendation_data import ROOT, OUT as BASE, SEED, dump
from recommendation import rank
from run_content_ablation import OUT as CONTENT, CASES, load_frozen, measure, comparison_interval, preserved_hashes
from run_recommendation_experiment import load_embeddings

OUT = ROOT / 'data/processed/ml03'
PARAMETERS = {'dimensions': 32, 'iterations': 12, 'alpha': 20.0, 'regularization': 1.0, 'seed': SEED}
WEIGHTS = (.25, .50, .75)
CODE = ('collaborative.py', 'run_collaborative_experiment.py', 'recommendation.py',
        'run_content_ablation.py', 'content_ablation.py')


def code_hashes():
    return {name: sha256(Path(__file__).parent / name) for name in CODE}


def inputs():
    _, protocol, catalog, profiles = load_frozen()
    embeddings, _ = load_embeddings(protocol, catalog)
    history_path = CONTENT / 'histories.json'
    receipt = json.loads((CONTENT / 'histories-manifest.json').read_text(encoding='utf-8'))
    if receipt['sha256'] != sha256(history_path) or receipt['baseline_hashes'] != preserved_hashes():
        raise ValueError('Frozen diagnostic histories changed')
    histories = json.loads(history_path.read_text(encoding='utf-8'))
    if len(histories) != len(profiles):
        raise ValueError('Diagnostic histories must align with validation profiles')
    return protocol, catalog, profiles, embeddings, histories


def training_matrix(catalog, profiles):
    records = pq.read_table(BASE / 'train.parquet', columns=['user_key', 'recipe_id', 'rating']).to_pylist()
    fitting_users = {row['user_key'] for row in records}
    if fitting_users & {profile['user_key'] for profile in profiles}:
        raise ValueError('Validation people must never be fitting users')
    positives = [row for row in records if row['rating'] >= 4]
    users = sorted({row['user_key'] for row in positives})
    user_index = {key: i for i, key in enumerate(users)}
    item_index = {row['id']: i for i, row in enumerate(catalog)}
    if any(row['recipe_id'] not in item_index for row in records):
        raise ValueError('Training recipes are not aligned with the frozen catalog')
    matrix = csr_matrix((np.ones(len(positives)),
        ([user_index[row['user_key']] for row in positives], [item_index[row['recipe_id']] for row in positives])),
        shape=(len(users), len(catalog)))
    matrix.sort_indices()
    if matrix.nnz != len(positives) or (matrix.data != 1).any():
        raise ValueError('Training person/recipe pairs must be unique')
    lengths = matrix.getnnz(axis=1)
    components, labels = connected_components(matrix.T @ matrix, directed=False)
    stats = {'explicit_rows': len(records), 'fitting_people': len(fitting_users),
        'rating_counts': {str(key): value for key, value in sorted(Counter(row['rating'] for row in records).items())},
        'positive_pairs': matrix.nnz, 'people_with_positive': len(users),
        'people_with_one_positive': int(np.sum(lengths == 1)),
        'people_with_at_least_two': int(np.sum(lengths >= 2)),
        'people_with_at_least_five': int(np.sum(lengths >= 5)),
        'people_with_at_least_ten': int(np.sum(lengths >= 10)),
        'positive_history_quantiles_0_50_90_99_100': np.quantile(lengths, [0, .5, .9, .99, 1]).tolist(),
        'recipes_with_positive': int(np.count_nonzero(matrix.getnnz(axis=0))),
        'co_like_recipe_components': components, 'largest_recipe_component': int(np.bincount(labels).max()),
        'validation_users_absent_from_fit': True}
    return matrix, stats


def prepare():
    _, catalog, profiles, _, _ = inputs()
    _, stats = training_matrix(catalog, profiles)
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'protocol.json').exists():
        configuration = load_configuration()
        if configuration['training_data'] != stats:
            raise ValueError('Fitting data statistics changed')
        print('Existing registered ML 03 protocol verified, not overwritten.')
        return
    configuration = {'experiment': 'ml03-implicit-als-v1', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'baseline_hashes': preserved_hashes(), 'ml02_protocol_sha256': sha256(CONTENT / 'protocol.json'),
        'histories_sha256': sha256(CONTENT / 'histories.json'),
        'protocol_document_sha256': sha256(ROOT / 'docs/ML_03_PROTOCOL.md'),
        'implementation_sha256': code_hashes(), 'parameters': PARAMETERS, 'hybrid_cf_weights': WEIGHTS,
        'training_data': stats, 'cases': CASES, 'test_scored': False}
    dump(OUT / 'protocol.json', configuration)
    print(json.dumps(stats, indent=2))
    print('Registered before fitting/scoring. Test remains reserved.')


def load_configuration():
    configuration = json.loads((OUT / 'protocol.json').read_text(encoding='utf-8'))
    if (configuration['experiment'] != 'ml03-implicit-als-v1'
            or configuration['baseline_hashes'] != preserved_hashes()
            or configuration['ml02_protocol_sha256'] != sha256(CONTENT / 'protocol.json')
            or configuration['histories_sha256'] != sha256(CONTENT / 'histories.json')
            or configuration['protocol_document_sha256'] != sha256(ROOT / 'docs/ML_03_PROTOCOL.md')
            or configuration['implementation_sha256'] != code_hashes()
            or configuration['parameters'] != PARAMETERS
            or configuration['hybrid_cf_weights'] != list(WEIGHTS)
            or configuration['cases'] != list(CASES)):
        raise ValueError('Registered ML 03 inputs/code/choices changed; do not mix runs')
    return configuration


def train():
    configuration = load_configuration()
    _, catalog, profiles, _, _ = inputs()
    if (OUT / 'model.json').exists():
        load_model(configuration, catalog)
        print('Saved trained factors verified, not overwritten.')
        return
    matrix, stats = training_matrix(catalog, profiles)
    if configuration['training_data'] != stats:
        raise ValueError('Fitting matrix no longer matches registration')
    started = time.perf_counter()
    def progress(step, loss):
        print(f'ALS iteration {step}/12: objective {loss:.6f}; elapsed {time.perf_counter() - started:.1f}s', flush=True)
    model = fit(matrix, **PARAMETERS, progress=progress)
    np.save(OUT / 'items.npy', model.items, allow_pickle=False)
    np.save(OUT / 'users.npy', model.users, allow_pickle=False)
    receipt = {'parameters': PARAMETERS, 'objective_trace': model.objectives,
        'factor_sha256': {name: sha256(OUT / name) for name in ('items.npy', 'users.npy')},
        'protocol_sha256': sha256(OUT / 'protocol.json'), 'catalog_sha256': configuration['baseline_hashes']['catalog.json'],
        'training_seconds': time.perf_counter() - started, 'blas_threads': 1, 'device': 'cpu',
        'packages': {name: version(name) for name in ('numpy', 'scipy', 'pyarrow', 'threadpoolctl')},
        'trained_by_tasteprint': True, 'text_encoder_fine_tuned': False}
    dump(OUT / 'model.json', receipt)
    load_model(configuration, catalog)
    print(json.dumps(receipt, indent=2))


def load_model(configuration, catalog):
    receipt = json.loads((OUT / 'model.json').read_text(encoding='utf-8'))
    if (receipt['parameters'] != PARAMETERS or receipt['protocol_sha256'] != sha256(OUT / 'protocol.json')
            or receipt['catalog_sha256'] != configuration['baseline_hashes']['catalog.json']
            or any(sha256(OUT / name) != expected for name, expected in receipt['factor_sha256'].items())):
        raise ValueError('Trained model provenance changed')
    items = np.load(OUT / 'items.npy', allow_pickle=False)
    users = np.load(OUT / 'users.npy', allow_pickle=False)
    if (items.shape != (len(catalog), PARAMETERS['dimensions'])
            or users.shape != (configuration['training_data']['people_with_positive'], PARAMETERS['dimensions'])
            or not np.isfinite(items).all() or not np.isfinite(users).all()
            or len(receipt['objective_trace']) != PARAMETERS['iterations'] + 1
            or not np.isfinite(receipt['objective_trace']).all()
            or np.any(np.diff(receipt['objective_trace']) > 1e-6)):
        raise ValueError('Trained factors or convergence trace are invalid')
    return items, receipt


def matrices(catalog, profiles, embeddings, items):
    ids = np.asarray([row['id'] for row in catalog])
    index = {int(recipe_id): i for i, recipe_id in enumerate(ids)}
    seeds = [[index[recipe_id] for recipe_id in profile['likes']] for profile in profiles]
    with threadpool_limits(limits=1):
        content = profile_scores(embeddings, np.asarray(seeds), 'centroid')
        new_users = fold_in(items, seeds, alpha=PARAMETERS['alpha'], regularization=PARAMETERS['regularization'])
        cf = new_users @ items.T
    scores = {'popularity': np.broadcast_to(np.asarray([row['training_like_count'] for row in catalog]), cf.shape),
        'full/centroid': content, 'collaborative': cf}
    for weight in WEIGHTS:
        scores[f'hybrid/cf_{weight:.2f}'] = np.stack([blend_scores(c, f, weight, ~np.isin(ids, p['seen']))
            for c, f, p in zip(content, cf, profiles)])
    scores['shuffled_collaborative'] = cf[shuffled_profile_indices(len(profiles), SEED)]
    return scores


def evaluate():
    configuration = load_configuration()
    _, catalog, profiles, embeddings, histories = inputs()
    items, receipt = load_model(configuration, catalog)
    scores = matrices(catalog, profiles, embeddings, items)
    results = {name: measure(values, catalog, profiles, histories) for name, values in scores.items()}
    original = json.loads((BASE / 'validation-results.json').read_text(encoding='utf-8'))
    for old, new in [('popularity', 'popularity'), ('semantic', 'full/centroid')]:
        for key, value in original['metrics'][old].items():
            if not np.isclose(results[new]['metrics'][key], value, atol=1e-12, rtol=0):
                raise ValueError(f'Frozen comparator does not reproduce: {new}/{key}')
    contrasts = {reference: {name: comparison_interval(results[reference]['ndcg_per_person'], result['ndcg_per_person'])
        for name, result in results.items() if name != reference} for reference in ('popularity', 'collaborative')}
    by_id = {row['id']: row for row in catalog}
    cases = []
    for person in CASES:
        profile = profiles[person]
        future = {row['recipe_id']: row['rating'] for row in histories[person]['future']}
        cases.append({'profile_index': person, 'seed_names': [by_id[i]['name'] for i in profile['likes']],
            'seed_recipe_ids': profile['likes'], 'methods': {name: [{'id': i, 'name': by_id[i]['name'],
                'known_later_rating': future.get(i), 'source': f'https://www.food.com/recipe/{i}'}
                for i in result['top_recipe_ids'][person][:5]] for name, result in results.items() if name != 'shuffled_collaborative'}})
    dump(OUT / 'cases.json', cases)
    output = {'experiment': configuration['experiment'], 'profiles': len(profiles), 'candidates': len(catalog),
        'test_scored': False, 'training': configuration['training_data'], 'model': receipt,
        'metrics_and_diagnostics': {name: {key: value for key, value in result.items() if key not in ('ndcg_per_person', 'top_recipe_ids')}
            for name, result in results.items()}, 'paired_ndcg_comparisons': contrasts,
        'original_metrics_reproduced': True, 'baseline_hashes_unchanged': preserved_hashes() == configuration['baseline_hashes'],
        'protocol_sha256': sha256(OUT / 'protocol.json'), 'cases_sha256': sha256(OUT / 'cases.json'),
        'implementation_sha256': configuration['implementation_sha256'],
        'limitations': ['One training configuration/seed; validation-only hybrid comparison, not final-test confirmation.',
            'Unobserved pairs have low-confidence zero targets, not verified dislike labels.',
            'Review history is positive-heavy, sparse and exposure-biased; latent factors need not mean human taste concepts.',
            'Most recommendations lack personal rating evidence. Exact-ID recovery is not full enjoyment assessment.',
            'Inference uses six earlier candidate likes; this is not yet the frontend onboarding distribution.']}
    if not output['baseline_hashes_unchanged']:
        raise ValueError('Original baseline was modified')
    dump(OUT / 'results.json', output)
    for name, result in results.items():
        print(name, json.dumps(result['metrics']), flush=True)
    print('CF minus popularity:', json.dumps(contrasts['popularity']['collaborative']), flush=True)
    print('Correct CF minus shuffled:', json.dumps(comparison_interval(results['shuffled_collaborative']['ndcg_per_person'], results['collaborative']['ndcg_per_person'])))


def recommend(likes, k, demo_only):
    configuration = load_configuration()
    _, catalog, _, embeddings, _ = inputs()
    items, _ = load_model(configuration, catalog)
    mapping = json.loads((BASE / 'demo-id-map.json').read_text(encoding='utf-8'))
    ids = np.asarray([row['id'] for row in catalog])
    index = {int(value): i for i, value in enumerate(ids)}
    seed_ids = [int(value.strip().removeprefix('foodcom:')) for value in likes.split(',') if value.strip()]
    seed_ids = list(dict.fromkeys(mapping.get(str(value), value) for value in seed_ids))
    if any(value not in index for value in seed_ids):
        raise ValueError('A liked recipe is outside the trained catalog; content fallback is not implemented here')
    with threadpool_limits(limits=1):
        user = fold_in(items, [[index[value] for value in seed_ids]], alpha=PARAMETERS['alpha'], regularization=PARAMETERS['regularization'])[0]
        scores = items @ user
    excluded = set(seed_ids)
    if demo_only:
        excluded.update(set(ids) - set(mapping.values()))
    by_id = {row['id']: row for row in catalog}
    ranked = rank(scores, ids, excluded, k)
    print(json.dumps({'method': 'collaborative only, trained from fitting-user likes',
        'candidate_scope': '30 approved display recipes' if demo_only else '5006 experimental recipes',
        'likes': [{'id': value, 'name': by_id[value]['name']} for value in seed_ids],
        'recommendations': [{'id': int(ids[i]), 'name': by_id[int(ids[i])]['name'],
            'ranking_score_not_probability': float(scores[i]), 'source': f'https://www.food.com/recipe/{ids[i]}'} for i in ranked]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('prepare', 'train', 'evaluate'):
        commands.add_parser(command)
    preview = commands.add_parser('recommend')
    preview.add_argument('--likes', required=True)
    preview.add_argument('--k', type=int, default=10)
    preview.add_argument('--demo-only', action='store_true')
    args = parser.parse_args()
    if args.command == 'recommend':
        recommend(args.likes, args.k, args.demo_only)
    else:
        {'prepare': prepare, 'train': train, 'evaluate': evaluate}[args.command]()


if __name__ == '__main__':
    main()
