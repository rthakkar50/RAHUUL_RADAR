import unittest
from api.main import _is_valid_complete_cache

class TestSprint196FCacheConsistency(unittest.TestCase):
    def test_complete_cache_overwrites_valid(self):
        existing = {"total_scanned": 195, "qualified_results": [{"symbol": "RELIANCE.NS"}]}
        new_data = {"total_scanned": 195, "qualified_results": [{"symbol": "TCS.NS"}]}
        self.assertTrue(_is_valid_complete_cache(new_data, existing))

    def test_partial_cache_rejected_when_valid_exists(self):
        existing = {"total_scanned": 195, "qualified_results": [{"symbol": "RELIANCE.NS"}]}
        partial_data = {"total_scanned": 28, "qualified_results": []}
        self.assertFalse(_is_valid_complete_cache(partial_data, existing))

    def test_empty_cache_accepts_initial_scan(self):
        existing = None
        initial_scan = {"total_scanned": 195, "qualified_results": [{"symbol": "RELIANCE.NS"}]}
        self.assertTrue(_is_valid_complete_cache(initial_scan, existing))

if __name__ == "__main__":
    unittest.main()
