import math
import unittest

import numpy as np

from prepare_recommendation_data import make_profile, user_partition, user_hash
from recommendation import recipe_text, content_signature, liked_profile, rank, recommend, ranking_metrics


class RecommendationTests(unittest.TestCase):
    def test_text_uses_source_food_not_ratings_or_people(self):
        recipe = {'name': 'Rice &amp; beans', 'ingredients': ['rice', 'beans'],
            'category': 'Lunch', 'keywords': ['Easy'], 'rating': 5, 'review': 'secret', 'author': 'someone'}
        self.assertEqual(recipe_text(recipe), 'Recipe: Rice & beans. Ingredients: rice, beans. Category: Lunch. Tags: Easy.')

    def test_exact_identity_ignores_case_spacing_and_ingredient_order(self):
        a = {'name': 'Rice & beans', 'ingredients': ['rice', 'beans']}
        b = {'name': ' RICE &amp; BEANS ', 'ingredients': ['beans', 'rice']}
        self.assertEqual(content_signature(a), content_signature(b))

    def test_partition_is_stable_and_has_disjoint_buckets(self):
        groups = {name: set() for name in ('train', 'validation', 'test')}
        for user_id in range(1, 1000):
            groups[user_partition(user_id)].add(user_id)
        self.assertEqual(sum(map(len, groups.values())), 999)
        self.assertTrue(all(groups.values()))
        self.assertFalse(groups['train'] & groups['validation'])
        self.assertFalse(groups['validation'] & groups['test'])
        self.assertEqual(user_hash(123), user_hash(123))

    def history(self, times=None):
        return [{'recipe_id': i + 1, 'rating': 5, 'timestamp': str(time), 'review_id': i + 100}
                for i, time in enumerate(times or range(1, 9))]

    def test_six_likes_are_earlier_than_every_target(self):
        history = self.history()
        history.append({'recipe_id': 9, 'rating': 1, 'timestamp': '2', 'review_id': 109})
        profile = make_profile(list(reversed(history)))
        self.assertEqual(profile['likes'], [1, 2, 3, 4, 5, 6])
        self.assertEqual(profile['seen'], [1, 2, 3, 4, 5, 6, 9])
        self.assertEqual(profile['relevant'], [7, 8])
        self.assertFalse(set(profile['seen']) & set(profile['relevant']))

    def test_same_timestamp_is_not_future_evidence(self):
        profile = make_profile(self.history([1, 2, 3, 4, 5, 6, 6, 7]))
        self.assertIn(7, profile['seen'])
        self.assertEqual(profile['relevant'], [8])
        self.assertIsNone(make_profile(self.history([1, 2, 3, 4, 5, 6, 6, 6])))

    def test_not_enough_likes_is_not_an_evaluation_profile(self):
        self.assertIsNone(make_profile(self.history()[:6]))
        history = self.history()
        for row in history:
            row['rating'] = 3
        self.assertIsNone(make_profile(history))

    def test_profile_normalizes_and_deduplicates_likes(self):
        vectors = np.eye(3, dtype=np.float32)
        np.testing.assert_allclose(liked_profile(vectors, [0, 0, 1]), [1 / math.sqrt(2), 1 / math.sqrt(2), 0])
        for seeds in ([], [-1], [3]):
            with self.assertRaises(ValueError):
                liked_profile(vectors, seeds)

    def test_ranking_excludes_seen_and_has_deterministic_ties(self):
        self.assertEqual(rank([.8, .8, 1, .1], [20, 10, 30, 40], [30], 2).tolist(), [1, 0])

    def test_invalid_rank_inputs_fail_explicitly(self):
        for scores, ids, k in (([1], [1, 2], 10), ([1, 2], [1, 1], 10), ([float('nan')], [1], 10), ([1], [1], 0)):
            with self.assertRaises(ValueError):
                rank(scores, ids, k=k)

    def test_recommendations_are_not_seed_likes(self):
        vectors = np.asarray([[1, 0], [.8, .6], [0, 1]], dtype=np.float32)
        result = recommend(vectors, [10, 20, 30], [10], k=2)
        self.assertEqual([item[0] for item in result], [20, 30])
        self.assertAlmostEqual(result[0][1], .8)
        with self.assertRaises(ValueError):
            recommend(vectors, [10, 20, 30], [99])

    def test_metrics_have_known_results(self):
        metrics = ranking_metrics([1, 2, 3], [1, 3], k=3)
        self.assertAlmostEqual(metrics['precision'], 2 / 3)
        self.assertEqual(metrics['recall'], 1)
        self.assertAlmostEqual(metrics['ndcg'], 1.5 / (1 + 1 / math.log2(3)))
        self.assertEqual(metrics['hit_rate'], 1)
        self.assertEqual(ranking_metrics([4, 5, 6], [1, 3], 3)['ndcg'], 0)
        with self.assertRaises(ValueError):
            ranking_metrics([1, 1], [1])


if __name__ == '__main__':
    unittest.main()
