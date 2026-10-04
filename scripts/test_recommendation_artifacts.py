"""Integration checks against generated local ML artifacts; skipped on clean clone."""
from collections import Counter
import json
import unittest

import pyarrow.parquet as pq

from prepare_recommendation_data import OUT
from run_recommendation_experiment import load_protocol, load_embeddings


@unittest.skipUnless((OUT / 'protocol.json').exists(), 'Prepare local ML 01 artifacts first')
class RecommendationArtifactTests(unittest.TestCase):
    def test_source_and_artifact_hashes_and_user_isolation(self):
        protocol, catalog = load_protocol()
        validation = json.loads((OUT / 'validation.json').read_text(encoding='utf-8'))
        test = json.loads((OUT / 'test.json').read_text(encoding='utf-8'))
        validation_users = {profile['user_key'] for profile in validation}
        test_users = {profile['user_key'] for profile in test}
        self.assertFalse(validation_users & test_users)
        counts = Counter()
        training_users = set()
        for batch in pq.ParquetFile(OUT / 'train.parquet').iter_batches():
            for row in batch.to_pylist():
                training_users.add(row['user_key'])
                if row['rating'] >= 4:
                    counts[row['recipe_id']] += 1
        self.assertFalse(training_users & (validation_users | test_users))
        for recipe in catalog:
            self.assertEqual(recipe['training_like_count'], counts[recipe['id']])
        self.assertEqual(protocol['test_status'], 'reserved, not scored in ML 01')

    def test_profiles_are_in_catalog_with_six_known_likes_and_unseen_targets(self):
        _, catalog = load_protocol()
        ids = {recipe['id'] for recipe in catalog}
        for partition in ('validation', 'test'):
            profiles = json.loads((OUT / f'{partition}.json').read_text(encoding='utf-8'))
            self.assertGreater(len(profiles), 0)
            for profile in profiles:
                self.assertEqual(len(set(profile['likes'])), 6)
                self.assertTrue(set(profile['likes']) <= set(profile['seen']))
                self.assertTrue(set(profile['seen']) <= ids)
                self.assertTrue(set(profile['relevant']) <= ids)
                self.assertFalse(set(profile['seen']) & set(profile['relevant']))
                self.assertGreater(len(profile['relevant']), 0)

    @unittest.skipUnless((OUT / 'embeddings.json').exists(), 'Encode local recipe artifacts first')
    def test_embedding_provenance_and_normalization(self):
        protocol, catalog = load_protocol()
        vectors, metadata = load_embeddings(protocol, catalog)
        self.assertEqual(vectors.shape, (len(catalog), 384))
        self.assertFalse(metadata['fine_tuned_by_tasteprint'])


if __name__ == '__main__':
    unittest.main()
