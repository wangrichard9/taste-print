import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.sparse import csr_matrix

import run_final_evaluation as final
from discover_service import DiscoverEngine
from recommendation import rank


class FinalEvaluationTests(unittest.TestCase):
    def profile(self):
        return {'user_key': f'{90:064x}', 'likes': list(range(1, 7)),
                'seen': list(range(1, 8)), 'relevant': [8], 'seed_cutoff_utc': '2001-01-01'}

    def test_profile_validation_accepts_fixed_test_partition(self):
        final.validate_profiles([self.profile()], set(range(1, 21)), set(), expected_count=1)

    def test_invalid_seeds_targets_partition_and_overlap_fail(self):
        changes = [{'likes': [1, 2]}, {'likes': [1] * 6}, {'relevant': [1]},
                   {'seen': [1, 2, 3, 4, 5]}, {'relevant': []}, {'relevant': [999]},
                   {'user_key': f'{80:064x}'}, {'user_key': 'not-a-digest'},
                   {'seed_cutoff_utc': None}, {'likes': [True, 2, 3, 4, 5, 6]}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                final.validate_profiles([{**self.profile(), **change}], set(range(1, 21)), set(), 1)
        with self.assertRaises(ValueError):
            final.validate_profiles([self.profile()], set(range(1, 21)), {self.profile()['user_key']}, 1)
        with self.assertRaises(ValueError):
            final.validate_profiles([self.profile(), self.profile()], set(range(1, 21)), set(), 2)
        with self.assertRaises(ValueError):
            final.validate_profiles([], set(range(1, 21)), set(), 1)

    def test_score_independence_from_future_labels(self):
        weights = csr_matrix(np.ones((8, 8)) - np.eye(8))
        catalog = [{'id': i} for i in range(1, 9)]
        profile = self.profile()
        changed = {**profile, 'relevant': [999], 'future': [{'rating': 1}]}
        np.testing.assert_array_equal(final.scores_for(catalog, [profile], weights),
                                      final.scores_for(catalog, [changed], weights))

    def test_primary_and_serving_keep_positive_ties_but_differ_for_zero_fallback(self):
        catalog = [{'id': i, 'training_like_count': count}
                   for i, count in [(1, 1), (2, 1), (3, 100), (4, 1000)]]
        weights = csr_matrix([[0, 2, 2, 0], [2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0]])
        engine = DiscoverEngine(catalog, weights, [{'id': f'foodcom:{i}', 'ingredients': []} for i in range(1, 5)])
        values = final.scores_for(catalog, [{'likes': [1]}], weights)[0]
        self.assertEqual([catalog[i]['id'] for i in rank(values, engine.ids, [1], 3)], [2, 3, 4])
        self.assertEqual([row['id'] for row in engine.recommend({'likes': ['foodcom:1']})['items']],
                         ['foodcom:2', 'foodcom:3', 'foodcom:4'])
        # No-connection primary uses IDs; serving uses fitting popularity.
        primary = [catalog[i]['id'] for i in rank(np.zeros(4), engine.ids, [1], 3)]
        served = engine.recommend({'passes': ['foodcom:1']})['items']
        self.assertEqual(primary, [2, 3, 4])
        self.assertEqual([row['id'] for row in served], ['foodcom:4', 'foodcom:3', 'foodcom:2'])
        self.assertTrue(all(row['basis'] == 'popularity' for row in served))

    def test_serving_excludes_earlier_seen_without_inventing_negative_seed_scores(self):
        catalog = [{'id': i, 'training_like_count': i} for i in range(1, 5)]
        weights = csr_matrix(np.ones((4, 4)) - np.eye(4))
        engine = DiscoverEngine(catalog, weights, [{'id': f'foodcom:{i}', 'ingredients': []} for i in range(1, 5)])
        result = engine.recommend({'likes': ['foodcom:1'], 'passes': ['foodcom:2']})
        self.assertEqual([row['id'] for row in result['items']], ['foodcom:3', 'foodcom:4'])
        self.assertEqual(result['items'][0]['evidence']['sharedLikers'], 1)

    def test_aggregate_metric_arithmetic_and_unknowns(self):
        catalog = [{'id': i, 'training_like_count': 1} for i in range(20)]
        result = final.summarize_rankings([list(range(10))], catalog,
            [{'seen': [19], 'relevant': [0, 12]}],
            [{'future': [{'recipe_id': 0, 'rating': 5}, {'recipe_id': 1, 'rating': 2}]}])
        self.assertEqual(result['metrics']['precision@10'], .1)
        self.assertEqual(result['metrics']['recall@10'], .5)
        self.assertAlmostEqual(result['metrics']['ndcg@10'], 1 / (1 + 1 / np.log2(3)))
        self.assertEqual(result['metrics']['people_with_hit'], 1)
        self.assertEqual(result['top10_rating_status'], {'known_high': 1, 'known_lower': 1, 'unknown': 8})
        self.assertEqual(result['unique_recommended_recipes'], 10)
        self.assertEqual(result['recovered_like_slots'], 1)

    def test_duplicate_seen_unknown_and_short_rankings_rejected(self):
        catalog = [{'id': i, 'training_like_count': 1} for i in range(20)]
        for ranked in ([0] * 10, list(range(9)), list(range(9)) + [19], list(range(9)) + [100]):
            with self.subTest(ranked=ranked), self.assertRaises(ValueError):
                final.summarize_rankings([ranked], catalog, [{'seen': [19], 'relevant': [0]}], [{'future': []}])
        with self.assertRaises(ValueError):
            final.summarize_rankings([], catalog, [{'seen': [], 'relevant': [0]}], [{'future': []}])

    def test_fixed_derangement_has_no_self_donors(self):
        first = final.shuffled_profile_indices(300, final.SEED)
        np.testing.assert_array_equal(first, final.shuffled_profile_indices(300, final.SEED))
        self.assertEqual(sorted(first.tolist()), list(range(300)))
        self.assertTrue(np.all(first != np.arange(300)))

    def test_paired_bootstrap_is_reproducible_with_correct_sign(self):
        result = final.comparison_interval([0, .1, .2], [.2, .2, .3])
        self.assertEqual(result, final.comparison_interval([0, .1, .2], [.2, .2, .3]))
        self.assertAlmostEqual(result['mean_ndcg_difference'], .4 / 3)
        self.assertEqual(result['better_people'], 3)
        self.assertGreater(result['paired_bootstrap_95_percent_interval'][0], 0)
        self.assertEqual(final.comparison_interval([0, 1], [0, 1])['tied_people'], 2)

    def test_write_once_refuses_to_replace_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'receipt.json'
            final.write_once(path, {'first': True})
            with self.assertRaises(FileExistsError):
                final.write_once(path, {'first': False})
            self.assertEqual(final.read_json(path), {'first': True})

    def test_prepare_does_not_deserialize_test_and_refuses_reregistration(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(final, 'OUT', Path(directory)), \
                patch.object(final, 'load_protocol'), patch.object(final, 'load_configuration'), \
                patch.object(final, 'previous_hashes', return_value={'test.json': 'hash'}), \
                patch.object(final, 'implementation_hashes', return_value={}), patch.object(final, 'sha256', return_value='hash'), \
                patch.object(final, 'read_json', return_value={'provisional_behavioral_nominee': 'direct/raw', 'test_scored': False}) as reader:
            final.prepare()
            self.assertEqual(reader.call_count, 1)
            self.assertEqual(reader.call_args.args[0].name, 'results.json')
            with self.assertRaises(FileExistsError):
                final.prepare()

    def test_started_marker_blocks_repeated_test_open(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(final, 'OUT', Path(directory)), \
                patch.object(final, 'registration', return_value={}), patch.object(final, 'read_json') as reader:
            final.write_once(Path(directory) / 'test-started.json', {})
            with self.assertRaises(ValueError):
                final.evaluate()
            reader.assert_not_called()

    def test_registration_rejects_changed_code_inputs_or_choices(self):
        fixture = {'experiment': final.EXPERIMENT, 'choices': copy.deepcopy(final.CHOICES),
                   'previous_artifact_sha256': {'frozen': 'hash'}, 'implementation_sha256': {'code': 'hash'},
                   'protocol_document_sha256': 'hash', 'test_opened_at_registration': False}
        with patch.object(final, 'read_json', return_value=fixture), \
                patch.object(final, 'previous_hashes', return_value={'frozen': 'hash'}), \
                patch.object(final, 'implementation_hashes', return_value={'code': 'hash'}), \
                patch.object(final, 'sha256', return_value='hash'):
            self.assertEqual(final.registration(), fixture)
            for key in ('choices', 'previous_artifact_sha256', 'implementation_sha256', 'protocol_document_sha256'):
                changed = {**fixture, key: 'changed'}
                with patch.object(final, 'read_json', return_value=changed), self.assertRaises(ValueError):
                    final.registration()


if __name__ == '__main__':
    unittest.main()
