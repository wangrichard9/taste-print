import unittest
import numpy as np
from scipy.sparse import csr_matrix

from co_like import fit_relationships, score_likes


class CoLikeTests(unittest.TestCase):
    def fixture(self):
        return np.asarray([[1, 1, 0], [1, 1, 0], [1, 0, 1], [1, 0, 0]])

    def test_raw_counts_match_dense_reference_without_self_links(self):
        positive = self.fixture()
        expected = positive.T @ positive
        np.fill_diagonal(expected, 0)
        np.testing.assert_array_equal(fit_relationships(positive, 'raw').toarray(), expected)

    def test_normalization_and_shrinkage_match_formula(self):
        weights = fit_relationships(self.fixture()).toarray()
        self.assertAlmostEqual(weights[0, 1], 2 / np.sqrt(4 * 2) * 2 / 12)
        self.assertAlmostEqual(weights[0, 2], 1 / np.sqrt(4) / 11)
        np.testing.assert_array_equal(np.diag(weights), [0, 0, 0])
        np.testing.assert_array_equal(weights, weights.T)

    def test_normalization_can_reorder_equal_support_with_different_popularity(self):
        positive = np.asarray([[1, 1, 1], [0, 1, 0], [0, 1, 0]])
        raw = score_likes(fit_relationships(positive, 'raw'), [[0]])[0]
        normalized = score_likes(fit_relationships(positive), [[0]])[0]
        self.assertEqual(raw[1], raw[2])
        self.assertGreater(normalized[2], normalized[1])

    def test_duplicate_seed_likes_and_training_values_are_binary(self):
        relationships = fit_relationships(self.fixture() * 3)
        np.testing.assert_array_equal(relationships.toarray(), fit_relationships(self.fixture()).toarray())
        np.testing.assert_array_equal(score_likes(relationships, [[0, 0, 1]]), score_likes(relationships, [[0, 1]]))

    def test_zero_degree_items_and_missing_pairs_stay_zero(self):
        relationships = fit_relationships([[1, 1, 0], [1, 0, 0]])
        np.testing.assert_array_equal(relationships.toarray()[2], [0, 0, 0])
        np.testing.assert_array_equal(score_likes(relationships, [[2]]), [[0, 0, 0]])

    def test_mean_seed_scores_and_no_seed_self_link(self):
        relationships = fit_relationships(self.fixture(), 'raw')
        np.testing.assert_array_equal(score_likes(relationships, [[1, 2]]), [[1.5, 0, 0]])

    def test_invalid_fit_inputs_fail(self):
        for positive in ([[0, 0]], [[np.nan]], [[-1, 1]]):
            with self.assertRaises(ValueError):
                fit_relationships(positive)
        for kwargs in ({'mode': 'unknown'}, {'shrinkage': -1}, {'shrinkage': np.nan}):
            with self.assertRaises(ValueError):
                fit_relationships([[1]], **kwargs)

    def test_invalid_score_inputs_fail(self):
        for profiles in ([], [[]], [[-1]], [[3]], [[.5]]):
            with self.assertRaises(ValueError):
                score_likes(csr_matrix(np.eye(3)), profiles)
        for weights in ([[1, 0]], [[np.nan]], [[-1]]):
            with self.assertRaises(ValueError):
                score_likes(weights, [[0]])


if __name__ == '__main__':
    unittest.main()
