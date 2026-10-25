"""
STEP 74: Permanent Regression Test Suite for STEP 72/73 List Normalization Safety.

Automates the regression verification cases for _normalize_scanner_response() in api/main.py:
1. Coverage attribute False must take precedence over getter value True.
2. If coverage attribute is absent, valid getter metadata is handled according to existing contract.
3. Missing, empty, and malformed timestamps preserve UNKNOWN freshness.
4. Wrapper with total_universe=200, total_scanned=184, 2 qualified picks produces consistent counts:
   184 scanned, 182 filtered, 16 no-data.
5. Wrapper with total_universe=200, total_scanned=2, 2 qualified picks does not classify unscanned assets as filter-rejected:
   2 scanned, 0 filtered, 198 no-data.
6. Inconsistent total_scanned (bool, negative, zero, too-small, too-large, string, float) safely rejected with fallback.
   Documents fallback semantics: len(data) is a conservative fallback based on available list contents,
   not proof of complete universe scanning.
7. Provider statistics preserved when a valid candle timestamp is present.
8. Ordinary Python list compatibility remains intact.
9. Standard dictionary-cache normalization remains unchanged.
10. Fallback from scanner_health dictionary when coverage is absent from attributes and top-level getter.
11. Preserving valid explicit filter_rejected_count and no_data_count when internally consistent.
"""

import time
import unittest
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import api.main as api_module
from application.intraday_scanner_service import IntradayScanResultList

IST_TZ = timezone(timedelta(hours=5, minutes=30))
# Fixed deterministic market clock for test suite:
# Wednesday, October 21, 2026 at 16:00:00 IST (weekday, closed session after 15:30)
FIXED_MARKET_DATETIME = datetime(2026, 10, 21, 16, 0, 0, tzinfo=IST_TZ)


class MockDatetime(datetime):
    """
    Deterministic datetime subclass that controls datetime.now() while preserving
    all real datetime methods (fromisoformat, strptime, astimezone, etc.).
    """
    _default_now = FIXED_MARKET_DATETIME
    _current_now = FIXED_MARKET_DATETIME

    @classmethod
    def set_default_now(cls, dt: datetime):
        cls._default_now = dt
        cls._current_now = dt

    @classmethod
    def set_now(cls, dt: datetime):
        cls._current_now = dt

    @classmethod
    def reset_now(cls):
        cls._current_now = cls._default_now

    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return cls._current_now.astimezone(tz)
        return cls._current_now


def _get_current_ist_timestamp() -> str:
    """Helper returning an ISO formatted timestamp for the latest completed trading session
    derived deterministically from the controlled market clock.
    """
    now = MockDatetime.now(IST_TZ)
    # When market is closed on weekend, Friday was the latest completed trading session
    if now.weekday() == 5:  # Saturday
        session_date = (now - timedelta(days=1)).date()
    elif now.weekday() == 6:  # Sunday
        session_date = (now - timedelta(days=2)).date()
    else:
        session_date = now.date()
    return f"{session_date.isoformat()}T15:30:00+05:30"


