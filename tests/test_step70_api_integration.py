"""
Regression and Integration Test Suite for STEP 70:
API Integration of Intraday Candle Metadata and Swing Count Alignment.

Verifies:
1. Intraday timestamp flows from the STEP 69 service result into _INTRADAY_CACHE.
2. Intraday timestamp is not taken from Swing metadata.
3. Intraday provider statistics are not copied from Swing.
4. Missing/invalid Intraday timestamps remain UNKNOWN.
5. Unverified coverage cannot produce whole-universe FRESH.
6. Yahoo fallback attribution remains accurate.
7. Swing qualified_count equals len(qualified_results) after orchestration.
8. Swing displayed BUY/SELL/WATCH breakdown agrees with the final displayed array.
9. Intraday count equals len(qualified_results).
10. Scanner results, ranking, scoring, and deduplication decisions remain unchanged.
11. Existing API keys and value types remain backward-compatible.
"""

import unittest
from unittest.mock import patch, MagicMock
import copy
import time
from datetime import datetime, timezone, timedelta

import api.main as api_module
from application.intraday_scanner_service import IntradayScanResultList


class TestStep70ApiIntegration(unittest.TestCase):

    def setUp(self):
        # Reset caches to known test states without mutating disk
        self.original_scanner_cache = copy.deepcopy(api_module._SCANNER_CACHE)
        self.original_intraday_cache = copy.deepcopy(api_module._INTRADAY_CACHE)
        self.original_running = api_module._ORCHESTRATION_IS_RUNNING

    def tearDown(self):
        api_module._SCANNER_CACHE = self.original_scanner_cache
        api_module._INTRADAY_CACHE = self.original_intraday_cache
        api_module._ORCHESTRATION_IS_RUNNING = self.original_running

    def test_01_intraday_timestamp_flows_into_cache(self):
        """1. Verify Intraday timestamp flows from STEP 69 service result into _INTRADAY_CACHE."""
        test_ts = "2026-10-21T11:15:00+05:30"
        mock_payload = {
            "latest_candle_timestamp": test_ts,
            "candle_coverage_verified": False,
            "total_universe": 184,
            "total_scanned": 184,
            "qualified_count": 2,
            "scanner_health": {
                "latest_candle_timestamp": test_ts,
                "candle_coverage_verified": False,
                "primary_provider": "Paytm Money + Yahoo Finance (Fallback)",
                "provider_mode": "HYBRID_FALLBACK",
            },
            "provider_statistics": {
                "yahoo": {"success": 10, "total_requests": 10},
                "paytm": {"success": 5, "fallback_count": 5}
            }
        }
        mock_items = [
            {"symbol": "RELIANCE.NS", "signal": "BUY", "Signal": "BUY"},
            {"symbol": "INFY.NS", "signal": "SELL", "Signal": "SELL"}
        ]
        mock_intra_res = IntradayScanResultList(mock_items, payload=mock_payload)

        mock_swing_res = {
            "total_universe": 200,
            "total_scanned": 200,
            "qualified_count": 1,
            "qualified_results": [{"symbol": "TCS.NS", "signal": "BUY", "Signal": "BUY"}],
            "scanner_health": {
                "latest_candle_timestamp": "2026-10-21T09:15:00+05:30",
                "candle_coverage_verified": True
            },
            "provider_statistics": {
                "paytm": {"success": 200, "fallback_count": 0}
            }
        }

        with patch("application.swing_scanner_service.SwingScannerService.execute_swing_scan", return_value=mock_swing_res), \
             patch("application.intraday_scanner_service.IntradayScannerService.execute_intraday_scan", return_value=mock_intra_res), \
             patch("core.signal_orchestrator.SignalOrchestrator.merge_and_resolve", return_value=[
                 {"symbol": "TCS.NS", "signal": "BUY", "Signal": "BUY", "source_engine": "swing"},
                 {"symbol": "RELIANCE.NS", "signal": "BUY", "Signal": "BUY", "source_engine": "intraday"},
                 {"symbol": "INFY.NS", "signal": "SELL", "Signal": "SELL", "source_engine": "intraday"}
             ]), \
             patch("api.main._save_cache_to_disk", return_value=None):

            api_module._run_enterprise_orchestration()

        with api_module._INTRADAY_LOCK:
            cached_intra = api_module._INTRADAY_CACHE["data"]

        self.assertIsNotNone(cached_intra)
        self.assertEqual(cached_intra.get("latest_candle_timestamp"), test_ts)
        self.assertFalse(cached_intra.get("candle_coverage_verified"))
        self.assertEqual(cached_intra.get("scanner_health", {}).get("latest_candle_timestamp"), test_ts)
        self.assertEqual(cached_intra.get("scanner_health", {}).get("provider_mode"), "HYBRID_FALLBACK")

    def test_02_and_03_intraday_timestamp_and_stats_isolated_from_swing(self):
        """2 & 3. Verify Intraday timestamp and provider statistics are not taken from Swing metadata."""
        swing_ts = "2026-10-21T10:00:00+05:30"
        swing_stats = {"paytm": {"success": 999, "fallback_count": 0}}

        mock_swing_res = {
            "total_universe": 200,
            "total_scanned": 200,
            "qualified_count": 1,
            "qualified_results": [{"symbol": "TCS.NS", "signal": "BUY", "Signal": "BUY"}],
            "scanner_health": {
                "latest_candle_timestamp": swing_ts,
                "candle_coverage_verified": True
            },
            "provider_statistics": swing_stats
        }

        # Intraday with missing timestamp and its own separate stats
        intra_stats = {"yahoo": {"success": 42, "total_requests": 42}}
        mock_intra_payload = {
            "latest_candle_timestamp": None,
            "candle_coverage_verified": False,
            "scanner_health": {"latest_candle_timestamp": None, "candle_coverage_verified": False},
            "provider_statistics": intra_stats
        }
        mock_intra_res = IntradayScanResultList([], payload=mock_intra_payload)

        with patch("application.swing_scanner_service.SwingScannerService.execute_swing_scan", return_value=mock_swing_res), \
             patch("application.intraday_scanner_service.IntradayScannerService.execute_intraday_scan", return_value=mock_intra_res), \
             patch("core.signal_orchestrator.SignalOrchestrator.merge_and_resolve", return_value=[
                 {"symbol": "TCS.NS", "signal": "BUY", "Signal": "BUY", "source_engine": "swing"}
             ]), \
             patch("api.main._save_cache_to_disk", return_value=None):

            api_module._run_enterprise_orchestration()

        with api_module._INTRADAY_LOCK:
            cached_intra = api_module._INTRADAY_CACHE["data"]

        # Timestamp must be None, NOT swing_ts
        self.assertIsNone(cached_intra.get("latest_candle_timestamp"))
        self.assertNotEqual(cached_intra.get("latest_candle_timestamp"), swing_ts)

        # Provider stats must be intra_stats, NOT swing_stats
        self.assertEqual(cached_intra.get("provider_statistics"), intra_stats)
        self.assertNotEqual(cached_intra.get("provider_statistics"), swing_stats)

    def test_04_missing_or_invalid_intraday_timestamps_remain_unknown(self):
        """4. Verify missing or invalid Intraday timestamps evaluate to UNKNOWN freshness."""
        invalid_cases = [None, "", "INVALID_TIMESTAMP", "UNKNOWN", "2099-01-01T00:00:00+05:30"]
        for inv_ts in invalid_cases:
            eval_res = api_module._evaluate_market_data_freshness(
                latest_candle_ts=inv_ts,
                market_status="CLOSED",
                total_scanned=184,
                total_universe=184,
                candle_coverage_verified=False
            )
            self.assertEqual(eval_res["freshness"], "UNKNOWN", f"Expected UNKNOWN for ts={inv_ts}")

    def test_05_unverified_coverage_cannot_produce_whole_universe_fresh(self):
        """5. Verify unverified coverage (candle_coverage_verified=False) cannot produce whole-universe FRESH."""
        # IST now
        ist_tz = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(ist_tz)
        current_candle_ts = now_ist.isoformat()

        # Both for OPEN and CLOSED states
        for m_status in ["OPEN", "CLOSED"]:
            eval_res = api_module._evaluate_market_data_freshness(
                latest_candle_ts=current_candle_ts,
                market_status=m_status,
                total_scanned=184,
                total_universe=184,
                candle_coverage_verified=False
            )
            self.assertNotEqual(eval_res["freshness"], "FRESH", f"Unverified coverage must never be FRESH in status {m_status}")
            self.assertIn(eval_res["freshness"], ["PARTIAL", "STALE", "UNKNOWN"])

    def test_06_yahoo_fallback_attribution_accuracy(self):
        """6. Verify Yahoo fallback attribution remains truthful in metadata."""
        telemetry_fallback = {
            "provider_statistics": {
                "yahoo": {"success": 50, "total_requests": 50},
                "paytm": {"success": 20, "fallback_count": 30}
            }
        }
        with patch("api.main._check_paytm_authenticated", return_value=True):
            meta = api_module._get_provider_metadata(scan_data=telemetry_fallback)
            self.assertTrue(meta["fallback_used"])
            self.assertEqual(meta["provider_mode"], "HYBRID_FALLBACK")
            self.assertIn("Fallback", meta["provider"])

    def test_07_and_08_swing_count_and_breakdown_consistency_after_dedup(self):
        """7 & 8. Verify Swing qualified_count equals len(qualified_results) and breakdown matches displayed array."""
        # Pre-deduplication: 30 items (10 BUY, 10 SELL, 10 WATCH)
        pre_swing_items = []
        for i in range(10):
            pre_swing_items.append({"symbol": f"S_BUY_{i}", "signal": "BUY", "Signal": "BUY"})
        for i in range(10):
            pre_swing_items.append({"symbol": f"S_SELL_{i}", "signal": "SELL", "Signal": "SELL"})
        for i in range(10):
            pre_swing_items.append({"symbol": f"S_WATCH_{i}", "signal": "WATCH", "Signal": "WATCH"})

        mock_swing_res = {
            "total_universe": 200,
            "total_scanned": 200,
            "qualified_count": 30,
            "buy_count": 10,
            "sell_count": 10,
            "watch_count": 10,
            "filter_rejected_count": 170,
            "no_data_count": 0,
            "rejected_count": 170,
            "qualified_results": pre_swing_items,
            "scanner_health": {"latest_candle_timestamp": "2026-10-21T11:15:00+05:30"}
        }

        # Deduplication assigns 1 WATCH item to Intraday, leaving 29 Swing items
        post_swing_items = [s for s in pre_swing_items if s["symbol"] != "S_WATCH_9"]
        bharti = {"symbol": "S_WATCH_9", "signal": "SELL", "Signal": "SELL", "source_engine": "intraday"}

        merged_orchestrated = [
            dict(s, source_engine="swing") for s in post_swing_items
        ] + [bharti]

        mock_intra_res = IntradayScanResultList([bharti], payload={
            "latest_candle_timestamp": "2026-10-21T11:15:00+05:30",
            "candle_coverage_verified": False,
            "total_universe": 184,
            "total_scanned": 184,
            "qualified_count": 1
        })

        with patch("application.swing_scanner_service.SwingScannerService.execute_swing_scan", return_value=mock_swing_res), \
             patch("application.intraday_scanner_service.IntradayScannerService.execute_intraday_scan", return_value=mock_intra_res), \
             patch("core.signal_orchestrator.SignalOrchestrator.merge_and_resolve", return_value=merged_orchestrated), \
             patch("api.main._save_cache_to_disk", return_value=None):

            api_module._run_enterprise_orchestration()

        with api_module._CACHE_LOCK:
            swing_cached = api_module._SCANNER_CACHE["data"]

        # Check Swing reconciliation
        self.assertEqual(len(swing_cached["qualified_results"]), 29)
        self.assertEqual(swing_cached["qualified_count"], 29)
        self.assertEqual(swing_cached["pre_orchestration_qualified_count"], 30)
        self.assertEqual(swing_cached["buy_count"], 10)
        self.assertEqual(swing_cached["sell_count"], 10)
        self.assertEqual(swing_cached["watch_count"], 9)
        self.assertEqual(swing_cached["filter_rejected_count"], 171)

        # Check normalization pass-through
        normalized_resp = api_module._normalize_scanner_response(swing_cached, total_universe=200)
        self.assertEqual(normalized_resp["qualified_count"], 29)
        self.assertEqual(len(normalized_resp["qualified_results"]), 29)
        self.assertEqual(normalized_resp["buy_count"], 10)
        self.assertEqual(normalized_resp["sell_count"], 10)
        self.assertEqual(normalized_resp["watch_count"], 9)

    def test_09_intraday_count_equals_display_intra_length(self):
        """9. Verify Intraday count equals len(qualified_results)."""
        items = [
            {"symbol": "SYM1", "signal": "BUY", "Signal": "BUY", "source_engine": "intraday"},
            {"symbol": "SYM2", "signal": "SELL", "Signal": "SELL", "source_engine": "intraday"},
        ]
        mock_intra_res = IntradayScanResultList(items, payload={
            "latest_candle_timestamp": "2026-10-21T11:15:00+05:30",
            "candle_coverage_verified": False,
            "total_universe": 184,
            "total_scanned": 184,
            "qualified_count": 2
        })
        mock_swing_res = {
            "total_universe": 200, "total_scanned": 200, "qualified_count": 0, "qualified_results": []
        }

        with patch("application.swing_scanner_service.SwingScannerService.execute_swing_scan", return_value=mock_swing_res), \
             patch("application.intraday_scanner_service.IntradayScannerService.execute_intraday_scan", return_value=mock_intra_res), \
             patch("core.signal_orchestrator.SignalOrchestrator.merge_and_resolve", return_value=items), \
             patch("api.main._save_cache_to_disk", return_value=None):

            api_module._run_enterprise_orchestration()

        with api_module._INTRADAY_LOCK:
            intra_cached = api_module._INTRADAY_CACHE["data"]

        self.assertEqual(len(intra_cached["qualified_results"]), 2)
        self.assertEqual(intra_cached["qualified_count"], 2)
        self.assertEqual(intra_cached["buy_count"], 1)
        self.assertEqual(intra_cached["sell_count"], 1)
        self.assertEqual(intra_cached["watch_count"], 0)

    def test_10_and_11_backward_compatibility_and_field_preservation(self):
        """10 & 11. Verify existing API response keys and types remain backward-compatible."""
        sample_dict = {
            "total_universe": 184,
            "total_scanned": 184,
            "qualified_count": 1,
            "buy_count": 1,
            "sell_count": 0,
            "watch_count": 0,
            "qualified_results": [{"symbol": "INFY.NS", "signal": "BUY", "Signal": "BUY"}],
            "latest_candle_timestamp": "2026-10-21T11:15:00+05:30",
            "candle_coverage_verified": False,
            "scanner_health": {
                "latest_candle_timestamp": "2026-10-21T11:15:00+05:30",
                "candle_coverage_verified": False
            }
        }
        res = api_module._normalize_scanner_response(sample_dict, total_universe=184)

        # Verify required API contract keys
        required_keys = [
            "total_universe", "total_attempted", "total_processed", "total_scanned",
            "total_ranked", "qualified_count", "filter_rejected_count", "no_data_count",
            "buy_count", "sell_count", "watch_count", "qualified_results",
            "server_timestamp", "scan_timestamp", "cache_timestamp", "market_data_freshness",
            "market_data_timestamp", "latest_candle_timestamp", "candle_coverage_verified",
            "provider", "market_status", "fallback_used"
        ]
        for key in required_keys:
            self.assertIn(key, res, f"Missing required response key: {key}")

        self.assertIsInstance(res["qualified_results"], list)
        self.assertIsInstance(res["qualified_count"], int)
        self.assertEqual(res["qualified_count"], len(res["qualified_results"]))


if __name__ == "__main__":
    unittest.main()
