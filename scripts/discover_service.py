"""Loopback-only serving of the saved raw co-like model. No fitting or labels."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
from scipy.sparse import load_npz

from co_like import score_likes
from download_foodcom import sha256
from recommendation import rank
from ingredient_matching import IngredientIndex, PRIORITIES, priority_key
from group_recommendation import group_recommendations

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ORIGINS = {'http://127.0.0.1:5173', 'http://localhost:5173',
                   'http://127.0.0.1:4173', 'http://localhost:4173'}


class LocalModelServer(ThreadingHTTPServer):
    # Windows SO_REUSEADDR can let a second server bind the same live port.
    # Fail clearly instead of appearing ready while an old service gets traffic.
    allow_reuse_address = not hasattr(socket, 'SO_EXCLUSIVEADDRUSE')

    def server_bind(self):
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class DiscoverEngine:
    def __init__(self, model_catalog, relationships, dishes):
        self.ids = np.array([item['id'] for item in model_catalog], dtype=np.int64)
        self.index = {f'foodcom:{recipe_id}': i for i, recipe_id in enumerate(self.ids)}
        self.popularity = np.array([item['training_like_count'] for item in model_catalog], dtype=float)
        self.weights = relationships.tocsr()
        self.dishes = {dish['id']: dish for dish in dishes}
        self.ingredients = IngredientIndex(dishes)
        if (self.weights.shape != (len(self.ids), len(self.ids)) or self.weights.diagonal().any()
                or not np.isfinite(self.weights.data).all() or (self.weights.data < 0).any()
                or not np.isfinite(self.popularity).all() or len(self.index) != len(self.ids)
                or not set(self.index) <= self.dishes.keys()):
            raise ValueError('Invalid or unaligned serving model')

    def choice_context(self, payload, allowed=('likes', 'passes'), dense_evidence=True):
        if not isinstance(payload, dict) or set(payload) - set(allowed):
            raise ValueError('Unexpected request fields')
        choices = {}
        for kind in ('likes', 'passes'):
            values = payload.get(kind, [])
            if (not isinstance(values, list) or len(values) > len(self.dishes)
                    or any(not isinstance(value, str) or value not in self.dishes for value in values)):
                raise ValueError('Choices must be known recipe IDs')
            choices[kind] = set(values)
        if choices['likes'] & choices['passes']:
            raise ValueError('A recipe cannot be liked and passed simultaneously')
        likes = sorted(choices['likes'] & self.index.keys())
        seeds = [self.index[value] for value in likes]
        scores = score_likes(self.weights, [seeds])[0] if seeds else np.zeros(len(self.ids))
        seed_weights = (self.weights[seeds].toarray() if dense_evidence else self.weights[seeds].tocsc()) if seeds else None
        return choices, likes, scores, seed_weights

    def recommend(self, payload):
        choices, likes, scores, seed_weights = self.choice_context(payload)
        seen = {self.ids[self.index[value]] for value in choices['likes'] | choices['passes'] if value in self.index}
        co_order = rank(scores, self.ids, seen, len(self.ids))
        positive = [int(i) for i in co_order if scores[i] > 0]
        fallback = [int(i) for i in rank(self.popularity, self.ids, seen, len(self.ids)) if scores[i] <= 0]
        items = []
        for i in positive + fallback:
            item = {'id': f'foodcom:{self.ids[i]}', 'basis': 'co_like' if scores[i] > 0 else 'popularity'}
            if scores[i] > 0:
                strongest = int(np.argmax(seed_weights[:, i]))
                item['evidence'] = {'seedId': likes[strongest], 'sharedLikers': int(seed_weights[strongest, i])}
            items.append(item)
        return {'method': 'raw_co_like', 'mode': 'co_like' if positive else 'popularity',
                'supportedLikeCount': len(likes), 'unsupportedLikeCount': len(choices['likes']) - len(likes),
                'catalogSize': len(self.ids), 'personalizedCount': len(positive), 'items': items}

    def ingredient_recommendations(self, payload):
        choices, likes, scores, seed_weights = self.choice_context(payload, ('likes', 'passes', 'ingredients', 'priority'))
        priority = payload.get('priority', 'balanced')
        if priority not in PRIORITIES:
            raise ValueError('Unknown ingredient priority')
        inputs, matches = self.ingredients.match(payload.get('ingredients'))
        ranked = []
        for recipe_id, match in matches.items():
            if recipe_id not in self.index or recipe_id in choices['passes']:
                continue
            i = self.index[recipe_id]
            known = recipe_id in choices['likes']
            item = {**match, 'id': recipe_id, 'sourceRecipeId': int(self.ids[i]), 'knownLike': known,
                    'basis': 'known_like' if known else 'co_like' if scores[i] > 0 else 'popularity',
                    'score': float(scores[i]), 'popularity': float(self.popularity[i])}
            if scores[i] > 0 and not known:
                strongest = int(np.argmax(seed_weights[:, i]))
                item['evidence'] = {'seedId': likes[strongest], 'sharedLikers': int(seed_weights[strongest, i])}
            ranked.append(item)
        ranked.sort(key=lambda item: priority_key(item, priority))
        new_count = sum(not item['knownLike'] for item in ranked)
        for item in ranked:
            for internal in ('score', 'popularity', 'sourceRecipeId'):
                del item[internal]
        return {'method': 'ingredient_rules+raw_co_like', 'priority': priority, 'ingredients': inputs,
                'catalogSize': len(self.ids), 'supportedLikeCount': len(likes),
                'newCount': new_count, 'knownCount': len(ranked) - new_count, 'items': ranked}


def load_engine(root=ROOT):
    folder = root / 'data/processed/ml04'
    protocol_path = folder / 'protocol.json'
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    models = json.loads((folder / 'models.json').read_text(encoding='utf-8'))
    catalog_path = root / 'data/processed/ml01/catalog.json'
    artifact = folder / 'direct_raw.npz'
    if (models['protocol_sha256'] != sha256(protocol_path) or models['test_scored']
            or sha256(catalog_path) != protocol['old_artifact_sha256']['ml01/catalog.json']
            or sha256(artifact) != models['models']['direct/raw']['artifact_sha256']['direct_raw.npz']
            or sha256(Path(__file__).with_name('co_like.py')) != protocol['implementation_sha256']['co_like.py']
            or sha256(Path(__file__).with_name('recommendation.py')) != protocol['implementation_sha256']['recommendation.py']):
        raise ValueError('Frozen model provenance changed')
    serving = root / 'data/processed/discover'
    manifest = json.loads((serving / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest['model_catalog_sha256'] != sha256(catalog_path)
            or manifest['serving_recipes_sha256'] != sha256(serving / 'recipes.json')
            or manifest['frontend_summary_sha256'] != sha256(root / 'src/data/model-recipes.json')
            or manifest['reviewed_catalog_sha256'] != sha256(root / 'src/data/recipes.json')):
        raise ValueError('Serving metadata is stale; run export_discover.py')
    return DiscoverEngine(json.loads(catalog_path.read_text(encoding='utf-8')), load_npz(artifact),
                          json.loads((serving / 'recipes.json').read_text(encoding='utf-8')))


def handler_for(engine):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            # No choice bodies, historical IDs or profile data in request logs.
            pass

        def allowed(self):
            host = self.headers.get('Host', '').split(':')[0]
            origin = self.headers.get('Origin')
            return host in ('127.0.0.1', 'localhost') and (origin is None or origin in ALLOWED_ORIGINS)

        def respond(self, status, value):
            data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            origin = self.headers.get('Origin')
            if origin in ALLOWED_ORIGINS:
                self.send_header('Access-Control-Allow-Origin', origin)
                self.send_header('Vary', 'Origin')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if not self.allowed():
                return self.respond(403, {'error': 'Local app access only'})
            path = urlparse(self.path).path
            if path == '/api/health':
                return self.respond(200, {'method': 'raw_co_like', 'catalogSize': len(engine.ids),
                                          'displaySize': len(engine.dishes), 'testScored': False,
                                          'revision': 'build05', 'features': ['discover', 'ingredients', 'mealmerge']})
            if path.startswith('/api/recipes/'):
                recipe_id = 'foodcom:' + path.removeprefix('/api/recipes/')
                dish = engine.dishes.get(recipe_id)
                return self.respond(200, dish) if dish else self.respond(404, {'error': 'Recipe not found'})
            return self.respond(404, {'error': 'Not found'})

        def do_POST(self):
            # Consume a bounded body before rejecting its origin/type/path.
            # Closing a Windows socket with unread POST bytes can reset the
            # connection before the client receives the intended error response.
            try:
                size = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                return self.respond(400, {'error': 'Invalid request size'})
            if size <= 0 or size > 262144:
                return self.respond(413 if self.allowed() else 403, {'error': 'Invalid request size'})
            self.connection.settimeout(5)
            try:
                body = self.rfile.read(size)
            except TimeoutError:
                return self.respond(408, {'error': 'Request body timed out'})
            if not self.allowed():
                return self.respond(403, {'error': 'Local app access only'})
            if self.path not in ('/api/recommendations', '/api/ingredients', '/api/mealmerge'):
                return self.respond(404, {'error': 'Not found'})
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.respond(415, {'error': 'JSON required'})
            try:
                payload = json.loads(body)
                if self.path == '/api/mealmerge':
                    result = group_recommendations(engine, payload)
                elif self.path == '/api/ingredients':
                    result = engine.ingredient_recommendations(payload)
                else:
                    result = engine.recommend(payload)
            except (ValueError, UnicodeError):
                return self.respond(400, {'error': 'Invalid recipe choices, ingredient list or group'})
            return self.respond(200, result)

        def do_OPTIONS(self):
            if not self.allowed():
                return self.respond(403, {'error': 'Local app access only'})
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin', 'http://127.0.0.1:5173'))
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Vary', 'Origin')
            self.end_headers()
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    engine = load_engine()
    server = LocalModelServer(('127.0.0.1', args.port), handler_for(engine))
    print(f'Tasteprint local model ready: {len(engine.ids)} recipes at http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
