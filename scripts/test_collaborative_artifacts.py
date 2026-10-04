import json
import unittest

import numpy as np

from run_collaborative_experiment import OUT, inputs, training_matrix, load_configuration, load_model, matrices
from recommendation import rank


@unittest.skipUnless((OUT / 'model.json').exists(), 'Train local ML 03 first')
class CollaborativeArtifactTests(unittest.TestCase):
    def test_fitting_people_and_catalog_align_with_registration(self):
        configuration = load_configuration()
        _, catalog, profiles, _, _ = inputs()
        matrix, stats = training_matrix(catalog, profiles)
        self.assertEqual(stats, configuration['training_data'])
        self.assertEqual(matrix.shape, (86845, 5006))
        self.assertFalse(configuration['test_scored'])

    def test_factors_and_new_user_inference_exclude_future_labels(self):
        configuration = load_configuration()
        _, catalog, profiles, embeddings, _ = inputs()
        items, receipt = load_model(configuration, catalog)
        self.assertTrue(receipt['trained_by_tasteprint'])
        scores = matrices(catalog, profiles, embeddings, items)
        changed = [{**profile, 'relevant': [-123], 'seed_cutoff_utc': 'not a feature'} for profile in profiles]
        other = matrices(catalog, changed, embeddings, items)
        ids = [row['id'] for row in catalog]
        for name in scores:
            np.testing.assert_array_equal(scores[name], other[name])
            for values, profile in zip(scores[name], profiles):
                ranked = [ids[i] for i in rank(values, ids, profile['seen'], 10)]
                self.assertFalse(set(ranked) & set(profile['seen']))

    @unittest.skipUnless((OUT / 'results.json').exists(), 'Evaluate validation first')
    def test_results_preserve_baselines_and_account_for_known_and_unknown(self):
        results = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
        self.assertFalse(results['test_scored'])
        self.assertTrue(results['original_metrics_reproduced'])
        self.assertTrue(results['baseline_hashes_unchanged'])
        self.assertEqual(len(results['metrics_and_diagnostics']), 7)
        for result in results['metrics_and_diagnostics'].values():
            self.assertEqual(sum(result['top10_rating_status'].values()), 3000)
            self.assertTrue(0 <= result['metrics']['ndcg@10'] <= 1)


if __name__ == '__main__':
    unittest.main()
