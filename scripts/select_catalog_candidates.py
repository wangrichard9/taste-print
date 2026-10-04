"""Find review candidates; final editorial selection is explicit, not automatic."""
import json
import re
from pathlib import Path
import pyarrow.parquet as pq
from audit_foodcom import canonical_id, duration_minutes, usable_list

ROOT = Path(__file__).resolve().parents[1]
queries = ['pizza', 'pesto pasta', 'pasta salad', 'salmon', 'chicken curry', 'chicken stir',
           'tacos', 'lentil soup', 'chickpea', 'risotto', 'tomato soup', 'meatballs',
           'fried rice', 'teriyaki', 'enchiladas', 'falafel', 'noodles', 'chili',
           'greek salad', 'caesar salad', 'roasted cauliflower', 'vegetable soup',
           'burrito', 'chicken salad', 'macaroni cheese', 'lasagna', 'sweet potato',
           'black bean', 'mushroom', 'frittata']
found = {query: [] for query in queries}
fields = ['RecipeId','Name','Description','Images','RecipeCategory','Keywords','RecipeIngredientParts',
          'RecipeIngredientQuantities','RecipeInstructions','TotalTime','RecipeServings','ReviewCount']
for batch in pq.ParquetFile(ROOT / 'data/raw/foodcom-v2/recipes.parquet').iter_batches(batch_size=8192, columns=fields):
    for row in batch.to_pylist():
        minutes = duration_minutes(row['TotalTime'])
        parts = row['RecipeIngredientParts'] or []
        quantities = row['RecipeIngredientQuantities'] or []
        if not (canonical_id(row['RecipeId']) and usable_list(parts) and usable_list(row['RecipeInstructions'])
                and len(parts) == len(quantities) and row['Images'] and minutes and 0 < minutes <= 90
                and (row['ReviewCount'] or 0) >= 5 and len(row['RecipeInstructions']) <= 20):
            continue
        name = row['Name'].lower()
        for query in queries:
            if all(word in name for word in query.split()):
                found[query].append(row)
for query in queries:
    found[query] = sorted(found[query], key=lambda row: (-(row['ReviewCount'] or 0), row['RecipeId']))[:3]
destination = ROOT / 'data/processed/foodcom-v2/catalog-candidates.json'
destination.write_text(json.dumps(found, indent=2), encoding='utf-8')
print(json.dumps({query: [{'id':int(row['RecipeId']), 'name':row['Name'], 'reviews':row['ReviewCount']} for row in rows] for query,rows in found.items()},indent=2))
