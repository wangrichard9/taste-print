import itertools
import json
import unittest
import numpy as np
from scipy.sparse import csr_matrix
from discover_service import DiscoverEngine, LocalModelServer, handler_for, load_engine
from group_recommendation import aggregate_key, group_recommendations, relative_positions
import test_discover_service as serving_tests


def fixture():
    weights = np.zeros((7, 7))
    weights[0, 2:] = [10, 8, 9, 7, 6]
    weights[1, 2:] = [7, 8, 10, 9, 6]
    weights[2:, :2] = weights[:2, 2:].T
    return DiscoverEngine([{'id': i + 1, 'training_like_count': count} for i, count in enumerate([100, 90, 20, 20, 30, 5, 1])],
        csr_matrix(weights), [{'id': f'foodcom:{i}', 'ingredients': ['tomatoes']} for i in range(1, 8)])


def member(member_id, like=None, passes=()):
    return {'id': member_id, 'name': member_id, 'likes': [like] if like else [], 'passes': list(passes)}


class GroupPolicyTests(unittest.TestCase):
    def test_tie_aware_positions_unknown_and_scale_invariance(self):
        scores = np.array([9, 9, 3, 0, 100])
        eligible = np.array([True, True, True, False, False])
        positions, fits, count = relative_positions(scores, eligible)
        self.assertEqual(count, 3)
        np.testing.assert_array_equal(positions, [1, 1, 3, 0, 0])
        np.testing.assert_allclose(fits[:3], [1, 1, 1 / 3])
        self.assertTrue(np.isnan(fits[3:]).all())
        scaled = relative_positions(scores * 1000, eligible)
        np.testing.assert_array_equal(positions, scaled[0]); np.testing.assert_allclose(fits, scaled[1])

    def test_coverage_precedes_policy_and_policies_diverge_on_tradeoff(self):
        balanced = lambda count, low, average: aggregate_key(count, low, average, 0, 1, 'balanced')
        overall = lambda count, low, average: aggregate_key(count, low, average, 0, 1, 'overall')
        self.assertLess(balanced(2, .1, .1), balanced(1, 1, 1))
        self.assertLess(overall(2, .1, .1), overall(1, 1, 1))
        self.assertLess(balanced(2, .6, .6), balanced(2, .4, .7))
        self.assertLess(overall(2, .4, .7), overall(2, .6, .6))

    def test_real_individual_scores_produce_distinct_group_orders(self):
        engine = fixture()
        people = [member('a', 'foodcom:1'), member('b', 'foodcom:2')]
        balanced = group_recommendations(engine, {'members': people})
        overall = group_recommendations(engine, {'members': people, 'priority': 'overall'})
        self.assertEqual([item['id'] for item in balanced['items'][:5]], [f'foodcom:{i}' for i in [5, 4, 3, 6, 7]])
        self.assertEqual([item['id'] for item in overall['items'][:5]], [f'foodcom:{i}' for i in [5, 3, 4, 6, 7]])
        self.assertEqual(balanced['items'][0]['members'][0]['evidence'], {'seedId': 'foodcom:1', 'sharedLikers': 9})
        self.assertEqual(balanced['items'][0]['members'][0]['position'], 2)
        self.assertTrue(all(item['basis'] == 'group' for item in balanced['items'][:5]))

    def test_member_order_and_repeated_likes_do_not_change_order(self):
        engine = fixture()
        people = [member('a', 'foodcom:1'), member('b', 'foodcom:2'), member('c', 'foodcom:3')]
        expected = None
        for perm in itertools.permutations(people):
            result = group_recommendations(engine, {'members': list(perm), 'priority': 'overall'})
            order = [item['id'] for item in result['items']]
            if expected is None: expected = order
            self.assertEqual(order, expected)
        people[0]['likes'] *= 2
        repeated = group_recommendations(engine, {'members': people, 'priority': 'overall'})
        self.assertEqual([item['id'] for item in repeated['items']], expected)
        self.assertEqual(repeated['members'][0]['supportedLikeCount'], 1)

    def test_blank_guest_is_unknown_without_a_fabricated_rank_or_dislike(self):
        engine = fixture()
        people = [member('a', 'foodcom:1'), member('blank')]
        result = group_recommendations(engine, {'members': people})
        self.assertEqual((result['evidenceMemberCount'], result['maxSupportCount']), (1, 1))
        self.assertTrue(all(item['members'][1] == {'memberId': 'blank', 'basis': 'unknown'} for item in result['items']))
        known = next(item for item in result['items'] if item['id'] == 'foodcom:1')
        self.assertEqual(known['members'][0], {'memberId': 'a', 'basis': 'known_like'})
        result2 = group_recommendations(engine, {'members': people, 'priority': 'overall'})
        self.assertEqual(result['items'], result2['items'])

    def test_all_unknown_is_popularity_and_explicit_passes_exclude_only_recipe(self):
        people = [member('a', passes=['foodcom:1']), member('b')]
        result = group_recommendations(fixture(), {'members': people})
        self.assertEqual(result['excludedCount'], 1)
        self.assertEqual(result['evidenceMemberCount'], 0)
        self.assertEqual(result['fallbackCount'], 6)
        self.assertEqual(result['items'][0]['id'], 'foodcom:2')
        self.assertTrue(all(item['basis'] == 'popularity' for item in result['items']))
        people[0]['passes'] = [f'foodcom:{i}' for i in range(1, 8)]
        self.assertEqual(group_recommendations(fixture(), {'members': people})['items'], [])

    def test_one_person_pass_overrides_another_person_known_like(self):
        result = group_recommendations(fixture(), {'members': [member('a', 'foodcom:1'), member('b', 'foodcom:2', ['foodcom:1'])]})
        self.assertNotIn('foodcom:1', [item['id'] for item in result['items']])
        self.assertEqual(result['excludedCount'], 1)

    def test_invalid_members_choices_priorities_and_extra_fields(self):
        good = [member('a'), member('b')]
        invalid = [None, [], {}, {'members': good, 'priority': []}, {'members': good, 'priority': 'x'},
          {'members': [member('a')]}, {'members': good * 3}, {'members': good, 'ingredients': ['rice']},
          {'members': [member('a'), member('a')]}, {'members': [{**member('a'), 'name': ''}, member('b')]},
          {'members': [{**member('a'), 'likes': ['foodcom:99']}, member('b')]},
          {'members': [member('a', 'foodcom:1', ['foodcom:1']), member('b')]},
          {'members': [{**member('a'), 'saved': []}, member('b')]}]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError): group_recommendations(fixture(), payload)

    def test_sparse_evidence_context_matches_original_dense_scoring(self):
        engine = fixture(); payload = {'likes': ['foodcom:1', 'foodcom:2']}
        dense = engine.choice_context(payload)
        sparse = engine.choice_context(payload, dense_evidence=False)
        np.testing.assert_array_equal(dense[2], sparse[2]); np.testing.assert_array_equal(dense[3], sparse[3].toarray())

    def test_saved_model_sources_and_actual_evidence_align(self):
        engine = load_engine()
        reviewed = json.loads((serving_tests.ROOT / 'src/data/recipes.json').read_text(encoding='utf-8'))
        people = [member('a', reviewed[0]['id']), member('b', reviewed[2]['id'])]
        result = group_recommendations(engine, {'members': people})
        self.assertEqual(result['catalogSize'], 5006); self.assertEqual(len(result['items']), 5006)
        self.assertGreater(result['maxSupportCount'], 0)
        for item in result['items']:
            for row in item['members']:
                if row['basis'] == 'co_like':
                    self.assertEqual(row['evidence']['sharedLikers'], engine.weights[
                        engine.index[row['evidence']['seedId']], engine.index[item['id']]])


