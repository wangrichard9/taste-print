"""Registered ML 02 content diagnosis; never scores the reserved test."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np
import pyarrow.parquet as pq

from audit_foodcom import canonical_id, has_text, usable_list
from content_ablation import ingredient_text, profile_scores, shuffled_profile_indices, score_auc, status_counts
from download_foodcom import sha256
from prepare_recommendation_data import ROOT, RAW, OUT as BASE, SEED, dump, make_profile, user_hash
from recommendation import clean_text, content_signature, rank, ranking_metrics
from run_recommendation_experiment import load_protocol, load_embeddings, MODEL, REVISION

OUT = ROOT / 'data/processed/ml02'
TEXTS = ('full', 'ingredients')
MODES = ('centroid', 'closest', 'top_two')
CASES = (0, 60, 120, 179, 239, 299)


def preserved_hashes():
    return {path.name: sha256(path) for path in sorted(BASE.iterdir()) if path.is_file()}


def load_frozen():
    configuration = json.loads((OUT / 'protocol.json').read_text(encoding='utf-8'))
    if configuration['baseline_hashes'] != preserved_hashes():
        raise ValueError('ML 01 input artifacts changed; stop instead of mixing experiments')
    if configuration['protocol_document_sha256'] != sha256(ROOT / 'docs/ML_02_PROTOCOL.md'):
        raise ValueError('Registered ML 02 choices changed')
    protocol, catalog = load_protocol()
    profiles = json.loads((BASE / 'validation.json').read_text(encoding='utf-8'))
    if len(profiles) != 300 or len(catalog) != 5006:
        raise ValueError('Unexpected original evaluation population')
    text_hash = hashlib.sha256(json.dumps([ingredient_text(row) for row in catalog], ensure_ascii=False).encode()).hexdigest()
    if (configuration['text_modes'] != list(TEXTS) or configuration['profile_modes'] != list(MODES)
            or configuration['cases'] != list(CASES) or configuration['ingredient_text_sha256'] != text_hash):
        raise ValueError('Registered text/profile/case choices differ from the implementation')
    return configuration, protocol, catalog, profiles


def prepare():
    protocol, catalog = load_protocol()
    load_embeddings(protocol, catalog)
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'protocol.json').exists():
        load_frozen()
        print('Existing registered ML 02 inputs verified; not overwritten.')
        return
    configuration = {'experiment': 'ml02-content-grid-v1', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'seed': SEED, 'baseline_hashes': preserved_hashes(),
        'protocol_document_sha256': sha256(ROOT / 'docs/ML_02_PROTOCOL.md'),
        'model': MODEL, 'revision': REVISION, 'text_modes': TEXTS, 'profile_modes': MODES,
        'cases': CASES, 'bootstrap_resamples': 2000, 'test_scored': False,
        'criterion': 'Exploratory paired validation NDCG@10; not a final-test winner',
        'ingredient_text_sha256': hashlib.sha256(json.dumps([ingredient_text(row) for row in catalog], ensure_ascii=False).encode()).hexdigest()}
    dump(OUT / 'protocol.json', configuration)
    print('Registered six variants and diagnostics before computing variant scores.')


def encode():
    configuration, protocol, catalog, _ = load_frozen()
    full, _ = load_embeddings(protocol, catalog)
    if (OUT / 'ingredients.json').exists():
        ingredient_embeddings(configuration, catalog)
        print('Frozen ingredient embeddings verified; not overwritten.')
        return
    # Offline is deliberate: use the model already downloaded for ML 01, no tokens.
    os.environ['HF_HUB_OFFLINE'] = '1'
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(4)
    torch.manual_seed(SEED)
    started = time.perf_counter()
    model = SentenceTransformer(MODEL, revision=REVISION, device='cpu', token=False,
        cache_folder=str(BASE / 'model-cache'), local_files_only=True,
        trust_remote_code=False, model_kwargs={'use_safetensors': True})
    sample = np.sort(np.random.default_rng(SEED).choice(len(catalog), 8, replace=False))
    check = model.encode([catalog[i]['text'] for i in sample], batch_size=32,
                         normalize_embeddings=True, convert_to_numpy=True)
    differences = np.max(np.abs(check - full[sample]), axis=1)
    if not np.allclose(check, full[sample], atol=1e-5):
        raise ValueError('Re-encoded full source rows disagree with frozen vectors')
    texts = [ingredient_text(row) for row in catalog]
    lengths = [len(model.tokenizer.encode(text, truncation=False)) for text in texts]
    vectors = model.encode(texts, batch_size=32, show_progress_bar=True,
                          normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)
    np.save(OUT / 'ingredients.npy', vectors, allow_pickle=False)
    metadata = {'model': MODEL, 'revision': REVISION, 'text_sha256': configuration['ingredient_text_sha256'],
        'catalog_sha256': protocol['artifacts']['catalog.json'], 'vectors_sha256': sha256(OUT / 'ingredients.npy'),
        'max_sequence_length': model.max_seq_length, 'maximum_input_tokens': max(lengths),
        'truncated_recipes': sum(length > model.max_seq_length for length in lengths),
        'reencoded_full_recipe_ids': [catalog[i]['id'] for i in sample],
        'reencoded_max_absolute_differences': differences.tolist(), 'original_alignment_check_passed': True,
        'threads': 4, 'batch_size': 32, 'device': 'cpu', 'fine_tuned': False,
        'packages': {name: version(name) for name in ('numpy', 'torch', 'sentence-transformers', 'transformers', 'pyarrow')},
        'encoding_seconds': time.perf_counter() - started}
    dump(OUT / 'ingredients.json', metadata)
    ingredient_embeddings(configuration, catalog)
    print(json.dumps(metadata, indent=2))


def ingredient_embeddings(configuration, catalog):
    metadata = json.loads((OUT / 'ingredients.json').read_text(encoding='utf-8'))
    if (metadata['model'] != MODEL or metadata['revision'] != REVISION
            or metadata['text_sha256'] != configuration['ingredient_text_sha256']
            or metadata['catalog_sha256'] != configuration['baseline_hashes']['catalog.json']
            or metadata['vectors_sha256'] != sha256(OUT / 'ingredients.npy')):
        raise ValueError('Ingredient vector provenance changed')
    vectors = np.load(OUT / 'ingredients.npy', allow_pickle=False)
    if (vectors.shape != (len(catalog), 384) or not np.isfinite(vectors).all()
            or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)):
        raise ValueError('Ingredient vectors are not aligned, finite and normalized')
    return vectors


def reconstruct_histories(protocol, catalog, profiles):
    for receipt in protocol['source_manifest']['files']:
        path = RAW / receipt['name']
        if path.stat().st_size != receipt['bytes'] or sha256(path) != receipt['sha256']:
            raise ValueError('Raw data changed since ML 01')
    identities = {}
    representatives = {}
    for batch in pq.ParquetFile(RAW / 'recipes.parquet').iter_batches(batch_size=8192,
            columns=['RecipeId', 'Name', 'RecipeIngredientParts']):
        for row in batch.to_pylist():
            recipe_id = canonical_id(row['RecipeId'])
            if recipe_id is None or not has_text(row['Name']) or not usable_list(row['RecipeIngredientParts']):
                continue
            signature = content_signature({'name': clean_text(row['Name']),
                'ingredients': [clean_text(item) for item in row['RecipeIngredientParts']]})
            identities[recipe_id] = signature
            representatives[signature] = min(recipe_id, representatives.get(signature, recipe_id))
    canonical = {recipe_id: representatives[signature] for recipe_id, signature in identities.items()}
    del identities, representatives
    keys = {profile['user_key'] for profile in profiles}
    histories = {key: {} for key in keys}
    cache = {}
    fields = ['AuthorId', 'RecipeId', 'ReviewId', 'Rating', 'DateSubmitted']
    for batch in pq.ParquetFile(RAW / 'reviews.parquet').iter_batches(batch_size=32768, columns=fields):
        for row in batch.to_pylist():
            user_id = canonical_id(row['AuthorId'])
            if user_id is None:
                continue
            if user_id not in cache:
                hashed = user_hash(user_id)
                cache[user_id] = hashed if hashed in keys else None
            key = cache[user_id]
            if key is None:
                continue
            recipe_id = canonical_id(row['RecipeId'])
            review_id = canonical_id(row['ReviewId'])
            if recipe_id not in canonical or review_id is None or row['Rating'] not in (1, 2, 3, 4, 5) or row['DateSubmitted'] is None:
                continue
            recipe_id = canonical[recipe_id]
            record = {'recipe_id': recipe_id, 'rating': row['Rating'],
                'timestamp': row['DateSubmitted'].isoformat(), 'review_id': review_id}
            prior = histories[key].get(recipe_id)
            if prior is None or (record['timestamp'], review_id) < (prior['timestamp'], prior['review_id']):
                histories[key][recipe_id] = record
    ids = {row['id'] for row in catalog}
    extracted = []
    for profile in profiles:
        history = list(histories[profile['user_key']].values())
        rebuilt = make_profile([row for row in history if row['recipe_id'] in ids])
        expected = {name: profile[name] for name in ('likes', 'seen', 'relevant', 'seed_cutoff_utc')}
        if rebuilt != expected:
            raise ValueError('Raw history does not reproduce the frozen six-like profile')
        future = [row for row in history if row['timestamp'] > profile['seed_cutoff_utc']]
        future.sort(key=lambda row: (row['timestamp'], row['review_id']))
        extracted.append({'future': future, 'valid_history_rows': len(history)})
    print('Raw-history reconstruction matches all 300 frozen validation profiles.', flush=True)
    return extracted


def measure(scores, catalog, profiles, histories):
    ids = np.asarray([row['id'] for row in catalog])
    index = {int(recipe_id): i for i, recipe_id in enumerate(ids)}
    rows, top_ids, aucs = [], [], []
    statuses = Counter({'known_high': 0, 'known_lower': 0, 'unknown': 0})
    recommended = Counter()
    for user_scores, profile, history in zip(scores, profiles, histories):
        ranked = [int(ids[i]) for i in rank(user_scores, ids, profile['seen'], 10)]
        rows.append(ranking_metrics(ranked, profile['relevant'], 10))
        top_ids.append(ranked)
        recommended.update(ranked)
        future_ratings = {row['recipe_id']: row['rating'] for row in history['future'] if row['recipe_id'] in index}
        statuses.update(status_counts(ranked, future_ratings))
        high = [user_scores[index[recipe_id]] for recipe_id, rating in future_ratings.items() if rating >= 4]
        lower = [user_scores[index[recipe_id]] for recipe_id, rating in future_ratings.items() if rating <= 3]
        auc = score_auc(high, lower)
        if auc is not None:
            aucs.append(auc)
    metrics = {key + '@10': float(np.mean([row[key] for row in rows])) for key in rows[0]}
    metrics['catalog_coverage@10'] = len(recommended) / len(catalog)
    metrics['people_with_hit'] = int(sum(row['hit_rate'] for row in rows))
    return {'metrics': metrics, 'top10_rating_status': dict(statuses),
        'unique_recommended_recipes': len(recommended),
        'largest_single_recipe_recommendation_share': max(recommended.values()) / (len(profiles) * 10),
        'observed_rating_auc': {'people_with_high_and_lower': len(aucs),
            'macro_auc': float(np.mean(aucs)) if aucs else None},
        'ndcg_per_person': [row['ndcg'] for row in rows], 'top_recipe_ids': top_ids}


def comparison_interval(reference, alternative):
    differences = np.asarray(alternative) - np.asarray(reference)
    sample = np.random.default_rng(SEED).integers(0, len(differences), size=(2000, len(differences)))
    boot = differences[sample].mean(axis=1)
    return {'mean_ndcg_difference': float(differences.mean()),
        'paired_bootstrap_95_percent_interval': np.quantile(boot, [.025, .975]).tolist(),
        'better_people': int(np.sum(differences > 0)), 'worse_people': int(np.sum(differences < 0)),
        'tied_people': int(np.sum(differences == 0))}


def evaluate():
    configuration, protocol, catalog, profiles = load_frozen()
    full, full_metadata = load_embeddings(protocol, catalog)
    ingredients = ingredient_embeddings(configuration, catalog)
    history_path = OUT / 'histories.json'
    history_receipt = OUT / 'histories-manifest.json'
    if history_path.exists() and history_receipt.exists():
        receipt = json.loads(history_receipt.read_text(encoding='utf-8'))
        if receipt['sha256'] != sha256(history_path) or receipt['baseline_hashes'] != configuration['baseline_hashes']:
            raise ValueError('Diagnostic histories changed')
        histories = json.loads(history_path.read_text(encoding='utf-8'))
    else:
        histories = reconstruct_histories(protocol, catalog, profiles)
        dump(history_path, histories)
        dump(history_receipt, {'sha256': sha256(history_path), 'baseline_hashes': configuration['baseline_hashes']})
    ids = [row['id'] for row in catalog]
    index = {recipe_id: i for i, recipe_id in enumerate(ids)}
    seeds = np.asarray([[index[recipe_id] for recipe_id in profile['likes']] for profile in profiles])
    popularity = np.asarray([row['training_like_count'] for row in catalog], dtype=np.float32)
    results = {'popularity': measure(np.broadcast_to(popularity, (len(profiles), len(catalog))), catalog, profiles, histories)}
    matrices = {}
    for name, vectors in [('full', full), ('ingredients', ingredients)]:
        for mode in MODES:
            variant = f'{name}/{mode}'
            matrices[variant] = profile_scores(vectors, seeds, mode)
            results[variant] = measure(matrices[variant], catalog, profiles, histories)
    original = json.loads((BASE / 'validation-results.json').read_text(encoding='utf-8'))
    for old, new in [('popularity', 'popularity'), ('semantic', 'full/centroid')]:
        for metric, value in original['metrics'][old].items():
            if not np.isclose(value, results[new]['metrics'][metric], atol=1e-12, rtol=0):
                raise ValueError(f'Original result did not reproduce: {new} {metric}')
    shuffled = shuffled_profile_indices(len(profiles), SEED)
    results['shuffled_full/centroid'] = measure(matrices['full/centroid'][shuffled], catalog, profiles, histories)
    reference = results['full/centroid']['ndcg_per_person']
    contrasts = {variant: comparison_interval(reference, results[variant]['ndcg_per_person']) for variant in results if variant != 'full/centroid'}
    simple_effects = {}
    for mode in MODES:
        simple_effects[f'ingredients_minus_full/{mode}'] = comparison_interval(results[f'full/{mode}']['ndcg_per_person'], results[f'ingredients/{mode}']['ndcg_per_person'])
    ranked_pop = sorted(catalog, key=lambda row: (-row['training_like_count'], row['id']))
    head_ids = {row['id'] for row in ranked_pop[:100]}
    all_future_high = sum(row['rating'] >= 4 for history in histories for row in history['future'])
    candidate_future_high = sum(len(profile['relevant']) for profile in profiles)
    coverage_per_user = [len(profile['relevant']) / sum(row['rating'] >= 4 for row in history['future']) for profile, history in zip(profiles, histories)]
    target_head = sum(recipe_id in head_ids for profile in profiles for recipe_id in profile['relevant'])
    cases = []
    by_id = {row['id']: row for row in catalog}
    for person in CASES:
        profile = profiles[person]
        future = {row['recipe_id']: row['rating'] for row in histories[person]['future']}
        seed_rows = [by_id[recipe_id] for recipe_id in profile['likes']]
        case = {'profile_index': person, 'seed_names': [row['name'] for row in seed_rows],
            'seed_recipe_ids': profile['likes'], 'withheld_positive_count': len(profile['relevant']),
            'withheld_example_names': [by_id[recipe_id]['name'] for recipe_id in profile['relevant'][:5]],
            'methods': {}}
        for variant in ('popularity', 'full/centroid', 'full/closest', 'ingredients/centroid', 'ingredients/closest', 'ingredients/top_two'):
            entries = []
            for recipe_id in results[variant]['top_recipe_ids'][person][:5]:
                row = by_id[recipe_id]
                similarities = full[index[recipe_id]] @ full[seeds[person]].T
                best_seed = seed_rows[int(np.argmax(similarities))]
                shared = sorted({clean_text(x).casefold() for x in row['ingredients']} & {clean_text(x).casefold() for x in best_seed['ingredients']})
                rating = future.get(recipe_id)
                entries.append({'id': recipe_id, 'name': row['name'], 'known_later_rating': rating,
                    'status': 'unknown' if rating is None else 'known_high' if rating >= 4 else 'known_lower',
                    'closest_seed_by_original_text': best_seed['name'], 'shared_exact_ingredient_names': shared})
            case['methods'][variant] = entries
        cases.append(case)
    dump(OUT / 'cases.json', cases)
    # Detailed rankings remain local. Only aggregate evidence is published in docs.
    output = {'experiment': configuration['experiment'], 'profiles': len(profiles), 'candidates': len(catalog),
        'test_scored': False, 'original_metrics_reproduced': True,
        'baseline_hashes_unchanged': configuration['baseline_hashes'] == preserved_hashes(),
        'metrics_and_diagnostics': {name: {key: value for key, value in result.items() if key not in ('ndcg_per_person', 'top_recipe_ids')} for name, result in results.items()},
        'paired_changes_from_original_centroid': contrasts, 'ingredient_text_effect_at_fixed_profile': simple_effects,
        'source_history_check': {'all_300_profiles_reconstructed': True, 'future_high_records_all_content': all_future_high,
            'future_high_records_in_catalog': candidate_future_high, 'pooled_positive_candidate_coverage': candidate_future_high / all_future_high,
            'mean_person_positive_candidate_coverage': float(np.mean(coverage_per_user)),
            'withheld_high_records_in_training_top100': target_head, 'withheld_high_records_total': candidate_future_high,
            'withheld_high_top100_fraction': target_head / candidate_future_high},
        'encoder_alignment': json.loads((OUT / 'ingredients.json').read_text(encoding='utf-8')),
        'artifact_sha256': {'protocol': sha256(OUT / 'protocol.json'), 'histories': sha256(history_path),
            'cases': sha256(OUT / 'cases.json'), 'original_vectors': full_metadata['vectors_sha256']},
        'implementation_sha256': {name: sha256(Path(__file__).parent / name) for name in ('content_ablation.py', 'run_content_ablation.py')},
        'limitations': ['Validation-only exploratory comparisons; no multiple-comparison adjustment or final-test claims.',
            'Observed-rating AUC is on a restricted selected subset, not the all-candidate recommendation task.',
            'Unrated suggestions and semantic resemblance are not evidence of enjoyment.',
            'The experiments do not isolate every text field, prove a sole root cause, or establish that more data solves the gap.']}
    if not output['baseline_hashes_unchanged']:
        raise ValueError('ML 01 was changed during the experiment')
    dump(OUT / 'results.json', output)
    for name, result in results.items():
        print(name, json.dumps(result['metrics']), json.dumps(result['top10_rating_status']), flush=True)
    print(json.dumps(output['source_history_check'], indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'encode', 'evaluate'))
    args = parser.parse_args()
    {'prepare': prepare, 'encode': encode, 'evaluate': evaluate}[args.command]()


if __name__ == '__main__':
    main()
