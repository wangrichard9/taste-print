"""Export source metadata for the frozen model catalog, never historical people."""
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse

import pyarrow.parquet as pq

from audit_foodcom import duration_minutes
from download_foodcom import sha256

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/discover'


def text(value):
    return html.unescape(value or '').strip()


def source_recipe(row):
    recipe_id = int(row['RecipeId'])
    name = text(row['Name'])
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'recipe'
    url = f'https://www.food.com/recipe/{slug}-{recipe_id}'
    photos = [value for value in (row['Images'] or []) if isinstance(value, str)
              and urlparse(value).scheme == 'https' and urlparse(value).netloc == 'img.sndimg.com']
    category = text(row['RecipeCategory']) or 'Recipe'
    # Category is source metadata, not an inferred taste, nutrition or safety claim.
    return {'id': f'foodcom:{recipe_id}', 'sourceRecipeId': recipe_id,
            'sourceName': name, 'sourceCategory': row['RecipeCategory'],
            'sourceUrl': url, 'datasetUrl': 'https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews',
            'datasetVersion': 2, 'name': name, 'category': category,
            'description': f'From the Food.com {category.lower()} collection.',
            'image': photos[0] if photos else '', 'imageAlt': f'Food.com recipe photograph: {name}',
            'imageSource': url, 'tags': [category],
            'ingredients': [text(value) for value in (row['RecipeIngredientParts'] or []) if text(value)],
            'instructions': [text(value) for value in (row['RecipeInstructions'] or []) if text(value)],
            'totalMinutes': duration_minutes(row['TotalTime']), 'servings': row['RecipeServings'],
            'modelSupported': True, 'manuallyReviewed': False}


def export():
    catalog_path = ROOT / 'data/processed/ml01/catalog.json'
    protocol = json.loads((ROOT / 'data/processed/ml04/protocol.json').read_text(encoding='utf-8'))
    if sha256(catalog_path) != protocol['old_artifact_sha256']['ml01/catalog.json']:
        raise ValueError('Frozen model catalog has changed')
    model = json.loads(catalog_path.read_text(encoding='utf-8'))
    model_ids = {item['id'] for item in model}
    reviewed_path = ROOT / 'src/data/recipes.json'
    reviewed = json.loads(reviewed_path.read_text(encoding='utf-8'))
    recipe_file = ROOT / 'data/raw/foodcom-v2/recipes.parquet'
    source = json.loads((recipe_file.parent / 'manifest.json').read_text(encoding='utf-8'))
    receipt = next(item for item in source['files'] if item['name'] == 'recipes.parquet')
    if source['version'] != 2 or sha256(recipe_file) != receipt['sha256']:
        raise ValueError('Source recipes differ from audited download')
    fields = ['RecipeId', 'Name', 'RecipeCategory', 'Images', 'RecipeIngredientParts',
              'RecipeInstructions', 'TotalTime', 'RecipeServings']
    recipes = {}
    for batch in pq.ParquetFile(recipe_file).iter_batches(batch_size=8192, columns=fields):
        for row in batch.to_pylist():
            if row['RecipeId'] in model_ids:
                recipes[int(row['RecipeId'])] = source_recipe(row)
    if set(recipes) != model_ids:
        raise ValueError('Some model recipes lack source records')
    for dish in reviewed:
        recipes[dish['sourceRecipeId']] = {**dish, 'modelSupported': dish['sourceRecipeId'] in model_ids,
                                         'manuallyReviewed': True}
    # Original reviewed data stays unchanged. Extra summaries contain no steps;
    # source directions are served on demand, not put in the JavaScript bundle.
    reviewed_ids = {dish['sourceRecipeId'] for dish in reviewed}
    extras = [{**recipes[item['id']], 'instructions': []} for item in model if item['id'] not in reviewed_ids]
    frontend = ROOT / 'src/data/model-recipes.json'
    frontend.write_text(json.dumps(extras, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / 'recipes.json'
    destination.write_text(json.dumps(list(recipes.values()), ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')
    provenance = {'model_catalog_sha256': sha256(catalog_path), 'source_recipes_sha256': sha256(recipe_file),
                  'reviewed_catalog_sha256': sha256(reviewed_path), 'frontend_summary_sha256': sha256(frontend),
                  'serving_recipes_sha256': sha256(destination), 'model_recipes': len(model),
                  'reviewed_recipes': len(reviewed), 'legacy_outside_model': len(reviewed_ids - model_ids),
                  'display_recipes': len(recipes), 'photos_present': sum(bool(dish['image']) for dish in recipes.values())}
    (OUT / 'manifest.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(provenance, indent=2))


if __name__ == '__main__':
    export()
