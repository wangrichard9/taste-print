"""ML 04 registered approach-selection comparison. Validation only, never test."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import time

import numpy as np
from scipy.sparse import load_npz, save_npz
from threadpoolctl import threadpool_limits

from co_like import fit_relationships, score_likes
from collaborative import fit, fold_in
from content_ablation import shuffled_profile_indices
from download_foodcom import sha256
from prepare_recommendation_data import ROOT, SEED, dump
from run_collaborative_experiment import inputs, training_matrix, load_configuration as original_configuration, load_model as original_model, matrices as original_matrices
from run_content_ablation import measure, comparison_interval, CASES

OUT = ROOT / 'data/processed/ml04'
FITS = {'cf/a5_r1': {'alpha': 5.0, 'regularization': 1.0},
        'cf/a20_r10': {'alpha': 20.0, 'regularization': 10.0},
        'cf/a5_r10': {'alpha': 5.0, 'regularization': 10.0}}
DIRECT = ('raw', 'cosine_shrunk')
SHRINKAGE = 10.0
CODE = ('co_like.py', 'run_behavior_comparison.py', 'collaborative.py', 'run_collaborative_experiment.py',
        'run_content_ablation.py', 'content_ablation.py', 'recommendation.py')


def old_hashes():
    return {f'{folder}/{path.name}': sha256(path) for folder in ('ml01', 'ml02', 'ml03')
            for path in sorted((ROOT / 'data/processed' / folder).iterdir()) if path.is_file()}


def code_hashes():
    return {name: sha256(Path(__file__).parent / name) for name in CODE}


def stem(name):
    return name.replace('/', '_')


def parameters(name):
    return {**FITS[name], 'dimensions': 32, 'iterations': 12, 'seed': SEED}


def prepare():
    _, catalog, profiles, _, _ = inputs()
    original_model(original_configuration(), catalog)
    _, stats = training_matrix(catalog, profiles)
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'protocol.json').exists():
        load_configuration()
        print('Existing ML 04 registration verified, not overwritten.')
        return
    configuration = {'experiment': 'ml04-behavior-selection-v1', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'old_artifact_sha256': old_hashes(), 'implementation_sha256': code_hashes(),
        'protocol_document_sha256': sha256(ROOT / 'docs/ML_04_PROTOCOL.md'),
        'new_als': {name: parameters(name) for name in FITS}, 'direct_modes': DIRECT,
        'shrinkage': SHRINKAGE, 'training_data': stats, 'cases': CASES, 'test_scored': False}
    dump(OUT / 'protocol.json', configuration)
    print('Registered two direct methods and three additional CF configurations before fitting/scoring.')


def load_configuration():
    configuration = json.loads((OUT / 'protocol.json').read_text(encoding='utf-8'))
    if (configuration['experiment'] != 'ml04-behavior-selection-v1'
            or configuration['old_artifact_sha256'] != old_hashes()
            or configuration['implementation_sha256'] != code_hashes()
            or configuration['protocol_document_sha256'] != sha256(ROOT / 'docs/ML_04_PROTOCOL.md')
            or configuration['new_als'] != {name: parameters(name) for name in FITS}
            or configuration['direct_modes'] != list(DIRECT) or configuration['shrinkage'] != SHRINKAGE
            or configuration['cases'] != list(CASES)):
        raise ValueError('Frozen ML 04 inputs/code/choices changed; do not mix experiments')
    return configuration


def train():
    configuration = load_configuration()
    _, catalog, profiles, _, _ = inputs()
    if (OUT / 'models.json').exists():
        load_models(configuration, catalog)
        print('Saved ML 04 fitted models verified, not overwritten.')
        return
    positive, stats = training_matrix(catalog, profiles)
    if stats != configuration['training_data']:
        raise ValueError('Fitting matrix differs from registration')
    receipt = {'protocol_sha256': sha256(OUT / 'protocol.json'), 'models': {},
        'packages': {name: version(name) for name in ('numpy', 'scipy', 'pyarrow', 'threadpoolctl')},
        'test_scored': False}
    for mode in DIRECT:
        started = time.perf_counter()
        name = f'direct/{mode}'
        relationships = fit_relationships(positive, mode, SHRINKAGE)
        file = stem(name) + '.npz'
        save_npz(OUT / file, relationships)
        receipt['models'][name] = {'artifact_sha256': {file: sha256(OUT / file)},
            'fitting_seconds': time.perf_counter() - started, 'nonzero_relationships': relationships.nnz,
            'mode': mode, 'shrinkage': SHRINKAGE if mode != 'raw' else None}
        print(f'{name}: {relationships.nnz} relationships; {time.perf_counter() - started:.1f}s', flush=True)
        del relationships
    for name in FITS:
        started = time.perf_counter()
        def progress(step, loss):
            print(f'{name}: ALS {step}/12, objective {loss:.6f}, {time.perf_counter() - started:.1f}s', flush=True)
        model = fit(positive, **parameters(name), progress=progress)
        hashes = {}
        for kind, factors in [('items', model.items), ('users', model.users)]:
            file = stem(name) + '_' + kind + '.npy'
            np.save(OUT / file, factors, allow_pickle=False)
            hashes[file] = sha256(OUT / file)
        receipt['models'][name] = {'artifact_sha256': hashes, 'parameters': parameters(name),
            'objective_trace': model.objectives, 'fitting_seconds': time.perf_counter() - started,
            'trained_by_tasteprint': True, 'blas_threads': 1}
        del model
    dump(OUT / 'models.json', receipt)
    load_models(configuration, catalog)


def load_models(configuration, catalog):
    receipt = json.loads((OUT / 'models.json').read_text(encoding='utf-8'))
    expected_names = {f'direct/{mode}' for mode in DIRECT} | set(FITS)
    if (receipt['protocol_sha256'] != sha256(OUT / 'protocol.json') or set(receipt['models']) != expected_names
            or receipt['test_scored']):
        raise ValueError('Model receipt differs from registration')
    loaded = {}
    for name, model in receipt['models'].items():
        if any(sha256(OUT / file) != expected for file, expected in model['artifact_sha256'].items()):
            raise ValueError('Saved ML 04 fitting artifact changed')
        if name.startswith('direct/'):
            weights = load_npz(OUT / (stem(name) + '.npz'))
            if (weights.shape != (len(catalog), len(catalog)) or not np.isfinite(weights.data).all()
                    or (weights.data < 0).any() or weights.diagonal().any()):
                raise ValueError('Invalid aligned direct relationships')
            loaded[name] = weights
        else:
            items = np.load(OUT / (stem(name) + '_items.npy'), allow_pickle=False)
            users = np.load(OUT / (stem(name) + '_users.npy'), allow_pickle=False, mmap_mode='r')
            trace = np.asarray(model['objective_trace'])
            if (model['parameters'] != parameters(name) or items.shape != (len(catalog), 32)
                    or users.shape != (configuration['training_data']['people_with_positive'], 32)
                    or not np.isfinite(items).all() or not np.isfinite(users).all()
                    or len(trace) != 13 or not np.isfinite(trace).all() or (np.diff(trace) > 1e-6).any()):
                raise ValueError('Invalid aligned factors/convergence')
            loaded[name] = items
    return loaded, receipt


def score_models(catalog, profiles, embeddings, loaded):
    original, _ = original_model(original_configuration(), catalog)
    baseline = original_matrices(catalog, profiles, embeddings, original)
    scores = {'popularity': baseline['popularity'], 'full/centroid': baseline['full/centroid'],
        'cf/a20_r1': baseline['collaborative']}
    index = {row['id']: i for i, row in enumerate(catalog)}
    seeds = [[index[recipe_id] for recipe_id in profile['likes']] for profile in profiles]
    with threadpool_limits(limits=1):
        for name, fitted in loaded.items():
            if name.startswith('direct/'):
                scores[name] = score_likes(fitted, seeds)
            else:
                users = fold_in(fitted, seeds, **FITS[name])
                scores[name] = users @ fitted.T
    return scores


def evaluate():
    configuration = load_configuration()
    _, catalog, profiles, embeddings, histories = inputs()
    loaded, receipt = load_models(configuration, catalog)
    scores = score_models(catalog, profiles, embeddings, loaded)
    results = {name: measure(values, catalog, profiles, histories) for name, values in scores.items()}
    old = json.loads((ROOT / 'data/processed/ml03/results.json').read_text(encoding='utf-8'))
    for name, previous in [('popularity', 'popularity'), ('full/centroid', 'full/centroid'), ('cf/a20_r1', 'collaborative')]:
        if results[name]['metrics'] != old['metrics_and_diagnostics'][previous]['metrics']:
            raise ValueError('Original metrics did not reproduce exactly')
    behavioral = [name for name in scores if name not in ('popularity', 'full/centroid')]
    shuffled = shuffled_profile_indices(len(profiles), SEED)
    controls = {name: measure(scores[name][shuffled], catalog, profiles, histories) for name in behavioral}
    contrasts = {reference: {name: comparison_interval(results[reference]['ndcg_per_person'], result['ndcg_per_person'])
        for name, result in results.items() if name != reference} for reference in ('popularity', 'cf/a20_r1')}
    personal = {name: comparison_interval(controls[name]['ndcg_per_person'], results[name]['ndcg_per_person']) for name in behavioral}
    best_value = max(results[name]['metrics']['ndcg@10'] for name in behavioral)
    nominee = sorted(name for name in behavioral if abs(results[name]['metrics']['ndcg@10'] - best_value) <= 1e-12)[0]
    top100 = {row['id'] for row in sorted(catalog, key=lambda row: (-row['training_like_count'], row['id']))[:100]}
    by_id = {row['id']: row for row in catalog}
    index = {row['id']: i for i, row in enumerate(catalog)}
    positive, _ = training_matrix(catalog, profiles)
    counts = np.asarray(positive.sum(axis=0)).ravel()
    raw = loaded['direct/raw']
    cases = []
    for person in CASES:
        profile = profiles[person]
        future = {row['recipe_id']: row['rating'] for row in histories[person]['future']}
        entries = {}
        for name, result in results.items():
            rows = []
            for recipe_id in result['top_recipe_ids'][person][:5]:
                row = {'id': recipe_id, 'name': by_id[recipe_id]['name'], 'known_later_rating': future.get(recipe_id)}
                if name.startswith('direct/'):
                    target = index[recipe_id]
                    row['co_like_evidence'] = [{'seed_name': by_id[seed]['name'],
                        'shared_fitting_likers': int(raw[index[seed], target]),
                        'seed_positive_count': int(counts[index[seed]]), 'target_positive_count': int(counts[target]),
                        'relationship_weight': float(loaded[name][index[seed], target])} for seed in profile['likes']]
                rows.append(row)
            entries[name] = rows
        cases.append({'profile_index': person, 'seed_names': [by_id[seed]['name'] for seed in profile['likes']], 'methods': entries})
    dump(OUT / 'cases.json', cases)
    dump(OUT / 'rankings.json', {name: {'ndcg_per_person': result['ndcg_per_person'], 'top_recipe_ids': result['top_recipe_ids']}
        for name, result in results.items()})
    def aggregate(result):
        return {key: value for key, value in result.items() if key not in ('ndcg_per_person', 'top_recipe_ids')}
    output = {'experiment': configuration['experiment'], 'profiles': len(profiles), 'candidates': len(catalog),
        'test_scored': False, 'original_metrics_reproduced': True,
        'old_artifacts_unchanged': old_hashes() == configuration['old_artifact_sha256'],
        'training': configuration['training_data'], 'fitting_receipt': receipt,
        'metrics_and_diagnostics': {name: aggregate(result) for name, result in results.items()},
        'shuffled_controls': {name: aggregate(result) for name, result in controls.items()},
        'correct_minus_shuffled_ndcg': personal, 'paired_ndcg_comparisons': contrasts,
        'fitting_top100_recommendation_share': {name: sum(i in top100 for ids in result['top_recipe_ids'] for i in ids) / (len(profiles) * 10)
            for name, result in results.items()}, 'provisional_behavioral_nominee': nominee,
        'protocol_sha256': sha256(OUT / 'protocol.json'), 'implementation_sha256': configuration['implementation_sha256'],
        'cases_sha256': sha256(OUT / 'cases.json'), 'rankings_sha256': sha256(OUT / 'rankings.json'),
        'limitations': ['Repeated validation use and selection among methods; no independent final-test claim.',
            'Bootstrap intervals do not correct multiple comparisons or training-seed variation.',
            'Unrated suggestions are unknown; co-like normalization is not causal removal of exposure/popularity.',
            'The 30-dish frontend and six-choice onboarding distribution are not validated by this experiment.']}
    if not output['old_artifacts_unchanged']:
        raise ValueError('Prior experiments changed')
    dump(OUT / 'results.json', output)
    for name, result in results.items():
        print(name, json.dumps(result['metrics']), flush=True)
        if name in personal:
            print('  correct minus shuffled:', json.dumps(personal[name]), flush=True)
    print('Provisional nominee:', nominee)
    print('Nominee minus popularity:', json.dumps(contrasts['popularity'][nominee]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'train', 'evaluate'))
    args = parser.parse_args()
    {'prepare': prepare, 'train': train, 'evaluate': evaluate}[args.command]()


if __name__ == '__main__':
    main()
