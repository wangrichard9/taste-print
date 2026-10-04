import unittest

import numpy as np
from scipy.sparse import csr_matrix

from collaborative import fit, fold_in, objective, blend_scores
from recommendation import rank


class CollaborativeTests(unittest.TestCase):
    def test_fold_in_matches_dense_weighted_least_squares(self):
        items = np.asarray([[1, .2], [.1, .8], [.4, .5], [.3, .7]])
        positive = np.asarray([1., 0., 1., 0.])
        confidence = 1 + 20 * positive
        expected = np.linalg.solve(items.T @ (confidence[:, None] * items) + np.eye(2), items.T @ (confidence * positive))
        np.testing.assert_allclose(fold_in(items, [[0, 2]])[0], expected, atol=1e-12)

    def test_objective_matches_full_dense_sum(self):
        positive = np.asarray([[1., 0., 1.], [0., 1., 0.]])
        users = np.asarray([[.2, .5], [.3, .1]])
        items = np.asarray([[.1, .4], [.5, .2], [.2, .7]])
        expected = np.sum((1 + 20 * positive) * (positive - users @ items.T)**2) + np.sum(users**2) + np.sum(items**2)
        self.assertAlmostEqual(objective(csr_matrix(positive), users, items, 20, 1), expected)

    def test_fit_is_reproducible_and_objective_decreases(self):
        positive = csr_matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]])
        first = fit(positive, dimensions=2, iterations=5)
        second = fit(positive, dimensions=2, iterations=5)
        np.testing.assert_array_equal(first.items, second.items)
        np.testing.assert_array_equal(first.users, second.users)
        self.assertTrue(np.all(np.diff(first.objectives) <= 1e-8))
        self.assertLess(first.objectives[-1], first.objectives[0])

    def test_behavioral_groups_recover_unseen_related_items(self):
        # No ingredient, title, cuisine, or text input: relationships come from likes.
        positive = np.asarray([[1, 1, 1, 0, 0, 0], [0, 0, 0, 1, 1, 1]])
        model = fit(csr_matrix(np.tile(positive, (8, 1))), dimensions=2, iterations=12)
        scores = fold_in(model.items, [[0, 1], [3, 4]]) @ model.items.T
        self.assertEqual(rank(scores[0], list(range(6)), [0, 1], 1).tolist(), [2])
        self.assertEqual(rank(scores[1], list(range(6)), [3, 4], 1).tolist(), [5])

    def test_duplicate_likes_do_not_increase_confidence(self):
        items = np.eye(3)
        np.testing.assert_array_equal(fold_in(items, [[0, 0, 1]]), fold_in(items, [[0, 1]]))

    def test_empty_unknown_and_noninteger_seed_indices_fail(self):
        for profiles in ([], [[]], [[-1]], [[3]], [[.5]]):
            with self.subTest(profiles=profiles), self.assertRaises(ValueError):
                fold_in(np.eye(3), profiles)
        with self.assertRaises(ValueError):
            fold_in([[np.nan]], [[0]])

    def test_invalid_training_data_and_parameters_fail(self):
        for values in ([[0, 0]], [[-1, 1]], [[np.nan, 1]]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                fit(csr_matrix(values))
        for kwargs in ({'dimensions': 0}, {'iterations': 0}, {'alpha': -1}, {'regularization': 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                fit(csr_matrix([[1, 0]]), **kwargs)

    def test_isolated_unrated_item_has_zero_factor(self):
        model = fit(csr_matrix([[1, 0], [1, 0]]), dimensions=2, iterations=2)
        np.testing.assert_array_equal(model.items[1], [0, 0])

    def test_blend_endpoints_preserve_exact_scores(self):
        content, cf = [3, 1, 2], [.1, .4, .2]
        np.testing.assert_array_equal(blend_scores(content, cf, 0), content)
        np.testing.assert_array_equal(blend_scores(content, cf, 1), cf)

    def test_blend_ties_and_seen_items_do_not_change_eligible_percentiles(self):
        result = blend_scores([100, 1, 1, 3], [-100, 1, 3, 2], .5, [False, True, True, True])
        np.testing.assert_allclose(result, [0, (1.5 + 1)/6, (1.5 + 3)/6, (3 + 2)/6])
        ranked = rank(result, [10, 20, 30, 40], [10], 3)
        self.assertNotIn(0, ranked)

    def test_blend_input_validation(self):
        for content, cf, weight, eligible in (([1], [1, 2], .5, None), ([np.nan], [1], .5, None),
                ([1], [2], -1, None), ([1], [2], 2, None), ([1], [2], .5, [False])):
            with self.assertRaises(ValueError):
                blend_scores(content, cf, weight, eligible)


if __name__ == '__main__':
    unittest.main()
