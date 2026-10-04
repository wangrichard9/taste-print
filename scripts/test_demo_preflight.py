import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import check_demo as demo


class DemoPreflightTests(unittest.TestCase):
    def test_local_urls_only_without_embedded_credentials_or_routes(self):
        self.assertEqual(demo.local_base('http://127.0.0.1:5173/'), 'http://127.0.0.1:5173')
        self.assertEqual(demo.local_base('http://localhost:4173'), 'http://localhost:4173')
        for url in ('https://example.com', 'http://127.0.0.1:8000', 'http://localhost:4173/#discover',
                    'http://localhost:4173/api', 'http://user:password@localhost:4173', 'http://localhost:4173?x=1'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                demo.local_base(url)

    def test_ranked_response_rejects_excluded_duplicate_empty_and_sample_ids(self):
        self.assertEqual(demo.check_ranked({'catalogSize': 5006, 'items': [{'id': 'foodcom:1'}]}, ['foodcom:2']), 1)
        for items in ([], [{'id': 'foodcom:2'}], [{'id': 'foodcom:1'}] * 2,
                      [{'id': 'example:1'}], ['foodcom:1'], [{'id': None}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                demo.check_ranked({'catalogSize': 5006, 'items': items}, ['foodcom:2'])
        with self.assertRaises(ValueError):
            demo.check_ranked({'catalogSize': 6, 'items': [{'id': 'foodcom:1'}]}, [])

    def fake_fetch(self, base, path, payload, timeout):
        self.calls.append((base, path, payload, timeout))
        values = {'/': '<title>Tasteprint</title><script></script>',
                  '/api/health': {'method': 'raw_co_like', 'catalogSize': 5006, 'features': ['discover', 'ingredients', 'mealmerge']},
                  '/api/recommendations': {'method': 'raw_co_like', 'catalogSize': 5006, 'items': [{'id': 'foodcom:99', 'basis': 'co_like'}]},
                  '/api/ingredients': {'method': 'ingredient_rules+raw_co_like', 'catalogSize': 5006, 'newCount': 1, 'items': [{'id': 'foodcom:99'}]},
                  '/api/mealmerge': {'method': 'group_rules+raw_co_like', 'catalogSize': 5006, 'evidenceMemberCount': 2, 'items': [{'id': 'foodcom:99'}]},
                  '/api/recipes/99': {'id': 'foodcom:99', 'instructions': ['Source step']}}
        value = values[path]
        return (value if isinstance(value, str) else json.dumps(value)).encode()

    def test_preflight_checks_real_flow_contracts_without_mutating_input_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / 'src/data'
            data.mkdir(parents=True)
            reviewed = json.dumps([{'id': f'foodcom:{i}'} for i in range(1, 11)])
            bulk = json.dumps([{'id': 'foodcom:99', 'sourceRecipeId': 99}])
            (data / 'recipes.json').write_text(reviewed)
            (data / 'model-recipes.json').write_text(bulk)
            self.calls = []
            with patch.object(demo, 'ROOT', root):
                self.assertEqual(demo.preflight('http://localhost:4173', 3, self.fake_fetch, lambda _line: None), 6)
            self.assertEqual((data / 'recipes.json').read_text(), reviewed)
            self.assertEqual((data / 'model-recipes.json').read_text(), bulk)
            self.assertEqual(len(self.calls), 6)
            self.assertEqual(len(self.calls[2][2]['likes']), 6)
            self.assertTrue(all(base == 'http://localhost:4173' and timeout == 3 for base, _, _, timeout in self.calls))

    def test_failed_request_does_not_print_a_false_pass(self):
        lines = []
        def failed(*_args):
            raise TimeoutError('bounded timeout')
        with self.assertRaises(TimeoutError):
            demo.preflight('http://127.0.0.1:5173', fetch=failed, emit=lines.append)
        self.assertEqual(lines, [])


if __name__ == '__main__':
    unittest.main()
