import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from typing import List, Dict, Any

from application.intraday_scanner_service import IntradayScannerService, IntradayScanResultList
from core.models.domain_models import ScanResult, SignalStrength
from api.main import _normalize_scanner_response


class TestStep88IntradayUniverseCounts(unittest.TestCase):
    """
    STEP 89 regression test suite for Intraday universe count and rejection-count reconciliation.
    Verifies that the fno_data shadowing bug is eliminated, total_universe reflects the actual
    configured universe (e.g. 184), and all count partitioning equations balance deterministically.
    """

    def _create_mock_scan_result(self, symbol: str, score: float = 75.0, signal_str: str = "BUY"):
        sr = ScanResult(
            symbol=symbol,
            company_name=symbol.replace(".NS", ""),
            sector="General",
            trend_direction="BULLISH",
            trend_score=score,
            momentum_score=score,
            structure_score=score,
            volume_score=score,
            volatility_score=50.0,
            relative_strength_score=score,
            risk_score=50.0,
            mtf_score=5.0,
            total_score=score,
            price=1000.0,
            volume=50000.0,
            signal=SignalStrength.BUY if signal_str == "BUY" else SignalStrength.WATCH,
            timestamp=datetime.now(),
            status="RANKED"
        )
        setattr(sr, "oi_change_pct", 5.2)
        setattr(sr, "pcr", 0.95)
        setattr(sr, "max_pain", 1000)
        setattr(sr, "total_oi", 500000)
        setattr(sr, "fno_bias", "BULLISH")
        setattr(sr, "adjusted_score", score)
        setattr(sr, "confidence", 85.0)
        setattr(sr, "adx_value", 32.0)
        return sr

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_01_universe_count_not_shadowed_by_fno_metrics(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """
        Verify that processing per-symbol 5-key F&O metrics does NOT shadow or overwrite
        the outer 184-symbol universe count.
        """
        # 1. Supply synthetic 184-symbol universe
        universe_symbols = [f"SYM_{i:03d}.NS" for i in range(184)]
        mock_get_fno.return_value = [{"symbol": s, "sector": "General"} for s in universe_symbols]

        # 2. Mock MarketDataManager
        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.get_live_price.return_value = 1000.0
        mock_manager.get_live_quote.return_value = {"volume": 50000}
        mock_manager.get_history.return_value = []
        mock_manager.last_ohlcv_status = {}
        mock_mdm_cls.return_value = mock_manager

        # 3. Simulate 27 viable ScanResult candidates returned from scan_market
        mock_candidates = [
            self._create_mock_scan_result(universe_symbols[i], score=90.0 - i)
            for i in range(27)
        ]
        mock_scan_market.return_value = mock_candidates

        service = IntradayScannerService()
        result = service.execute_intraday_scan(timeframe="5m")

        # Invariant checks
        self.assertIsInstance(result, IntradayScanResultList)
        self.assertEqual(result.get("total_universe"), 184)
        self.assertNotEqual(result.get("total_universe"), 5, "Defect: total_universe must NOT be 5!")
        self.assertEqual(result.get("total_scanned"), 27)
        self.assertTrue(result.get("total_scanned") <= result.get("total_universe"))

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_02_exact_step88_reconciliation_values_with_9_qualified(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """
        Verify the exact STEP 88 count reconciliation contract:
        total_universe: 184, total_scanned: 27, qualified_count: 9,
        filter_rejected_count: 18, no_data_count: 157, rejected_count: 175.
        """
        universe_symbols = [f"SYM_{i:03d}.NS" for i in range(184)]
        mock_get_fno.return_value = [{"symbol": s, "sector": "General"} for s in universe_symbols]

        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.get_live_price.return_value = 1000.0
        mock_manager.get_live_quote.return_value = {"volume": 50000}
        mock_manager.get_history.return_value = []
        mock_manager.last_ohlcv_status = {}
        mock_mdm_cls.return_value = mock_manager

        mock_candidates = [
            self._create_mock_scan_result(universe_symbols[i], score=95.0 - i)
            for i in range(27)
        ]
        mock_scan_market.return_value = mock_candidates

        service = IntradayScannerService()

        # Patch EliteSelectionEngine & PrecisionEntryEngine to deterministically accept exactly 9 picks
        with patch("core.elite_selection_engine.EliteSelectionEngine.evaluate") as mock_ese, \
             patch("core.precision_entry_engine.PrecisionEntryEngine.evaluate") as mock_pee:

            def ese_side_effect(item):
                idx = int(item["Symbol"].split("_")[1].split(".")[0])
                return dict(item) if idx < 9 else None
            mock_ese.side_effect = ese_side_effect

            def pee_side_effect(elite_res):
                res = dict(elite_res)
                res["Trade Quality Index"] = res.get("Score", 80)
                res["Trade Grade"] = "A"
                res["Risk Grade"] = "LOW"
                res["Entry Decision"] = "ENTER NOW"
                res["Entry Score"] = 85
                res["Expected Holding Time"] = "30m"
                res["Reason Selected"] = "Momentum Breakout"
                return res
            mock_pee.side_effect = pee_side_effect

            result = service.execute_intraday_scan(timeframe="5m")

        # Exact expected reconciliation
        self.assertEqual(result.get("total_universe"), 184)
        self.assertEqual(result.get("total_scanned"), 27)
        self.assertEqual(result.get("qualified_count"), 9)
        self.assertEqual(len(result), 9)
        self.assertEqual(result.get("filter_rejected_count"), 18)
        self.assertEqual(result.get("no_data_count"), 157)
        self.assertEqual(result.get("rejected_count"), 175)

        # Mathematical contract checks
        self.assertEqual(
            result.get("filter_rejected_count") + result.get("qualified_count"),
            result.get("total_scanned")
        )
        self.assertEqual(
            result.get("filter_rejected_count") + result.get("no_data_count") + result.get("qualified_count"),
            result.get("total_universe")
        )
        self.assertEqual(
            result.get("rejected_count") + result.get("qualified_count"),
            result.get("total_universe")
        )

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_03_scanner_health_and_cache_payload_universe_consistency(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """
        Verify that last_health and last_cache_payload both preserve the 184 universe size.
        """
        universe_symbols = [f"SYM_{i:03d}.NS" for i in range(184)]
        mock_get_fno.return_value = [{"symbol": s, "sector": "General"} for s in universe_symbols]

        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.get_live_price.return_value = 1000.0
        mock_manager.get_live_quote.return_value = {"volume": 50000}
        mock_manager.get_history.return_value = []
        mock_manager.last_ohlcv_status = {}
        mock_mdm_cls.return_value = mock_manager

        mock_scan_market.return_value = [
            self._create_mock_scan_result(universe_symbols[i]) for i in range(10)
        ]

        service = IntradayScannerService()
        result = service.execute_intraday_scan(timeframe="5m")

        self.assertEqual(service.last_health["total_universe"], 184)
        self.assertEqual(service.last_cache_payload["total_universe"], 184)
        self.assertEqual(result.get("total_universe"), 184)
        self.assertEqual(result["total_universe"], 184)
        self.assertEqual(result.payload["total_universe"], 184)

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_04_normalize_scanner_response_integration(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """
        Verify that passing the IntradayScanResultList to api.main._normalize_scanner_response
        preserves all reconciled counts and correctly labels freshness as non-FRESH.
        """
        universe_symbols = [f"SYM_{i:03d}.NS" for i in range(184)]
        mock_get_fno.return_value = [{"symbol": s, "sector": "General"} for s in universe_symbols]

        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.get_live_price.return_value = 1000.0
        mock_manager.get_live_quote.return_value = {"volume": 50000}
        mock_manager.get_history.return_value = []
        mock_manager.last_ohlcv_status = {}
        mock_mdm_cls.return_value = mock_manager

        mock_candidates = [
            self._create_mock_scan_result(universe_symbols[i], score=95.0 - i)
            for i in range(27)
        ]
        mock_scan_market.return_value = mock_candidates

        service = IntradayScannerService()

        with patch("core.elite_selection_engine.EliteSelectionEngine.evaluate") as mock_ese, \
             patch("core.precision_entry_engine.PrecisionEntryEngine.evaluate") as mock_pee:
            def ese_side_effect(item):
                idx = int(item["Symbol"].split("_")[1].split(".")[0])
                return dict(item) if idx < 9 else None
            mock_ese.side_effect = ese_side_effect
            mock_pee.side_effect = lambda x: dict(x)

            result = service.execute_intraday_scan(timeframe="5m")

        # Pass through api/main.py normalizer
        norm_resp = _normalize_scanner_response(
            result,
            is_scanning=False,
            total_universe=184,
            cache_timestamp=1700000000.0,
            ttl_seconds=300.0
        )

        self.assertEqual(norm_resp["total_universe"], 184)
        self.assertEqual(norm_resp["total_scanned"], 27)
        self.assertEqual(norm_resp["qualified_count"], 9)
        self.assertEqual(norm_resp["filter_rejected_count"], 18)
        self.assertEqual(norm_resp["no_data_count"], 157)
        self.assertEqual(norm_resp["rejected_count"], 175)
        self.assertEqual(norm_resp["total_processed"], 9)
        self.assertNotEqual(norm_resp["market_data_freshness"], "FRESH")

    @patch("application.intraday_scanner_service.get_fno_symbols")
    @patch("market.market_data_manager.MarketDataManager")
    @patch("scanner.scanner_engine.ScannerEngine.scan_market")
    def test_05_dynamic_universe_sizing_not_hardcoded(
        self, mock_scan_market, mock_mdm_cls, mock_get_fno
    ):
        """
        Verify that total_universe is dynamically derived from configured stock_list
        and not hardcoded to 184.
        """
        # Dynamic 50-symbol universe
        custom_symbols = [f"CUST_{i:02d}.NS" for i in range(50)]
        mock_get_fno.return_value = [{"symbol": s, "sector": "General"} for s in custom_symbols]

        mock_manager = MagicMock()
        mock_manager.is_connected.return_value = True
        mock_manager.get_live_price.return_value = 500.0
        mock_manager.get_live_quote.return_value = {"volume": 20000}
        mock_manager.get_history.return_value = []
        mock_manager.last_ohlcv_status = {}
        mock_mdm_cls.return_value = mock_manager

        mock_candidates = [
            self._create_mock_scan_result(custom_symbols[i], score=80.0)
            for i in range(15)
        ]
        mock_scan_market.return_value = mock_candidates

        service = IntradayScannerService()

        with patch("core.elite_selection_engine.EliteSelectionEngine.evaluate") as mock_ese, \
             patch("core.precision_entry_engine.PrecisionEntryEngine.evaluate") as mock_pee:
            def ese_side_effect(item):
                idx = int(item["Symbol"].split("_")[1].split(".")[0])
                return dict(item) if idx < 5 else None
            mock_ese.side_effect = ese_side_effect
            mock_pee.side_effect = lambda x: dict(x)

            result = service.execute_intraday_scan(timeframe="5m")

        self.assertEqual(result.get("total_universe"), 50)
        self.assertEqual(result.get("total_scanned"), 15)
        self.assertEqual(result.get("qualified_count"), 5)
        self.assertEqual(result.get("filter_rejected_count"), 10)
        self.assertEqual(result.get("no_data_count"), 35)
        self.assertEqual(result.get("rejected_count"), 45)
        self.assertEqual(10 + 35 + 5, 50)


if __name__ == "__main__":
    unittest.main()
