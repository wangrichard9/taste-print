import json
import unittest

import numpy as np

from recommendation import rank
from run_behavior_comparison import OUT, load_configuration, inputs, load_models, score_models, old_hashes


@unittest.skipUnless((OUT / 'models.json').exists(), 'Fit registered local ML 04 first')
class BehaviorComparisonArtifactTests(unittest.TestCase):
    def test_registered_methods_and_prior_artifacts_are_preserved(self):
        configuration = load_configuration()
        self.assertEqual(configuration['old_artifact_sha256'], old_hashes())
        self.assertEqual(len(configuration['new_als']), 3)
        self.assertEqual(configuration['direct_modes'], ['raw', 'cosine_shrunk'])
        self.assertFalse(configuration['test_scored'])
        _, catalog, _, _, _ = inputs()
        loaded, receipt = load_models(configuration, catalog)
        self.assertEqual(len(loaded), 5)
        for name, weights in loaded.items():
            if name.startswith('direct/'):
                np.testing.assert_array_equal(weights.diagonal(), np.zeros(len(catalog)))
                if name == 'direct/cosine_shrunk':
                    self.assertLessEqual(weights.data.max(), 1)
            else:
                self.assertEqual(weights.shape, (5006, 32))
        self.assertFalse(receipt['test_scored'])

    def test_all_inference_is_independent_of_future_labels_and_ranks_exclude_seen(self):
        configuration = load_configuration()
        _, catalog, profiles, embeddings, _ = inputs()
        loaded, _ = load_models(configuration, catalog)
        scores = score_models(catalog, profiles, embeddings, loaded)
        altered = [{**profile, 'relevant': [-99], 'seed_cutoff_utc': 'not a feature'} for profile in profiles]
        changed = score_models(catalog, altered, embeddings, loaded)
        ids = [row['id'] for row in catalog]
        self.assertEqual(len(scores), 8)
        for name in scores:
            np.testing.assert_array_equal(scores[name], changed[name])
            for values, profile in zip(scores[name], profiles):
                output = [ids[i] for i in rank(values, ids, profile['seen'], 10)]
                self.assertFalse(set(output) & set(profile['seen']))

    @unittest.skipUnless((OUT / 'results.json').exists(), 'Evaluate registered comparison first')
    def test_grid_controls_and_label_accounting(self):
        result = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
        self.assertFalse(result['test_scored'])
        self.assertTrue(result['original_metrics_reproduced'])
        self.assertTrue(result['old_artifacts_unchanged'])
        self.assertEqual(len(result['metrics_and_diagnostics']), 8)
        self.assertEqual(len(result['shuffled_controls']), 6)
        self.assertEqual(len(result['correct_minus_shuffled_ndcg']), 6)
        for method in list(result['metrics_and_diagnostics'].values()) + list(result['shuffled_controls'].values()):
            self.assertEqual(sum(method['top10_rating_status'].values()), 3000)
            self.assertTrue(0 <= method['metrics']['ndcg@10'] <= 1)
        nominee = result['provisional_behavioral_nominee']
        behavioral = result['correct_minus_shuffled_ndcg']
        self.assertEqual(result['metrics_and_diagnostics'][nominee]['metrics']['ndcg@10'],
            max(result['metrics_and_diagnostics'][name]['metrics']['ndcg@10'] for name in behavioral))


if __name__ == '__main__':
    unittest.main()
