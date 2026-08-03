import unittest
import asyncio
import time
import json
from api.main import (
    app,
    run_swing_scanner,
    run_intraday_scanner,
    _normalize_scanner_response,
    _SCANNER_CACHE,
    _CACHE_LOCK,
    _INTRADAY_CACHE,
    _INTRADAY_LOCK
)

class TestSprint182BCacheSchema(unittest.TestCase):

    def test_normalize_scanner_response_none(self):
        res = _normalize_scanner_response(None, is_scanning=True, total_universe=200)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["total_universe"], 200)
        self.assertEqual(res["qualified_count"], 0)
        self.assertEqual(res["qualified_results"], [])
        self.assertEqual(res["status"], "SCANNING")

    def test_normalize_scanner_response_list(self):
        raw_list = [
            {"Symbol": "DIVISLAB.NS", "Signal": "BUY", "Score": 89},
            {"Symbol": "SUNPHARMA.NS", "Signal": "WATCH", "Score": 85}
        ]
        res = _normalize_scanner_response(raw_list, is_scanning=False, total_universe=200)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["total_universe"], 200)
        self.assertEqual(res["qualified_count"], 2)
        self.assertEqual(res["buy_count"], 1)
        self.assertEqual(res["watch_count"], 1)
        self.assertEqual(len(res["qualified_results"]), 2)
        self.assertEqual(res["status"], "COMPLETED")

    def test_normalize_scanner_response_dict(self):
        raw_dict = {
            "qualified_count": 1,
            "qualified_results": [{"Symbol": "LAURUSLABS.NS", "Signal": "BUY", "Score": 89}]
        }
        res = _normalize_scanner_response(raw_dict, is_scanning=False, total_universe=200)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["qualified_count"], 1)
        self.assertIn("provider", res)
        self.assertIn("market_status", res)

    def test_run_swing_scanner_async_modes(self):
        async def run_tests():
            # Mode 1: Cache is None
            with _CACHE_LOCK:
                _SCANNER_CACHE["data"] = None
            res1 = await run_swing_scanner()
            self.assertIsInstance(res1, dict)
            self.assertEqual(res1["status"], "SCANNING")
            self.assertEqual(res1["qualified_results"], [])

            # Mode 2: Cache is List
            with _CACHE_LOCK:
                _SCANNER_CACHE["data"] = [{"Symbol": "TATAMOTORS.NS", "Signal": "BUY"}]
                _SCANNER_CACHE["last_updated"] = time.time()
            res2 = await run_swing_scanner()
            self.assertIsInstance(res2, dict)
            self.assertEqual(res2["qualified_count"], 1)
            self.assertEqual(res2["qualified_results"][0]["Symbol"], "TATAMOTORS.NS")

            # Mode 3: Cache is Dict
            with _CACHE_LOCK:
                _SCANNER_CACHE["data"] = {
                    "qualified_count": 1,
                    "qualified_results": [{"Symbol": "TITAN.NS", "Signal": "BUY"}]
                }
                _SCANNER_CACHE["last_updated"] = time.time()
            res3 = await run_swing_scanner()
            self.assertIsInstance(res3, dict)
            self.assertEqual(res3["qualified_count"], 1)
            self.assertEqual(res3["qualified_results"][0]["Symbol"], "TITAN.NS")

        asyncio.run(run_tests())

if __name__ == "__main__":
    unittest.main()
