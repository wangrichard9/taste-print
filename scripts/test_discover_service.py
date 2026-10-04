import http.client
import json
from pathlib import Path
import threading
import unittest
from http.server import ThreadingHTTPServer

import numpy as np
from scipy.sparse import csr_matrix

from co_like import score_likes
from discover_service import DiscoverEngine, handler_for, load_engine, ROOT
from recommendation import rank


def fixture():
    catalog = [{'id': i, 'training_like_count': count} for i, count in zip(range(1, 5), [5, 10, 3, 1])]
    weights = csr_matrix([[0, 2, 1, 0], [2, 0, 4, 0], [1, 4, 0, 0], [0, 0, 0, 0]])
    dishes = [{'id': f'foodcom:{i}', 'instructions': ['A source step'], 'ingredients': ['tomatoes']} for i in range(1, 6)]
    return DiscoverEngine(catalog, weights, dishes)


class DiscoverServingTests(unittest.TestCase):
    def test_score_equivalence_evidence_and_seen_exclusions(self):
        engine = fixture()
        result = engine.recommend({'likes': ['foodcom:1', 'foodcom:1'], 'passes': ['foodcom:2']})
        self.assertEqual(result['supportedLikeCount'], 1)
        self.assertEqual(result['items'], [
            {'id': 'foodcom:3', 'basis': 'co_like', 'evidence': {'seedId': 'foodcom:1', 'sharedLikers': 1}},
            {'id': 'foodcom:4', 'basis': 'popularity'}])
        expected = score_likes(engine.weights, [[0]])[0]
        np.testing.assert_array_equal(expected, [0, 2, 1, 0])

    def test_empty_all_passes_unsupported_and_isolated_likes_fall_back(self):
        engine = fixture()
        for payload in ({}, {'likes': ['foodcom:5']}, {'likes': ['foodcom:4']}):
            result = engine.recommend(payload)
            self.assertEqual(result['mode'], 'popularity')
            self.assertTrue(all(item == {'id': item['id'], 'basis': 'popularity'} for item in result['items']))
        self.assertEqual(engine.recommend({})['items'][0]['id'], 'foodcom:2')
        self.assertEqual(engine.recommend({'passes': [f'foodcom:{i}' for i in range(1, 5)]})['items'], [])

    def test_mean_uses_all_unique_likes_without_turning_passes_into_bans(self):
        result = fixture().recommend({'likes': ['foodcom:1', 'foodcom:2']})
        self.assertEqual(result['items'][0]['id'], 'foodcom:3')
        self.assertEqual(result['items'][0]['evidence'], {'seedId': 'foodcom:2', 'sharedLikers': 4})

    def test_invalid_choices_and_unaligned_models_fail_explicitly(self):
        engine = fixture()
        for payload in ([], None, {'saved': []}, {'likes': 'foodcom:1'}, {'likes': [True]},
                        {'likes': ['foodcom:99']}, {'likes': ['foodcom:1'], 'passes': ['foodcom:1']}):
            with self.assertRaises(ValueError):
                engine.recommend(payload)
        with self.assertRaises(ValueError):
            DiscoverEngine([{'id': 1, 'training_like_count': 1}], csr_matrix([[2]]), [{'id': 'foodcom:1', 'ingredients': []}])


class DiscoverHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(fixture()))
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse()
        status, data, output_headers = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return status, json.loads(data) if data else None, output_headers

    def test_routes_and_local_preflight(self):
        self.assertEqual(self.request('GET', '/api/health')[1]['catalogSize'], 4)
        self.assertEqual(self.request('GET', '/api/recipes/1')[1]['instructions'], ['A source step'])
        self.assertEqual(self.request('GET', '/api/recipes/999')[0], 404)
        self.assertEqual(self.request('GET', '/data/raw/foodcom-v2/reviews.parquet')[0], 404)
        status, result, headers = self.request('POST', '/api/recommendations', '{"likes":["foodcom:1"]}',
            {'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:5173'})
        self.assertEqual(status, 200)
        self.assertEqual(result['mode'], 'co_like')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['Access-Control-Allow-Origin'], 'http://127.0.0.1:5173')
        self.assertEqual(self.request('OPTIONS', '/api/recommendations', headers={'Origin': 'http://127.0.0.1:5173'})[0], 204)

    def test_remote_origins_hosts_invalid_json_and_bodies_are_rejected(self):
        self.assertEqual(self.request('GET', '/api/health', headers={'Origin': 'https://untrusted.example'})[0], 403)
        self.assertEqual(self.request('GET', '/api/health', headers={'Host': 'untrusted.example'})[0], 403)
        self.assertEqual(self.request('POST', '/api/recommendations', '{}')[0], 415)
        self.assertEqual(self.request('POST', '/api/recommendations', 'broken', {'Content-Type': 'application/json'})[0], 400)
        self.assertEqual(self.request('POST', '/api/recommendations', '{}', {'Content-Type': 'application/json', 'Content-Length': '262145'})[0], 413)


@unittest.skipUnless((ROOT / 'data/processed/discover/manifest.json').exists(), 'Export Discover metadata first')
class DiscoverArtifactTests(unittest.TestCase):
    def test_saved_model_alignment_metadata_and_original_ranking(self):
        engine = load_engine()
        self.assertEqual(len(engine.ids), 5006)
        self.assertEqual(len(engine.dishes), 5006)
        reviewed = json.loads((ROOT / 'src/data/recipes.json').read_text(encoding='utf-8'))
        for dish in reviewed:
            self.assertIn(dish['id'], engine.index)
            for key, value in dish.items():
                self.assertEqual(engine.dishes[dish['id']][key], value)
        # Use existing validation inputs to check serving equivalence only;
        # never read, score or modify the held-out final-test profiles.
        profile = json.loads((ROOT / 'data/processed/ml01/validation.json').read_text(encoding='utf-8'))[120]
        likes = [f'foodcom:{value}' for value in profile['likes']]
        passes = [f'foodcom:{value}' for value in profile['seen'] if value not in profile['likes'] and f'foodcom:{value}' in engine.dishes]
        result = engine.recommend({'likes': likes, 'passes': passes})
        scores = score_likes(engine.weights, [[engine.index[value] for value in likes]])[0]
        expected = [f'foodcom:{engine.ids[i]}' for i in rank(scores, engine.ids, profile['seen'], 10)]
        self.assertEqual([item['id'] for item in result['items'][:10]], expected)
        summaries = json.loads((ROOT / 'src/data/model-recipes.json').read_text(encoding='utf-8'))
        self.assertEqual(len(summaries), 4976)
        for dish in summaries:
            self.assertEqual(dish['instructions'], [])
            self.assertTrue(dish['modelSupported'])
            self.assertFalse(dish['manuallyReviewed'])
            self.assertTrue(not dish['image'] or dish['image'].startswith('https://img.sndimg.com/'))


if __name__ == '__main__':
    unittest.main()
