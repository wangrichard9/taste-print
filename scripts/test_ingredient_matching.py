import json
import unittest
from discover_service import load_engine
from ingredient_matching import IngredientIndex, canonical_name, distinct_match_count, ingredient_inputs
import test_discover_service as serving_tests


def ingredient_fixture():
    engine = serving_tests.fixture()
    lists = [['tomatoes'], ['tomatoes', 'spinach', 'salt', 'pasta'],
             ['tomatoes', 'spinach'], ['tomatoes', 'spinach', 'chickpeas'], ['tomatoes']]
    for dish, ingredients in zip(engine.dishes.values(), lists):
        dish['ingredients'] = ingredients
    engine.ingredients = IngredientIndex(engine.dishes.values())
    return engine


class IngredientMatchingTests(unittest.TestCase):
    def test_case_plural_preparation_and_aliases(self):
        self.assertEqual(canonical_name('Fresh chopped TOMATOES'), 'tomato')
        self.assertEqual(canonical_name('garbanzo beans'), 'chickpea')
        self.assertEqual(canonical_name('Garlic cloves'), 'garlic')
        self.assertEqual(ingredient_inputs(['Chickpeas', 'garbanzo beans', ' chickpeas ']), {'chickpea': 'Chickpeas'})
        self.assertEqual(canonical_name('scallions'), canonical_name('spring onion'))

    def test_family_names_without_substring_or_processed_product_matches(self):
        rows = [{'id': str(i), 'ingredients': [name]} for i, name in enumerate([
            'cherry tomatoes', 'tomato paste', 'eggplant', 'whole eggs', 'rice vinegar', 'rice',
            'coconut milk', 'buttermilk', 'whole milk', 'boneless skinless chicken breasts'])]
        index = IngredientIndex(rows)
        for query, expected in [('tomatoes', {'0'}), ('egg', {'3'}), ('rice', {'5'}), ('milk', {'8'}), ('chicken', {'9'})]:
            self.assertEqual(set(index.match([query])[1]), expected)
        self.assertEqual(index.match(['cherry tomato'])[1]['0']['matches'][0]['recipeIngredient'], 'cherry tomatoes')

    def test_source_duplicates_additional_entries_and_overlapping_queries(self):
        index = IngredientIndex([{'id': 'a', 'ingredients': ['tomatoes', 'fresh tomatoes', 'spinach', 'salt']}])
        labels, found = index.match(['tomatoes', 'tomato', 'Spinach'])
        self.assertEqual(labels, ['tomatoes', 'Spinach'])
        self.assertEqual(found['a']['matchCount'], 2)
        self.assertEqual(found['a']['additionalIngredients'], ['salt'])
        self.assertEqual(index.match(['dragon fruit'])[1], {})
        # Three query labels / three source entries, but only two independent fits.
        matches = [{'input': label, 'recipeIngredient': source} for label, source in
                   [('onion', 'red onion'), ('red onion', 'red onion'), ('tomato', 'roma tomato'), ('tomato', 'cherry tomato')]]
        self.assertEqual(distinct_match_count(matches), 2)

    def test_invalid_inputs_are_rejected_atomically(self):
        for values in [None, [], 'rice', [True], [''], ['   '], ['123'], ['fresh'], ['a' * 41], ['rice'] * 13]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                ingredient_inputs(values)


class IngredientServingTests(unittest.TestCase):
    def test_priorities_are_distinct_and_favorites_remain_eligible(self):
        engine = ingredient_fixture()
        expected = {'balanced': ['4', '2', '3'], 'ingredients': ['4', '3', '2'], 'taste': ['2', '3', '4']}
        for priority, order in expected.items():
            payload = {'likes': ['foodcom:1'], 'ingredients': ['tomato', 'spinach', 'chickpea'], 'priority': priority}
            result = engine.ingredient_recommendations(payload)
            self.assertEqual([item['id'].split(':')[1] for item in result['items'] if not item['knownLike']], order)
            self.assertEqual((result['newCount'], result['knownCount']), (3, 1))
            known = next(item for item in result['items'] if item['knownLike'])
            self.assertEqual(known['basis'], 'known_like')
            self.assertNotIn('evidence', known)
            self.assertTrue(all('score' not in item and 'popularity' not in item for item in result['items']))
            self.assertEqual(result, engine.ingredient_recommendations(payload))

    def test_passes_fallback_evidence_and_empty_matches(self):
        engine = ingredient_fixture()
        result = engine.ingredient_recommendations({'likes': ['foodcom:1'], 'passes': ['foodcom:3'], 'ingredients': ['tomato']})
        self.assertNotIn('foodcom:3', [item['id'] for item in result['items']])
        co = next(item for item in result['items'] if item['id'] == 'foodcom:2')
        self.assertEqual(co['evidence'], {'seedId': 'foodcom:1', 'sharedLikers': 2})
        result = engine.ingredient_recommendations({'ingredients': ['tomato']})
        self.assertTrue(all(item['basis'] == 'popularity' and 'evidence' not in item for item in result['items']))
        self.assertEqual(result['items'][0]['id'], 'foodcom:2')
        result = engine.ingredient_recommendations({'ingredients': ['dragon fruit']})
        self.assertEqual((result['newCount'], result['knownCount'], result['items']), (0, 0, []))

    def test_invalid_requests(self):
        engine = ingredient_fixture()
        for payload in [{}, {'ingredients': []}, {'ingredients': ['rice'], 'priority': []},
                        {'ingredients': ['rice'], 'priority': 'unknown'}, {'ingredients': ['rice'], 'saved': []},
                        {'ingredients': ['rice'], 'likes': ['foodcom:99']}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                engine.ingredient_recommendations(payload)

    def test_real_catalog_matches_source_metadata_without_changing_model(self):
        engine = load_engine()
        result = engine.ingredient_recommendations({'ingredients': ['Tomatoes', 'Spinach', 'Chickpeas']})
        self.assertEqual(result['catalogSize'], 5006)
        self.assertGreater(result['newCount'], 3)
        self.assertEqual(result['knownCount'], 0)
        for item in result['items']:
            source = engine.dishes[item['id']]['ingredients']
            self.assertTrue(all(pair['recipeIngredient'] in source for pair in item['matches']))
            self.assertTrue(all(value in source for value in item['additionalIngredients']))
            self.assertGreaterEqual(item['matchCount'], 1)


# Reuse the HTTP fixture, without inheriting/rerunning its test methods.
class IngredientHttpTests(unittest.TestCase):
    setUpClass = classmethod(serving_tests.DiscoverHttpTests.setUpClass.__func__)
    tearDownClass = classmethod(serving_tests.DiscoverHttpTests.tearDownClass.__func__)
    request = serving_tests.DiscoverHttpTests.request

    def test_ingredient_endpoint_and_error_status(self):
        headers = {'Content-Type': 'application/json', 'Origin': 'http://127.0.0.1:5173'}
        status, result, output = self.request('POST', '/api/ingredients', json.dumps({'ingredients': ['tomato']}), headers)
        self.assertEqual(status, 200)
        self.assertEqual(result['method'], 'ingredient_rules+raw_co_like')
        self.assertEqual(result['newCount'], 4)
        self.assertEqual(output['Cache-Control'], 'no-store')
        self.assertEqual(self.request('POST', '/api/ingredients', '{}', headers)[0], 400)
        self.assertEqual(self.request('POST', '/api/ingredients', '{"ingredients":["rice"]}',
                                      {'Content-Type': 'application/json', 'Origin': 'https://other.example'})[0], 403)


if __name__ == '__main__':
    unittest.main()
