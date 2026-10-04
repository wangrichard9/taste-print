"""Mechanically export an explicitly reviewed selection into frontend recipe data."""
import hashlib
import html
import json
from pathlib import Path
import re
import pyarrow.parquet as pq
from audit_foodcom import duration_minutes, usable_list
from download_foodcom import sha256

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'data/raw/foodcom-v2/manifest.json').read_text(encoding='utf-8'))
if manifest['version'] != 2 or manifest['source'] != 'https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews':
    raise ValueError('Unexpected dataset provenance')
recipe_file = ROOT / 'data/raw/foodcom-v2/recipes.parquet'
receipt = next(item for item in manifest['files'] if item['name'] == 'recipes.parquet')
if recipe_file.stat().st_size != receipt['bytes'] or sha256(recipe_file) != receipt['sha256']:
    raise ValueError('Recipe file differs from its download manifest')
selection = json.loads((ROOT / 'data/catalog-selection.json').read_text(encoding='utf-8'))
assert len(selection) == 30 and len({item['id'] for item in selection}) == 30
ids = {item['id'] for item in selection}
rows = {}
fields = ['RecipeId','Name','Images','RecipeIngredientParts','RecipeIngredientQuantities',
          'RecipeInstructions','TotalTime','RecipeServings','RecipeCategory','Keywords']
for batch in pq.ParquetFile(recipe_file).iter_batches(batch_size=8192, columns=fields):
    for row in batch.to_pylist():
        if row['RecipeId'] in ids:
            rows[int(row['RecipeId'])] = row
recipes = []
for item in selection:
    row = rows[item['id']]
    assert usable_list(row['RecipeIngredientParts']) and usable_list(row['RecipeInstructions'])
    assert len(row['RecipeIngredientParts']) == len(row['RecipeIngredientQuantities'])
    photo = row['Images'][item.get('photoIndex', 0)]
    assert photo.startswith('https://img.sndimg.com/')
    original_name = html.unescape(row['Name'])
    slug = re.sub(r'[^a-z0-9]+', '-', original_name.lower()).strip('-')
    source_url = f"https://www.food.com/recipe/{slug}-{item['id']}"
    recipes.append({
        'id': f"foodcom:{item['id']}", 'sourceRecipeId': item['id'],
        'sourceName': original_name, 'sourceCategory': row['RecipeCategory'],
        'sourceUrl': source_url, 'datasetUrl':'https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews',
        'datasetVersion': 2, 'name':item['name'], 'category':item['category'],
        'description':item['description'], 'tags':item['tags'],
        'image':photo, 'imageAlt':f"Food.com recipe photograph: {item['name']}",
        'imageSource':source_url,
        'ingredients':[html.unescape(value) for value in row['RecipeIngredientParts']],
        'instructions':[html.unescape(value).strip() for value in row['RecipeInstructions']],
        'totalMinutes':duration_minutes(row['TotalTime']), 'servings':row['RecipeServings'],
    })
destination = ROOT / 'src/data/recipes.json'
destination.write_text(json.dumps(recipes, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f"Exported {len(recipes)} explicitly selected recipes; SHA-256 {hashlib.sha256(destination.read_bytes()).hexdigest()}")
