import unittest
from audit_foodcom import canonical_id, duration_minutes, has_text, usable_list, probe_photo


class DataAuditTests(unittest.TestCase):
    def test_recipe_ids_do_not_silently_truncate(self):
        self.assertEqual(canonical_id(38.0), 38)
        for value in (None, True, 38.5, float("nan"), float("inf"), 0, -1, "bad"):
            self.assertIsNone(canonical_id(value))

    def test_lists_must_contain_nonblank_text(self):
        self.assertTrue(usable_list(["salt", "pepper"]))
        for value in (None, [], [""], ["salt", None], [" "]):
            self.assertFalse(usable_list(value))
        self.assertFalse(has_text(0))

    def test_source_iso_durations(self):
        self.assertEqual(duration_minutes("PT1H30M"), 90)
        self.assertEqual(duration_minutes("PT30S"), 0.5)
        self.assertEqual(duration_minutes("PT24H45M"), 1485)
        for value in (None, "PT", "unknown", "90 minutes"):
            self.assertIsNone(duration_minutes(value))

    def test_photo_probe_rejects_untrusted_hosts_without_fetching(self):
        for url in ("http://img.sndimg.com/a.jpg", "https://127.0.0.1/a.jpg", "https://example.com/a.jpg"):
            result = probe_photo({"RecipeId": 38, "Name": "Example", "Images": [url]})
            self.assertFalse(result["ok"])
            self.assertEqual(result["reason"], "not_allowlisted")


if __name__ == "__main__":
    unittest.main()
