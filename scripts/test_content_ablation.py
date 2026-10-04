import unittest

import numpy as np

from content_ablation import ingredient_text, profile_scores, shuffled_profile_indices, score_auc, status_counts
from recommendation import liked_profile, rank


class ContentAblationTests(unittest.TestCase):
    def test_ingredient_variant_removes_all_other_fields(self):
        recipe = {'name': 'Secret title', 'ingredients': ['rice', 'salt &amp; pepper'],
            'category': 'Lunch', 'keywords': ['Easy'], 'training_like_count': 999}
        self.assertEqual(ingredient_text(recipe), 'Ingredients: rice, salt & pepper.')

    def test_centroid_reproduces_existing_profile(self):
        vectors = np.eye(3, dtype=np.float32)
        seeds = np.asarray([[0, 1]])
        scores = profile_scores(vectors, seeds, 'centroid')[0]
        np.testing.assert_allclose(scores, vectors @ liked_profile(vectors, [0, 1]), atol=1e-7)

    def test_closest_does_not_force_compromise_between_interests(self):
        vectors = np.asarray([[1, 0], [0, 1], [1 / np.sqrt(2), 1 / np.sqrt(2)],
                              [np.sqrt(.99), .1]], dtype=np.float32)
        seeds = np.asarray([[0, 1]])
        ids = [10, 20, 30, 40]
        average = rank(profile_scores(vectors, seeds, 'centroid')[0], ids, [10, 20], 1)
        closest = rank(profile_scores(vectors, seeds, 'closest')[0], ids, [10, 20], 1)
        self.assertEqual(ids[average[0]], 30)
        self.assertEqual(ids[closest[0]], 40)

    def test_top_two_is_mean_of_two_greatest_seed_similarities(self):
        vectors = np.eye(3, dtype=np.float32)
        scores = profile_scores(vectors, np.asarray([[0, 1, 2]]), 'top_two')[0]
        np.testing.assert_allclose(scores, [.5, .5, .5])

    def test_mean_of_all_seed_cosines_is_proportional_to_centroid(self):
        vectors = np.asarray([[1, 0], [.6, .8], [0, 1]], dtype=np.float32)
        mean_cosines = (vectors[[0, 1]] @ vectors.T).mean(axis=0)
        centroid = profile_scores(vectors, np.asarray([[0, 1]]), 'centroid')[0]
        np.testing.assert_allclose(mean_cosines / np.linalg.norm(vectors[[0, 1]].mean(axis=0)), centroid, atol=1e-7)

    def test_shuffling_is_deterministic_derangement(self):
        first = shuffled_profile_indices(300, 20260930)
        np.testing.assert_array_equal(first, shuffled_profile_indices(300, 20260930))
        self.assertEqual(set(first.tolist()), set(range(300)))
        self.assertTrue(np.all(first != np.arange(300)))
        with self.assertRaises(ValueError):
            shuffled_profile_indices(1, 20260930)

    def test_auc_uses_observed_high_and_lower_ratings_with_half_credit_ties(self):
        self.assertEqual(score_auc([.8, .5], [.2, .5]), .875)
        self.assertEqual(score_auc([.2], [.8]), 0)
        self.assertEqual(score_auc([.5], [.5]), .5)
        self.assertIsNone(score_auc([.5], []))

    def test_missing_rating_is_unknown_not_disliked(self):
        result = status_counts([1, 2, 3], {1: 5, 2: 2})
        self.assertEqual(result, {'known_high': 1, 'known_lower': 1, 'unknown': 1})

    def test_invalid_scoring_inputs_fail_instead_of_silent_reindexing(self):
        vectors = np.eye(3, dtype=np.float32)
        for seeds, mode in (([[0, 3]], 'centroid'), ([[0, 0]], 'closest'), ([[0]], 'top_two'), ([[0, 1]], 'wrong')):
            with self.assertRaises(ValueError):
                profile_scores(vectors, np.asarray(seeds), mode)


if __name__ == '__main__':
    unittest.main()
