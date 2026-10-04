"""Build an immutable, user-disjoint ML 01 protocol from the audited source."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from audit_foodcom import canonical_id, has_text, usable_list
from download_foodcom import sha256
from recommendation import content_signature, clean_text, recipe_text

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/foodcom-v2"
OUT = ROOT / "data/processed/ml01"
SEED = 20260930
PROTOCOL = "ml01-user-disjoint-six-likes-v1"


def user_hash(user_id):
    return hashlib.sha256(f"{SEED}:{user_id}".encode()).hexdigest()


def user_partition(user_id):
    bucket = int(user_hash(user_id), 16) % 100
    return "train" if bucket < 80 else "validation" if bucket < 90 else "test"


def make_profile(history, seed_count=6):
    """History is already restricted to the fixed candidate catalog."""
    history = sorted(history, key=lambda item: (item['timestamp'], item['review_id']))
    positives = [row for row in history if row['rating'] >= 4]
    if len(positives) <= seed_count:
        return None
    seeds = positives[:seed_count]
    cutoff = seeds[-1]['timestamp']
    # Same-time reviews cannot count as future evidence; exclude all known items.
    seen = sorted({row['recipe_id'] for row in history if row['timestamp'] <= cutoff})
    targets = sorted({row['recipe_id'] for row in positives if row['timestamp'] > cutoff} - set(seen))
    if not targets:
        return None
    return {"likes": [row['recipe_id'] for row in seeds], "seen": seen,
            "relevant": targets, "seed_cutoff_utc": cutoff}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog-size', type=int, default=5000)
    parser.add_argument('--max-eval-users', type=int, default=300)
    args = parser.parse_args()
    if args.catalog_size < 10 or args.max_eval_users < 1:
        parser.error('Positive evaluation size and catalog size >= 10 required')
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'protocol.json').exists():
        parser.error('Protocol already exists. Use its frozen artifacts; create a new experiment for changes.')
    manifest = json.loads((RAW / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['version'] != 2 or manifest['source'] != 'https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews':
        raise ValueError('Unexpected source provenance')
    for receipt in manifest['files']:
        path = RAW / receipt['name']
        if path.stat().st_size != receipt['bytes'] or sha256(path) != receipt['sha256']:
            raise ValueError(f"Source changed: {receipt['name']}")
    recipes = {}
    fields = ['RecipeId', 'Name', 'RecipeIngredientParts', 'RecipeCategory', 'Keywords']
    flags = Counter()
    for batch in pq.ParquetFile(RAW / 'recipes.parquet').iter_batches(columns=fields, batch_size=8192):
        for row in batch.to_pylist():
            recipe_id = canonical_id(row['RecipeId'])
            if recipe_id is None or not has_text(row['Name']) or not usable_list(row['RecipeIngredientParts']):
                flags['recipes_without_usable_content'] += 1
                continue
            recipes[recipe_id] = {'id': recipe_id, 'name': clean_text(row['Name']),
                'ingredients': [clean_text(x) for x in row['RecipeIngredientParts']],
                'category': clean_text(row['RecipeCategory']),
                'keywords': [clean_text(x) for x in (row['Keywords'] or []) if has_text(x)]}
    # Lowest source ID is the deterministic representative, independent of ratings.
    canonical = {}
    representatives = {}
    for recipe_id in sorted(recipes):
        signature = content_signature(recipes[recipe_id])
        representative = representatives.setdefault(signature, recipe_id)
        canonical[recipe_id] = representative
    flags['exact_content_duplicate_recipes'] = len(recipes) - len(representatives)
    print(f'Recipe content checked: {len(recipes):,}; exact duplicate identities: {flags["exact_content_duplicate_recipes"]:,}', flush=True)
    popularity = Counter()
    histories = {'validation': defaultdict(list), 'test': defaultdict(list)}
    train_rows = []
    # Collapse any source IDs mapped to the same content identity. Earliest valid
    # explicit rating wins; no average computed using future ratings.
    earliest = {}
    fields = ['ReviewId', 'RecipeId', 'AuthorId', 'Rating', 'DateSubmitted']
    for batch in pq.ParquetFile(RAW / 'reviews.parquet').iter_batches(columns=fields, batch_size=32768):
        for row in batch.to_pylist():
            recipe_id = canonical_id(row['RecipeId'])
            user_id = canonical_id(row['AuthorId'])
            review_id = canonical_id(row['ReviewId'])
            if recipe_id not in canonical or user_id is None or review_id is None or row['Rating'] not in (1, 2, 3, 4, 5) or row['DateSubmitted'] is None:
                flags['excluded_reviews'] += 1
                continue
            recipe_id = canonical[recipe_id]
            record = {'recipe_id': recipe_id, 'rating': row['Rating'],
                'timestamp': row['DateSubmitted'].isoformat(), 'review_id': review_id}
            key = (user_id, recipe_id)
            existing = earliest.get(key)
            if existing:
                flags['collapsed_user_content_repeat_rows'] += 1
            if existing is None or (record['timestamp'], review_id) < (existing['timestamp'], existing['review_id']):
                earliest[key] = record
    partition_users = defaultdict(set)
    for (user_id, recipe_id), record in earliest.items():
        partition = user_partition(user_id)
        partition_users[partition].add(user_id)
        if partition == 'train':
            if record['rating'] >= 4:
                popularity[recipe_id] += 1
            # Pseudonymous user key allows later CF work without exporting names.
            train_rows.append({'user_key': user_hash(user_id), **record})
        else:
            histories[partition][user_id].append(record)
    del earliest
    selected = {recipe_id for recipe_id, _ in sorted(popularity.items(), key=lambda pair: (-pair[1], pair[0]))[:args.catalog_size]}
    # Keep approved demo inputs addressable; do not use their ratings to select them.
    demo = json.loads((ROOT / 'data/catalog-selection.json').read_text(encoding='utf-8'))
    demo_map = {str(row['id']): canonical[row['id']] for row in demo}
    selected.update(demo_map.values())
    candidate_recipes = [recipes[recipe_id] | {'training_like_count': popularity[recipe_id],
                          'text': recipe_text(recipes[recipe_id])} for recipe_id in sorted(selected)]
    counts = {}
    for partition, users in histories.items():
        profiles = []
        counts[partition] = {'users': len(users), 'explicit_rows': 0, 'candidate_rows': 0,
            'positive_rows': 0, 'candidate_positive_rows': 0, 'eligible_profiles': 0}
        for user_id in sorted(users, key=user_hash):
            history = users[user_id]
            catalog_history = [row for row in history if row['recipe_id'] in selected]
            counts[partition]['explicit_rows'] += len(history)
            counts[partition]['candidate_rows'] += len(catalog_history)
            counts[partition]['positive_rows'] += sum(row['rating'] >= 4 for row in history)
            counts[partition]['candidate_positive_rows'] += sum(row['rating'] >= 4 for row in catalog_history)
            profile = make_profile(catalog_history)
            if profile:
                counts[partition]['eligible_profiles'] += 1
                if len(profiles) < args.max_eval_users:
                    profiles.append({'user_key': user_hash(user_id), **profile})
        counts[partition]['evaluated_or_reserved_profiles'] = len(profiles)
        dump(OUT / f'{partition}.json', profiles)
    # Save fitting data for reproduction, not a claim that a CF model was trained.
    train_rows = [row for row in train_rows if row['recipe_id'] in selected]
    train_rows.sort(key=lambda row: (row['user_key'], row['timestamp'], row['review_id']))
    pq.write_table(pa.Table.from_pylist(train_rows), OUT / 'train.parquet')
    dump(OUT / 'catalog.json', candidate_recipes)
    dump(OUT / 'demo-id-map.json', demo_map)
    artifacts = ['catalog.json', 'validation.json', 'test.json', 'train.parquet', 'demo-id-map.json']
    protocol = {'protocol': PROTOCOL, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'seed': SEED, 'source_manifest': manifest, 'source_flags': dict(flags),
        'partition': 'sha256(seed:user_id) modulo 100: 0..79 train, 80..89 validation, 90..99 test',
        'partition_users': {key: len(value) for key, value in partition_users.items()},
        'relevance': 'explicit rating >= 4; zero/missing excluded; 1..3 not seed likes',
        'catalog_selection': 'top training-user positive counts, ties by source ID; plus approved 30 demo IDs mapped to canonical content',
        'requested_popular_catalog_size': args.catalog_size, 'candidate_recipes': len(selected),
        'training_candidate_rows': len(train_rows), 'evaluation': counts,
        'profile': 'first six positive candidate-catalog recipes in timestamp/review-ID order; later-time positives withheld; all pre-cutoff observed recipes excluded',
        'metrics': 'macro Precision@10, Recall@10, binary NDCG@10, HitRate@10 on all candidate items minus seen; no sampled negatives',
        'test_status': 'reserved, not scored in ML 01',
        'limitations': ['Catalog-conditioned, active-reviewer sample; not the full catalog or representative of Expo visitors.',
            'User-disjoint, not global chronological: fitting-user ratings can be later than evaluation seeds.',
            'Exact title/ingredient identities collapsed; near-duplicate variants may remain.',
            'Unobserved items are not established dislikes; incomplete positives and positive-heavy ratings limit interpretation.',
            'Reused generic text model is not food-specific or fine-tuned; no allergy guarantees.'],
        'artifacts': {name: sha256(OUT / name) for name in artifacts}}
    dump(OUT / 'protocol.json', protocol)
    print(json.dumps({key: protocol[key] for key in ('candidate_recipes', 'training_candidate_rows', 'partition_users', 'evaluation')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
