import json
import unittest

from run_content_ablation import OUT, load_frozen, ingredient_embeddings


@unittest.skipUnless((OUT / 'protocol.json').exists(), 'Register local ML 02 first')
class ContentAblationArtifactTests(unittest.TestCase):
    def test_registered_inputs_match_original_and_leave_test_unscored(self):
        configuration, _, catalog, profiles = load_frozen()
        self.assertEqual(configuration['profile_modes'], ['centroid', 'closest', 'top_two'])
        self.assertEqual(configuration['text_modes'], ['full', 'ingredients'])
        self.assertFalse(configuration['test_scored'])
        self.assertEqual(len(catalog), 5006)
        self.assertEqual(len(profiles), 300)

    @unittest.skipUnless((OUT / 'ingredients.json').exists(), 'Encode ingredient vectors first')
    def test_ingredient_vectors_keep_same_rows_and_model(self):
        configuration, _, catalog, _ = load_frozen()
        vectors = ingredient_embeddings(configuration, catalog)
        self.assertEqual(vectors.shape, (5006, 384))
        metadata = json.loads((OUT / 'ingredients.json').read_text(encoding='utf-8'))
        self.assertTrue(metadata['original_alignment_check_passed'])
        self.assertEqual(len(metadata['reencoded_full_recipe_ids']), 8)
        self.assertFalse(metadata['fine_tuned'])

    @unittest.skipUnless((OUT / 'results.json').exists(), 'Evaluate registered variants first')
    def test_complete_grid_baseline_preservation_and_label_accounting(self):
        result = json.loads((OUT / 'results.json').read_text(encoding='utf-8'))
        self.assertFalse(result['test_scored'])
        self.assertTrue(result['original_metrics_reproduced'])
        self.assertTrue(result['baseline_hashes_unchanged'])
        self.assertEqual(len(result['metrics_and_diagnostics']), 8)
        for method in result['metrics_and_diagnostics'].values():
            self.assertEqual(sum(method['top10_rating_status'].values()), 3000)
            self.assertGreaterEqual(method['metrics']['ndcg@10'], 0)
            self.assertLessEqual(method['metrics']['ndcg@10'], 1)
        source = result['source_history_check']
        self.assertTrue(source['all_300_profiles_reconstructed'])
        self.assertEqual(source['future_high_records_in_catalog'], 6650)
        self.assertGreaterEqual(source['future_high_records_all_content'], 6650)


if __name__ == '__main__':
    unittest.main()