class GroupHttpTests(unittest.TestCase):
    setUpClass = classmethod(serving_tests.DiscoverHttpTests.setUpClass.__func__)
    tearDownClass = classmethod(serving_tests.DiscoverHttpTests.tearDownClass.__func__)
    request = serving_tests.DiscoverHttpTests.request

    def test_local_server_cannot_claim_an_already_served_port(self):
        server = LocalModelServer(('127.0.0.1', 0), handler_for(fixture()))
        try:
            with self.assertRaises(OSError):
                LocalModelServer(('127.0.0.1', server.server_port), handler_for(fixture()))
        finally:
            server.server_close()

    def test_group_endpoint_validation_and_local_access(self):
        payload = json.dumps({'members': [member('a', 'foodcom:1'), member('b', 'foodcom:2')]})
        headers = {'Content-Type': 'application/json'}
        status, result, output = self.request('POST', '/api/mealmerge', payload, headers)
        self.assertEqual(status, 200); self.assertEqual(result['method'], 'group_rules+raw_co_like')
        self.assertEqual(output['Cache-Control'], 'no-store')
        self.assertEqual(self.request('POST', '/api/mealmerge', '{}', headers)[0], 400)
        self.assertEqual(self.request('POST', '/api/mealmerge', payload, {**headers, 'Origin': 'https://untrusted.example'})[0], 403)


if __name__ == '__main__': unittest.main()