class TestStep73ListNormalizationSafety(unittest.TestCase):
    """Regression test suite for _normalize_scanner_response() list-normalization safety."""

    def setUp(self):
        self.sample_items = [
            {"Symbol": "RELIANCE.NS", "Signal": "BUY", "Score": 88.5},
            {"Symbol": "TCS.NS", "Signal": "SELL", "Score": 76.0},
        ]
        MockDatetime.reset_now()
        self.dt_patcher = patch("api.main.datetime", MockDatetime)
        self.time_patcher = patch("api.main.time.time", side_effect=lambda: MockDatetime.now().timestamp())
        self.dt_patcher.start()
        self.time_patcher.start()

        self.current_ist_ts = _get_current_ist_timestamp()
        self.current_time = MockDatetime.now().timestamp()

    def tearDown(self):
        self.time_patcher.stop()
        self.dt_patcher.stop()
        MockDatetime.reset_now()

    def test_01_coverage_attribute_false_precedence_over_getter_true(self):
        """Case 1: Explicit attribute candle_coverage_verified=False must take precedence

        over getter value True, and must never yield whole-universe FRESH.
        """
        class ConflictedWrapper(list):
            def __init__(self, items: List[Dict[str, Any]], payload: Dict[str, Any]):
                super().__init__(items)
                self.payload = payload
                self.latest_candle_timestamp = payload.get("latest_candle_timestamp")
                # Explicit attribute set to False
                self.candle_coverage_verified = False

            def get(self, key: str, default: Any = None) -> Any:
                return self.payload.get(key, default)

        conflicted_payload = {
            "total_universe": 184,
            "total_scanned": 184,
            "latest_candle_timestamp": self.current_ist_ts,
            # Getter returns True, contradictory to attribute
            "candle_coverage_verified": True,
            "scanner_health": {
                "candle_coverage_verified": True,
                "latest_candle_timestamp": self.current_ist_ts,
            },
        }

        wrapper = ConflictedWrapper(self.sample_items, conflicted_payload)
        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=184,
            cache_timestamp=self.current_time,
        )

        # Attribute False must take precedence
        self.assertFalse(
            res.get("candle_coverage_verified"),
            "Explicit attribute False must take precedence over getter True."
        )
        # Unverified coverage must NOT yield FRESH
        self.assertNotEqual(
            res.get("market_data_freshness"),
            "FRESH",
            "Unverified candle coverage must never produce whole-universe FRESH status."
        )
        self.assertIn(
            res.get("market_data_freshness"),
            ["PARTIAL", "STALE"],
            "Market data freshness with unverified coverage should evaluate to PARTIAL or STALE."
        )

        # Demonstrate independence across calendar states (weekend clock with Friday completed session candle)
        sat_now = datetime(2026, 10, 24, 16, 0, 0, tzinfo=IST_TZ)
        fri_candle = "2026-10-23T15:30:00+05:30"
        sat_conflicted = dict(conflicted_payload)
        sat_conflicted["latest_candle_timestamp"] = fri_candle
        sat_conflicted["scanner_health"] = {
            "candle_coverage_verified": True,
            "latest_candle_timestamp": fri_candle,
        }
        w_weekend = ConflictedWrapper(self.sample_items, sat_conflicted)
        try:
            MockDatetime.set_now(sat_now)
            res_weekend = api_module._normalize_scanner_response(
                w_weekend,
                total_universe=184,
                cache_timestamp=sat_now.timestamp(),
            )
            self.assertFalse(res_weekend.get("candle_coverage_verified"))
            self.assertNotEqual(res_weekend.get("market_data_freshness"), "FRESH")
            self.assertIn(res_weekend.get("market_data_freshness"), ["PARTIAL", "STALE"])
        finally:
            MockDatetime.reset_now()

    def test_02_coverage_getter_fallback_when_attribute_absent(self):
        """Case 2: When the coverage attribute is absent, getter metadata

        must be handled according to the contract.
        """
        class GetterOnlyWrapper(list):
            def __init__(self, items: List[Dict[str, Any]], payload: Dict[str, Any]):
                super().__init__(items)
                self.payload = payload

            def get(self, key: str, default: Any = None) -> Any:
                return self.payload.get(key, default)

        getter_payload = {
            "total_universe": 184,
            "total_scanned": 184,
            "latest_candle_timestamp": self.current_ist_ts,
            "candle_coverage_verified": True,
            "provider_statistics": {
                "yahoo": {"success": 5, "total_requests": 5}
            },
        }

        wrapper = GetterOnlyWrapper(self.sample_items, getter_payload)
        # Verify attribute is actually absent
        self.assertFalse(hasattr(wrapper, "candle_coverage_verified"))

        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=184,
            cache_timestamp=self.current_time,
        )

        self.assertTrue(
            res.get("candle_coverage_verified"),
            "When attribute is absent, valid getter True must be respected."
        )
        self.assertEqual(
            res.get("provider_statistics"),
            {"yahoo": {"success": 5, "total_requests": 5}},
            "Provider statistics from getter must be preserved."
        )

    def test_03_missing_empty_and_malformed_timestamps_preserve_unknown(self):
        """Case 3: Missing, empty, or malformed timestamps must strictly

        preserve UNKNOWN freshness.
        """
        bad_timestamps = [
            None,
            "",
            "   ",
            "None",
            "NULL",
            "INVALID_TIMESTAMP",
            "UNKNOWN",
            "LIVE",
            -100,
            0,
        ]

        for bad_ts in bad_timestamps:
            with self.subTest(bad_timestamp=bad_ts):
                payload = {
                    "total_universe": 184,
                    "total_scanned": 184,
                    "latest_candle_timestamp": bad_ts,
                    "candle_coverage_verified": False,
                }
                wrapper = IntradayScanResultList(self.sample_items, payload=payload)
                res = api_module._normalize_scanner_response(
                    wrapper,
                    total_universe=184,
                    cache_timestamp=self.current_time,
                )

                self.assertEqual(
                    res.get("market_data_freshness"),
                    "UNKNOWN",
                    f"Timestamp {bad_ts!r} must result in UNKNOWN freshness."
                )

    def test_04_proportional_counts_scanned_184_of_200_with_2_qualified(self):
        """Case 4: Wrapper with total_universe=200, total_scanned=184, 2 qualified

        picks must produce consistent counts: 184 scanned, 182 filtered, 16 no-data.
        """
        payload = {
            "total_universe": 184,
            "total_scanned": 184,
            "latest_candle_timestamp": self.current_ist_ts,
            "candle_coverage_verified": False,
            "provider_statistics": {"yahoo": {"success": 10}},
        }
        wrapper = IntradayScanResultList(self.sample_items, payload=payload)
        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=200,
            cache_timestamp=self.current_time,
        )

        self.assertEqual(res.get("total_universe"), 200)
        self.assertEqual(res.get("total_scanned"), 184, "Total scanned must match wrapper 184.")
        self.assertEqual(res.get("qualified_count"), 2, "Qualified count must match len(data)=2.")
        self.assertEqual(
            res.get("filter_rejected_count"),
            182,
            "filter_rejected_count must be 184 - 2 = 182."
        )
        self.assertEqual(
            res.get("no_data_count"),
            16,
            "no_data_count must be 200 - 184 = 16."
        )
        self.assertEqual(
            res.get("rejected_count"),
            198,
            "rejected_count must equal filter_rejected (182) + no_data (16) = 198."
        )
        self.assertEqual(res.get("total_attempted"), 200)
        self.assertEqual(res.get("total_processed"), 2)

    def test_05_unscanned_assets_not_falsely_filter_rejected(self):
        """Case 5: Wrapper with total_universe=200, total_scanned=2, 2 qualified

        picks must not classify the 198 unscanned assets as filter-rejected.
        """
        payload = {
            "total_universe": 200,
            "total_scanned": 2,
            "latest_candle_timestamp": self.current_ist_ts,
            "candle_coverage_verified": False,
        }
        wrapper = IntradayScanResultList(self.sample_items, payload=payload)
        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=200,
            cache_timestamp=self.current_time,
        )

        self.assertEqual(res.get("total_scanned"), 2)
        self.assertEqual(res.get("qualified_count"), 2)
        self.assertEqual(
            res.get("filter_rejected_count"),
            0,
            "filter_rejected_count must be 0 (2 scanned - 2 qualified), not 198."
        )
        self.assertEqual(
            res.get("no_data_count"),
            198,
            "The 198 unscanned assets must be reported under no_data_count."
        )
        self.assertEqual(
            res.get("rejected_count"),
            198,
            "rejected_count must equal 0 + 198 = 198."
        )

    def test_06_inconsistent_total_scanned_safely_rejected_with_fallback(self):
        """Case 6: Inconsistent total_scanned values (Boolean, negative, zero, smaller-than-data,

        greater-than-universe, string, float) must be rejected safely and fall back to len(data).

        FALLBACK SEMANTICS DOCUMENTATION:
        When the wrapper does not provide a valid total_scanned, len(data) is only a
        conservative fallback based on available list contents—not proof of complete
        universe scanning.
        """
        inconsistent_cases = [
            (True, "Boolean True (isinstance(True, int) is True)"),
            (False, "Boolean False"),
            (-10, "Negative integer"),
            (0, "Zero scanned"),
            (1, "Count smaller than len(data) = 2"),
            (250, "Count larger than total_universe = 200"),
            ("184", "String representation of integer"),
            (184.5, "Float representation"),
            (None, "None value"),
            ([], "List value"),
            ({}, "Dict value"),
        ]

        for bad_scanned, label in inconsistent_cases:
            with self.subTest(label=label, bad_val=bad_scanned):
                payload = {
                    "total_universe": 200,
                    "total_scanned": bad_scanned,
                    "latest_candle_timestamp": self.current_ist_ts,
                }
                wrapper = IntradayScanResultList(self.sample_items, payload=payload)
                res = api_module._normalize_scanner_response(
                    wrapper,
                    total_universe=200,
                    cache_timestamp=self.current_time,
                )

                # Safe fallback to len(data) = 2
                self.assertEqual(
                    res.get("total_scanned"),
                    2,
                    f"Failed for {label}: total_scanned must safely fall back to len(data)=2."
                )
                self.assertEqual(
                    res.get("filter_rejected_count"),
                    0,
                    f"Failed for {label}: filter_rejected_count must fall back to 0."
                )
                self.assertEqual(
                    res.get("no_data_count"),
                    198,
                    f"Failed for {label}: no_data_count must fall back to total_universe - len(data)."
                )

        # Explicit assertion confirming fallback semantics contract
        fallback_payload = {"total_scanned": None}
        fallback_wrapper = IntradayScanResultList(self.sample_items, payload=fallback_payload)
        fallback_res = api_module._normalize_scanner_response(fallback_wrapper, total_universe=200)
        # Fallback total_scanned equals available list length
        self.assertEqual(fallback_res.get("total_scanned"), len(self.sample_items))
        # Filter rejected is 0 because no scanned assets were filtered beyond the list itself
        self.assertEqual(fallback_res.get("filter_rejected_count"), 0)
        # Remaining universe is conservative no_data
        self.assertEqual(fallback_res.get("no_data_count"), 200 - len(self.sample_items))

    def test_07_provider_statistics_preserved_with_valid_timestamp(self):
        """Case 7: Provider statistics must be retained on the list-wrapper

        normalization branch when a valid candle timestamp is present.
        """
        expected_stats = {
            "yahoo": {"success": 184, "fallback_count": 0, "failure": 0},
            "paytm": {"success": 0, "fallback_count": 184, "failure": 184},
        }
        payload = {
            "total_universe": 184,
            "total_scanned": 184,
            "latest_candle_timestamp": self.current_ist_ts,
            "candle_coverage_verified": False,
            "provider_statistics": expected_stats,
            "scanner_health": {
                "latest_candle_timestamp": self.current_ist_ts,
                "primary_provider": "Paytm Money + Yahoo Finance (Fallback)",
                "provider_mode": "HYBRID_FALLBACK",
            },
        }
        wrapper = IntradayScanResultList(self.sample_items, payload=payload)
        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=184,
            cache_timestamp=self.current_time,
        )

        self.assertEqual(res.get("latest_candle_timestamp"), self.current_ist_ts)
        self.assertEqual(
            res.get("provider_statistics"),
            expected_stats,
            "provider_statistics dictionary must be preserved in response."
        )
        self.assertEqual(
            res.get("scanner_health", {}).get("primary_provider"),
            "Paytm Money + Yahoo Finance (Fallback)"
        )
        self.assertEqual(
            res.get("scanner_health", {}).get("provider_mode"),
            "HYBRID_FALLBACK"
        )
        self.assertIsNotNone(res.get("provider"))

    def test_08_ordinary_python_list_compatibility(self):
        """Case 8: Ordinary Python list compatibility must remain intact

        (fallback to len(data), COMPLETED status, no provider statistics).
        """
        raw_list = [
            {"Symbol": "DIVISLAB.NS", "Signal": "BUY", "Score": 89},
            {"Symbol": "SUNPHARMA.NS", "Signal": "WATCH", "Score": 85},
        ]
        res = api_module._normalize_scanner_response(
            raw_list,
            is_scanning=False,
            total_universe=200,
            cache_timestamp=self.current_time,
            ttl_seconds=300.0,
        )

        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("total_scanned"), 2)
        self.assertEqual(res.get("qualified_count"), 2)
        self.assertEqual(res.get("filter_rejected_count"), 0)
        self.assertEqual(res.get("no_data_count"), 198)
        self.assertEqual(res.get("rejected_count"), 198)
        self.assertEqual(res.get("buy_count"), 1)
        self.assertEqual(res.get("watch_count"), 1)
        self.assertEqual(res.get("sell_count"), 0)
        self.assertEqual(res.get("status"), "COMPLETED")
        self.assertIsNone(res.get("provider_statistics"))
        self.assertFalse(res.get("is_stale"))

    def test_09_standard_dictionary_cache_normalization_unchanged(self):
        """Case 9: Standard dictionary-cache normalization path remains completely unchanged."""
        payload_dict = {
            "total_universe": 184,
            "total_scanned": 184,
            "qualified_count": 1,
            "qualified_results": [{"symbol": "INFY.NS", "signal": "BUY", "Signal": "BUY"}],
            "latest_candle_timestamp": self.current_ist_ts,
            "candle_coverage_verified": False,
            "provider_statistics": {"yahoo": {"success": 10}},
        }
        res = api_module._normalize_scanner_response(
            payload_dict,
            total_universe=184,
            cache_timestamp=self.current_time,
        )

        self.assertEqual(res.get("total_scanned"), 184)
        self.assertEqual(res.get("qualified_count"), 1)
        self.assertEqual(res.get("filter_rejected_count"), 183)
        self.assertEqual(res.get("no_data_count"), 0)
        self.assertEqual(res.get("provider_statistics"), {"yahoo": {"success": 10}})
        self.assertFalse(res.get("candle_coverage_verified"))
        self.assertIn(res.get("market_data_freshness"), ["PARTIAL", "STALE"])
        self.assertEqual(res.get("status"), "COMPLETED")

        # Demonstrate independence across calendar states (weekend clock with Friday completed session candle)
        sat_now = datetime(2026, 10, 24, 16, 0, 0, tzinfo=IST_TZ)
        fri_candle = "2026-10-23T15:30:00+05:30"
        payload_sat = dict(payload_dict)
        payload_sat["latest_candle_timestamp"] = fri_candle
        try:
            MockDatetime.set_now(sat_now)
            res_sat = api_module._normalize_scanner_response(
                payload_sat,
                total_universe=184,
                cache_timestamp=sat_now.timestamp(),
            )
            self.assertEqual(res_sat.get("total_scanned"), 184)
            self.assertFalse(res_sat.get("candle_coverage_verified"))
            self.assertIn(res_sat.get("market_data_freshness"), ["PARTIAL", "STALE"])
        finally:
            MockDatetime.reset_now()

    def test_10_scanner_health_fallback_when_attribute_and_getter_coverage_absent(self):
        """Case 10: Fallback to scanner_health dictionary when coverage is absent

        from both instance attributes and top-level getter.
        """
        class HealthOnlyWrapper(list):
            def __init__(self, items: List[Dict[str, Any]], scanner_health: Dict[str, Any]):
                super().__init__(items)
                self.scanner_health = scanner_health

            def get(self, key: str, default: Any = None) -> Any:
                if key == "scanner_health":
                    return self.scanner_health
                return default

        health_dict = {
            "candle_coverage_verified": True,
            "latest_candle_timestamp": self.current_ist_ts,
        }
        wrapper = HealthOnlyWrapper(self.sample_items, health_dict)
        self.assertFalse(hasattr(wrapper, "candle_coverage_verified"))
        self.assertIsNone(wrapper.get("candle_coverage_verified"))

        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=184,
            cache_timestamp=self.current_time,
        )

        self.assertTrue(
            res.get("candle_coverage_verified"),
            "When absent elsewhere, scanner_health candle_coverage_verified should be used."
        )

    def test_11_preserve_internally_consistent_explicit_rejection_counts(self):
        """Case 11: When wrapper provides explicit filter_rejected_count and no_data_count

        that are internally consistent with total_scanned and total_universe, they must be preserved.
        """
        payload = {
            "total_universe": 200,
            "total_scanned": 150,
            "filter_rejected_count": 148,
            "no_data_count": 50,
            "latest_candle_timestamp": self.current_ist_ts,
            "candle_coverage_verified": False,
        }
        # Invariants: 148 (fr) + 2 (qual) <= 150 (scanned), and 148 + 50 + 2 == 200 (universe)
        wrapper = IntradayScanResultList(self.sample_items, payload=payload)
        res = api_module._normalize_scanner_response(
            wrapper,
            total_universe=200,
            cache_timestamp=self.current_time,
        )

        self.assertEqual(res.get("total_scanned"), 150)
        self.assertEqual(res.get("filter_rejected_count"), 148)
        self.assertEqual(res.get("no_data_count"), 50)
        self.assertEqual(res.get("rejected_count"), 198)


if __name__ == "__main__":
    unittest.main()
