"""Create a local QA contact sheet; no photo downloads or extra app routes."""
import html
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--alternates', action='store_true')
parser.add_argument('--ids', help='Comma-separated source IDs for alternate photo review')
args = parser.parse_args()
recipes = json.loads((root / 'src/data/recipes.json').read_text(encoding='utf-8'))
if args.alternates:
    candidates = json.loads((root / 'data/processed/foodcom-v2/catalog-candidates.json').read_text(encoding='utf-8'))
    rows = {int(row['RecipeId']):row for group in candidates.values() for row in group}
    ids = [int(value) for value in args.ids.split(',')] if args.ids else [139798,213535,266209,153569,46221,86112,120810,25360]
    recipes = [{'sourceRecipeId':id, 'name':f'{rows[id]["Name"]} · photo {index}', 'image':url}
               for id in ids for index,url in enumerate(rows[id]['Images'])]
cards = ''.join(f'<figure><img src="{html.escape(item["image"],quote=True)}" alt="{html.escape(item["name"],quote=True)}" referrerpolicy="no-referrer"><figcaption>{item["sourceRecipeId"]} · {html.escape(item["name"])}</figcaption></figure>' for item in recipes)
document = '<!doctype html><html><head><meta charset="utf-8"><title>Tasteprint photo review</title><style>body{margin:20px;font:12px Arial;background:white;color:#17191e}h1{font-size:20px}main{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:16px}figure{margin:0}img{display:block;width:100%;height:145px;object-fit:cover;background:#f5f7fb}figcaption{padding:7px 0;line-height:1.4;min-height:34px}</style></head><body><h1>Selected recipe photo review · not an app screen</h1><main>' + cards + '</main></body></html>'
(root / 'data/processed/foodcom-v2/catalog-review.html').write_text(document,encoding='utf-8')
print('Local contact sheet created.')
