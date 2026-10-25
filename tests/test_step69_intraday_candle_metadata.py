import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from application.intraday_scanner_service import (
    IntradayScannerService,
    IntradayScanResultList,
    _normalize_candle_timestamp,
)
from core.models.domain_models import ScanResult, SignalStrength
from data.stocks import Stock


class TestStep69IntradayCandleMetadata(unittest.TestCase):
    """
    STEP 69 verification suite for Intraday candle timestamp metadata propagation.
    Ensures safe, non-mutating testing with synthetic fixtures.
    """

    def test_normalize_candle_timestamp_valid_formats(self):
        """Test valid ISO strings, datetimes (aware & naive), and epochs."""
        ist_tz = timezone(timedelta(hours=5, minutes=30))

        # Datetime naive
        dt_naive = datetime(2026, 10, 21, 13, 30, 0)
        res1 = _normalize_candle_timestamp(dt_naive)
        self.assertEqual(res1, "2026-10-21T13:30:00+05:30")

        # Datetime aware UTC
        dt_utc = datetime(2026, 10, 21, 8, 0, 0, tzinfo=timezone.utc)
        res2 = _normalize_candle_timestamp(dt_utc)
        self.assertEqual(res2, "2026-10-21T13:30:00+05:30")

        # Valid ISO string
        iso_str = "2026-10-21T13:30:00+05:30"
        res3 = _normalize_candle_timestamp(iso_str)
        self.assertEqual(res3, "2026-10-21T13:30:00+05:30")

    def test_normalize_candle_timestamp_missing_and_invalid(self):
        """Test that missing or invalid timestamps return None without fabricating values."""
        self.assertIsNone(_normalize_candle_timestamp(None))
        self.assertIsNone(_normalize_candle_timestamp(""))
        self.assertIsNone(_normalize_candle_timestamp("None"))
        self.assertIsNone(_normalize_candle_timestamp("NULL"))
        self.assertIsNone(_normalize_candle_timestamp("UNKNOWN"))
        self.assertIsNone(_normalize_candle_timestamp("LIVE"))
        self.assertIsNone(_normalize_candle_timestamp("not-a-valid-date"))
        self.assertIsNone(_normalize_candle_timestamp(-100))
        self.assertIsNone(_normalize_candle_timestamp(0))
        # Year out of reasonable range
        self.assertIsNone(_normalize_candle_timestamp(datetime(1990, 1, 1)))
        self.assertIsNone(_normalize_candle_timestamp(datetime(2099, 1, 1)))

    def test_intraday_scan_result_list_compatibility(self):
        """Test that IntradayScanResultList acts as a list while exposing dictionary access."""
        raw_picks = [
            {"Symbol": "TECHM.NS", "Signal": "BUY", "Score": 85.0},
            {"Symbol": "SAIL.NS", "Signal": "SELL", "Score": 72.0}
        ]
        payload = {
            "total_universe": 184,
            "total_scanned": 184,
            "latest_candle_timestamp": "2026-10-21T13:30:00+05:30",
            "candle_coverage_verified": False,
            "scanner_health": {
                "latest_candle_timestamp": "2026-10-21T13:30:00+05:30",
                "api_status": "ONLINE"
            }
        }
        res_list = IntradayScanResultList(raw_picks, payload=payload)

        # List behavior
        self.assertTrue(isinstance(res_list, list))
        self.assertEqual(len(res_list), 2)
        self.assertEqual(res_list[0]["Symbol"], "TECHM.NS")
        self.assertEqual(res_list[1]["Symbol"], "SAIL.NS")
        self.assertEqual([r["Symbol"] for r in res_list], ["TECHM.NS", "SAIL.NS"])

        # Dict access behavior (for api/main.py and consistency tests)
        self.assertEqual(res_list.get("total_universe"), 184)
        self.assertEqual(res_list.get("latest_candle_timestamp"), "2026-10-21T13:30:00+05:30")
        self.assertEqual(res_list["total_scanned"], 184)
        self.assertEqual(len(res_list.get("qualified_results")), 2)
        self.assertIn("total_universe", res_list)
        self.assertFalse(res_list.get("candle_coverage_verified"))

        # Attributes
        self.assertEqual(res_list.latest_candle_timestamp, "2026-10-21T13:30:00+05:30")
        self.assertFalse(res_list.candle_coverage_verified)

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_execute_intraday_scan_propagates_verified_timestamp(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """Verify that verified candle timestamps propagate through execute_intraday_scan."""
        mock_get_fno.return_value = [
            {"symbol": "RELIANCE.NS", "sector": "Energy"},
            {"symbol": "TCS.NS", "sector": "IT"}
        ]

        # Mock MarketDataManager instance
        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.get_live_price.return_value = 1500.0
        mock_manager.get_live_quote.return_value = {"volume": 100000}

        # Mock last_ohlcv_status on provider
        mock_manager.last_ohlcv_status = {
            "RELIANCE.NS": {
                "provider": "YahooFinance (Fallback)",
                "fallback_used": True,
                "paytm_error": "HTTP_405",
                "newest_candle_timestamp": "2026-10-21T13:30:00+05:30"
            },
            "TCS.NS": {
                "provider": "YahooFinance (Fallback)",
                "fallback_used": True,
                "paytm_error": "HTTP_405",
                "newest_candle_timestamp": "2026-10-21T13:25:00+05:30"
            }
        }
        mock_mdm_cls.return_value = mock_manager

        # Mock ScanResult from scanner_engine
        mock_sr = ScanResult(
            symbol="RELIANCE.NS",
            company_name="RELIANCE",
            sector="Energy",
            trend_direction="BULLISH",
            trend_score=75.0,
            momentum_score=80.0,
            structure_score=70.0,
            volume_score=65.0,
            volatility_score=50.0,
            relative_strength_score=70.0,
            risk_score=60.0,
            mtf_score=5.0,
            total_score=75.0,
            price=1500.0,
            volume=100000.0,
            signal=SignalStrength.BUY,
            timestamp=datetime.now()
        )
        mock_scan_market.return_value = [mock_sr]

        service = IntradayScannerService()
        results = service.execute_intraday_scan(timeframe="5m")

        # Verify results
        self.assertTrue(isinstance(results, list))
        self.assertEqual(results.get("latest_candle_timestamp"), "2026-10-21T13:30:00+05:30")
        self.assertFalse(results.get("candle_coverage_verified"))
        self.assertEqual(results.get("requested_interval"), "5m")

        health = service.get_health()
        self.assertEqual(health["latest_candle_timestamp"], "2026-10-21T13:30:00+05:30")
        self.assertFalse(health["candle_coverage_verified"])
        self.assertEqual(health["requested_interval"], "5m")
        self.assertEqual(health["api_status"], "ONLINE")

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_missing_ohlcv_timestamps_yield_none(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """Verify that when no candle timestamps exist, latest_candle_timestamp is None."""
        mock_get_fno.return_value = [{"symbol": "INFY.NS", "sector": "IT"}]
        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.last_ohlcv_status = {}  # Empty status
        mock_mdm_cls.return_value = mock_manager
        mock_scan_market.return_value = []

        service = IntradayScannerService()
        results = service.execute_intraday_scan(timeframe="5m")

        self.assertIsNone(results.get("latest_candle_timestamp"))
        self.assertFalse(results.get("candle_coverage_verified"))
        health = service.get_health()
        self.assertIsNone(health["latest_candle_timestamp"])

    def test_zero_swing_cross_contamination(self):
        """Verify that Intraday service does not reference or reuse Swing metadata."""
        service = IntradayScannerService()
        # Ensure no swing attributes exist on the service
        self.assertFalse(hasattr(service, "execute_swing_scan"))
        self.assertFalse(hasattr(service, "swing_service"))


if __name__ == "__main__":
    unittest.main()
