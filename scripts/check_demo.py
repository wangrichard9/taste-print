"""Read-only local demo preflight. Never train, score held-out people or save choices."""
import argparse
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 8 * 1024 * 1024


def local_base(value):
    parsed = urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost')
            or parsed.port not in (5173, 4173) or parsed.username or parsed.password
            or parsed.path not in ('', '/') or parsed.query or parsed.fragment):
        raise ValueError('Use http://127.0.0.1:5173 or an existing localhost/4173 app origin, without a route')
    return value.rstrip('/')


def request(base, path, payload=None, timeout=10):
    body = None if payload is None else json.dumps(payload).encode('utf-8')
    headers = {} if body is None else {'Content-Type': 'application/json'}
    with urlopen(Request(base + path, data=body, headers=headers), timeout=timeout) as response:
        content = response.read(MAX_BODY + 1)
        if len(content) > MAX_BODY:
            raise ValueError('Unexpectedly large response')
        return content


def check_ranked(result, excluded, expected_catalog=5006):
    if not isinstance(result, dict) or result.get('catalogSize') != expected_catalog:
        raise ValueError('Unexpected recipe catalog')
    items = result.get('items')
    if not isinstance(items, list) or not items:
        raise ValueError('Expected actual recipe results, not an empty/sample response')
    ids = [row.get('id') for row in items if isinstance(row, dict)]
    if (len(ids) != len(items) or any(not isinstance(value, str) or not value.startswith('foodcom:') for value in ids)
            or len(set(ids)) != len(ids) or set(ids) & set(excluded)):
        raise ValueError('Invalid, duplicate or excluded recipe results')
    return len(items)


def preflight(base, timeout=10, fetch=request, emit=print):
    base = local_base(base)
    if not 1 <= timeout <= 30:
        raise ValueError('Timeout must be between 1 and 30 seconds')
    reviewed = json.loads((ROOT / 'src/data/recipes.json').read_text(encoding='utf-8'))
    bulk = json.loads((ROOT / 'src/data/model-recipes.json').read_text(encoding='utf-8'))
    likes = [row['id'] for row in reviewed[:6]]
    passed = reviewed[6]['id']
    checks = 0

    def call(label, path, payload=None, as_json=True):
        nonlocal checks
        started = time.perf_counter()
        content = fetch(base, path, payload, timeout)
        value = json.loads(content) if as_json else content.decode('utf-8')
        # A PASS is printed only after that check's assertions, below.
        return value, label, started

    def passed_check(label, started, detail):
        nonlocal checks
        checks += 1
        emit(f'PASS {label}: {detail} ({time.perf_counter() - started:.2f}s)')

    page, label, started = call('app HTML', '/', as_json=False)
    if 'Tasteprint' not in page or '<script' not in page:
        raise ValueError('The app HTML is not the expected Tasteprint entry')
    passed_check(label, started, 'Tasteprint entry is reachable')
    health, label, started = call('model via app proxy', '/api/health')
    if (health.get('method') != 'raw_co_like' or health.get('catalogSize') != 5006
            or not {'discover', 'ingredients', 'mealmerge'} <= set(health.get('features', []))):
        raise ValueError('Expected the current local recipe model with all three flows')
    passed_check(label, started, '5,006 recipes; Discover, Ingredients, MealMerge')

    discovery, label, started = call('Discover', '/api/recommendations', {'likes': likes, 'passes': [passed]})
    count = check_ranked(discovery, [*likes, passed])
    if discovery.get('method') != 'raw_co_like' or not any(row.get('basis') == 'co_like' for row in discovery['items']):
        raise ValueError('Expected actual shared-like recommendations')
    passed_check(label, started, f'{count:,} eligible recipe results')

    ingredients, label, started = call('Ingredients', '/api/ingredients', {
        'likes': likes, 'passes': [passed], 'ingredients': ['tomatoes', 'spinach', 'chickpeas'], 'priority': 'balanced'})
    count = check_ranked(ingredients, [passed])
    if ingredients.get('method') != 'ingredient_rules+raw_co_like' or ingredients.get('newCount', 0) <= 0:
        raise ValueError('Expected real ingredient retrieval with new options')
    passed_check(label, started, f'{count:,} real ingredient-matching options')

    group, label, started = call('MealMerge', '/api/mealmerge', {'priority': 'balanced', 'members': [
        {'id': 'you', 'name': 'QA host', 'likes': likes, 'passes': [passed]},
        {'id': 'guest-1', 'name': 'QA guest', 'likes': [reviewed[8]['id'], reviewed[9]['id']], 'passes': [likes[0]]}]})
    count = check_ranked(group, [passed, likes[0]])
    if group.get('method') != 'group_rules+raw_co_like' or group.get('evidenceMemberCount') != 2:
        raise ValueError('Expected actual two-person group evidence')
    passed_check(label, started, f'{count:,} eligible shared recipe results')

    source = bulk[0]
    directions, label, started = call('bulk source directions', f"/api/recipes/{source['sourceRecipeId']}")
    if (directions.get('id') != source['id'] or not isinstance(directions.get('instructions'), list)
            or not directions['instructions'] or any(not isinstance(step, str) or not step.strip() for step in directions['instructions'])):
        raise ValueError('Expected aligned nonblank source instructions')
    passed_check(label, started, f"{len(directions['instructions'])} source steps")
    emit(f'{checks} checks passed. QA requests only; no preferences or guests were persisted.')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:5173')
    parser.add_argument('--timeout', type=float, default=10)
    args = parser.parse_args()
    try:
        preflight(args.base_url, args.timeout)
    except (ValueError, OSError, TimeoutError) as error:
        parser.exit(1, f'FAIL demo preflight: {error}\nCheck the app/model terminals, then run the same check again. Do not clear browser data or retrain.\n')


if __name__ == '__main__':
    main()
