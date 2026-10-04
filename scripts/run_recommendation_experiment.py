"""Encode, evaluate validation, or try a Tasteprint profile. No neural training."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import time

import numpy as np

from download_foodcom import sha256
from prepare_recommendation_data import OUT, PROTOCOL, dump
from recommendation import recommend, rank, ranking_metrics, liked_profile

MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
REVISION = '1110a243fdf4706b3f48f1d95db1a4f5529b4d41'


def load_protocol():
    protocol = json.loads((OUT / 'protocol.json').read_text(encoding='utf-8'))
    if protocol['protocol'] != PROTOCOL:
        raise ValueError('Unexpected experiment protocol')
    for name, expected_hash in protocol['artifacts'].items():
        if sha256(OUT / name) != expected_hash:
            raise ValueError(f'Frozen artifact changed: {name}')
    catalog = json.loads((OUT / 'catalog.json').read_text(encoding='utf-8'))
    return protocol, catalog


def load_embeddings(protocol, catalog):
    metadata = json.loads((OUT / 'embeddings.json').read_text(encoding='utf-8'))
    if (metadata['model'] != MODEL or metadata['revision'] != REVISION
            or metadata['catalog_sha256'] != protocol['artifacts']['catalog.json']
            or metadata['vectors_sha256'] != sha256(OUT / 'embeddings.npy')):
        raise ValueError('Embedding provenance differs from the frozen experiment')
    embeddings = np.load(OUT / 'embeddings.npy', allow_pickle=False)
    if (embeddings.shape != (len(catalog), 384) or not np.isfinite(embeddings).all()
            or not np.allclose(np.linalg.norm(embeddings, axis=1), 1, atol=1e-5)):
        raise ValueError('Embeddings must be aligned, finite, normalized 384-dimensional vectors')
    return embeddings, metadata


def encode(protocol, catalog, allow_download):
    if (OUT / 'embeddings.json').exists():
        load_embeddings(protocol, catalog)
        print('Verified existing frozen embeddings; not overwritten.')
        return
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(4)
    torch.manual_seed(protocol['seed'])
    started = time.perf_counter()
    model = SentenceTransformer(MODEL, revision=REVISION, device='cpu',
        cache_folder=str(OUT / 'model-cache'), token=False,
        local_files_only=not allow_download, trust_remote_code=False,
        model_kwargs={'use_safetensors': True})
    texts = [row['text'] for row in catalog]
    token_lengths = [len(model.tokenizer.encode(text, truncation=False)) for text in texts]
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)
    if embeddings.shape != (len(catalog), 384) or not np.isfinite(embeddings).all():
        raise ValueError('Unexpected encoder output')
    np.save(OUT / 'embeddings.npy', embeddings, allow_pickle=False)
    metadata = {'model': MODEL, 'revision': REVISION,
        'model_card': f'https://huggingface.co/{MODEL}/tree/{REVISION}',
        'license': 'Apache-2.0 (model card)', 'fine_tuned_by_tasteprint': False,
        'device': 'cpu', 'threads': 4, 'batch_size': 32,
        'max_sequence_length': model.max_seq_length,
        'recipes_over_token_limit': sum(length > model.max_seq_length for length in token_lengths),
        'maximum_input_tokens': max(token_lengths), 'dimensions': 384,
        'profile': 'normalized mean of unique explicitly liked normalized recipe vectors',
        'catalog_sha256': protocol['artifacts']['catalog.json'],
        'vectors_sha256': sha256(OUT / 'embeddings.npy'),
        'packages': {name: version(name) for name in ('numpy', 'torch', 'sentence-transformers', 'transformers', 'pyarrow')},
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'encoding_seconds': time.perf_counter() - started}
    dump(OUT / 'embeddings.json', metadata)
    load_embeddings(protocol, catalog)
    print(json.dumps(metadata, indent=2))


def evaluate(protocol, catalog):
    embeddings, metadata = load_embeddings(protocol, catalog)
    profiles = json.loads((OUT / 'validation.json').read_text(encoding='utf-8'))
    if not profiles:
        raise ValueError('No eligible validation profiles; do not report empty metrics')
    ids = np.asarray([row['id'] for row in catalog])
    index = {int(recipe_id): i for i, recipe_id in enumerate(ids)}
    popularity = np.asarray([row['training_like_count'] for row in catalog], dtype=float)
    # Score profiles together rather than dispatching hundreds of tiny BLAS jobs.
    user_vectors = np.stack([liked_profile(embeddings, [index[recipe_id] for recipe_id in profile['likes']]) for profile in profiles])
    all_scores = user_vectors @ embeddings.T
    totals = {'popularity': [], 'semantic': []}
    paired = []
    recommendation_sets = {'popularity': set(), 'semantic': set()}
    started = time.perf_counter()
    for user_scores, profile in zip(all_scores, profiles):
        if set(profile['seen']) & set(profile['relevant']):
            raise ValueError('Seen recipes leaked into held-out positives')
        metrics = {}
        for name, scores in [('popularity', popularity), ('semantic', user_scores)]:
            ranked_ids = [int(ids[i]) for i in rank(scores, ids, profile['seen'], 10)]
            recommendation_sets[name].update(ranked_ids)
            metrics[name] = ranking_metrics(ranked_ids, profile['relevant'], 10)
            totals[name].append(metrics[name])
        paired.append(metrics['semantic']['ndcg'] - metrics['popularity']['ndcg'])
    results = {}
    for name, rows in totals.items():
        results[name] = {key + '@10': float(np.mean([row[key] for row in rows])) for key in rows[0]}
        results[name]['catalog_coverage@10'] = len(recommendation_sets[name]) / len(catalog)
    # Paired resampling quantifies validation sample variability, not model calibration.
    differences = np.asarray(paired)
    rng = np.random.default_rng(protocol['seed'])
    boot = differences[rng.integers(0, len(profiles), size=(2000, len(profiles)))].mean(axis=1)
    output = {'protocol': PROTOCOL, 'split': 'validation', 'test_scored': False,
        'profiles': len(profiles), 'candidate_recipes': len(catalog),
        'mean_heldout_likes': float(np.mean([len(profile['relevant']) for profile in profiles])),
        'model': MODEL, 'model_revision': REVISION,
        'metrics': results, 'semantic_minus_popularity_ndcg@10': float(differences.mean()),
        'paired_bootstrap_95_percent_interval': [float(x) for x in np.quantile(boot, [.025, .975])],
        'validation_users_semantic_better_ndcg': int(np.sum(differences > 0)),
        'validation_users_popularity_better_ndcg': int(np.sum(differences < 0)),
        'validation_users_tied_ndcg': int(np.sum(differences == 0)),
        'ranking_loop_seconds': time.perf_counter() - started,
        'artifacts': protocol['artifacts'], 'embedding_sha256': metadata['vectors_sha256'],
        'implementation_sha256': {name: sha256(Path(__file__).parent / name) for name in
            ('recommendation.py', 'prepare_recommendation_data.py', 'run_recommendation_experiment.py')},
        'limitations': protocol['limitations']}
    dump(OUT / 'validation-results.json', output)
    print(json.dumps(output, indent=2))


def try_profile(protocol, catalog, likes, k, demo_only):
    embeddings, _ = load_embeddings(protocol, catalog)
    mapping = json.loads((OUT / 'demo-id-map.json').read_text(encoding='utf-8'))
    likes = [int(value.strip().removeprefix('foodcom:')) for value in likes.split(',') if value.strip()]
    likes = [mapping.get(str(recipe_id), recipe_id) for recipe_id in likes]
    by_id = {row['id']: row for row in catalog}
    ids = [row['id'] for row in catalog]
    excluded = set(ids) - set(mapping.values()) if demo_only else set()
    rows = recommend(embeddings, ids, likes, seen_ids=excluded, k=k)
    output = {'method': 'semantic content only; not the hybrid',
        'candidate_scope': '30 approved display recipes' if demo_only else 'full ML 01 experiment catalog',
        'likes': [{'id': recipe_id, 'name': by_id[recipe_id]['name']} for recipe_id in dict.fromkeys(likes)],
        'recommendations': [{'id': recipe_id, 'name': by_id[recipe_id]['name'],
            'cosine_similarity_not_probability': score,
            'ingredients': by_id[recipe_id]['ingredients'],
            'source': f'https://www.food.com/recipe/{recipe_id}'} for recipe_id, score in rows]}
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    encoder = commands.add_parser('encode')
    encoder.add_argument('--download-model', action='store_true', help='Explicitly allow public model download; otherwise use local cache only')
    commands.add_parser('evaluate', help='Validation only. Test remains reserved for a later agreed final evaluation.')
    recommender = commands.add_parser('recommend')
    recommender.add_argument('--likes', required=True, help='Comma-separated numeric or foodcom: source IDs')
    recommender.add_argument('--k', type=int, default=10)
    recommender.add_argument('--demo-only', action='store_true', help='Rank only the 30 manually approved display recipes')
    args = parser.parse_args()
    protocol, catalog = load_protocol()
    if args.command == 'encode':
        encode(protocol, catalog, args.download_model)
    elif args.command == 'evaluate':
        evaluate(protocol, catalog)
    else:
        try_profile(protocol, catalog, args.likes, args.k, args.demo_only)


if __name__ == '__main__':
    main()
