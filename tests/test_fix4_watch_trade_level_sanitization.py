import unittest
from unittest.mock import MagicMock, patch
from application.swing_scanner_service import SwingScannerService
from core.models import ScanResult
from ranking.scoring_rules import SignalStrength
from core.false_signal_report import FalseSignalReport

class TestFix4WatchTradeLevelSanitization(unittest.TestCase):
    def setUp(self):
        self.service = SwingScannerService()

    def _create_mock_scan_result(self, symbol="TEST.NS", signal=SignalStrength.BUY,
                                  trend_dir="BULLISH", trend_score=25.0, mom_score=20.0,
                                  structure_score=75.0, total_score=80.0, price=100.0,
                                  reasons=None):
        if reasons is None:
            reasons = ["EMA20 above EMA50", "Price above EMA20"]
        res = ScanResult(
            symbol=symbol,
            company_name="Test Company",
            sector="Pharma",
            trend_direction=trend_dir,
            trend_score=trend_score,
            momentum_score=mom_score,
            structure_score=structure_score,
            volume_score=60.0,
            volatility_score=0.0,
            relative_strength_score=65.0,
            risk_score=50.0,
            mtf_score=80.0,
            total_score=total_score,
            price=price,
            volume=1500000.0,
            signal=signal,
            timestamp=None
        )
        setattr(res, "adjusted_score", total_score)
        setattr(res, "reasons", list(reasons))
        setattr(res, "adx_value", 28.0)
        setattr(res, "avwap_status", "Neutral")
        setattr(res, "breakdown_detail", {"atr": 2.0, "rsi": 58.0, "structure": {"type": "HH_HL"}})
        return res

    def test_case_1_policybzr_invalid_trade_levels_sanitized(self):
        """
        Invalid SELL with negative target and extreme SL downgraded to WATCH.
        Must sanitize levels to Entry = price, SL = 0.0, T1 = 0.0, T2 = 0.0, RR = '0.0'.
        """
        r = self._create_mock_scan_result(
            symbol="POLICYBZR.NS",
            signal=SignalStrength.SELL,
            trend_dir="STRONG_BEAR",
            trend_score=0.0,
            mom_score=6.25,
            structure_score=6.25,
            total_score=18.0,
            price=1166.0
        )
        r.breakdown_detail = {
            "atr": 25.0,
            "rsi": 23.5,
            "structure": {"swing_high": 1904.90, "swing_low": 1710.10}
        }

        # Pipeline returns negative target from unconstrained swing high
        pipeline_mock_res = {
            "status": "APPROVED",
            "score": 100.0,
            "recommended_entry": 1166.0,
            "stop_loss": 1904.90,
            "target_1": -311.80,
            "target_2": -1050.70,
            "risk_reward": 0.0,
            "calibrated_confidence": 92.0,
            "reasons": []
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "POLICYBZR.NS", "sector": "Fintech"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    qual = scan_out.get("qualified_results", [])
                    item = next((x for x in qual if x.get("Symbol") == "POLICYBZR.NS"), None)

                    self.assertIsNotNone(item)
                    self.assertEqual(item.get("Signal"), "WATCH")
                    self.assertEqual(float(item.get("Entry")), 1166.0)
                    self.assertEqual(float(item.get("Stop Loss")), 0.0)
                    self.assertEqual(float(item.get("Target 1")), 0.0)
                    self.assertEqual(float(item.get("Target 2")), 0.0)
                    self.assertIn(str(item.get("RR")), ["0.0", "0"])
                    self.assertIn(str(item.get("Risk Reward")), ["0.0", "0"])
                    self.assertTrue(any("Downgraded to WATCH" in r for r in item.get("_reasons", [])))

    def test_case_2_kotakbank_inverted_directional_levels_sanitized(self):
        """
        WATCH setup with Bullish trend but inverted SELL levels must have brackets sanitized to 0.0.
        """
        r = self._create_mock_scan_result(
            symbol="KOTAKBANK.NS",
            signal=SignalStrength.SELL,
            trend_dir="BULL",
            trend_score=21.0,
            mom_score=6.25,
            structure_score=10.0,
            total_score=30.0,
            price=404.0
        )
        r.breakdown_detail = {"atr": 5.0, "rsi": 40.0, "structure": {"type": "LL_LH"}}

        pipeline_mock_res = {
            "status": "APPROVED",
            "score": 55.0,
            "recommended_entry": 404.0,
            "stop_loss": 420.60,
            "target_1": 370.80,
            "target_2": 354.20,
            "risk_reward": 2.0,
            "calibrated_confidence": 50.0,
            "reasons": []
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "KOTAKBANK.NS", "sector": "Banking"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    qual = scan_out.get("qualified_results", [])
                    item = next((x for x in qual if x.get("Symbol") == "KOTAKBANK.NS"), None)

                    self.assertIsNotNone(item)
                    self.assertEqual(item.get("Signal"), "WATCH")
                    self.assertEqual(float(item.get("Stop Loss")), 0.0)
                    self.assertEqual(float(item.get("Target 1")), 0.0)
                    self.assertIn(str(item.get("RR")), ["0.0", "0"])

    def test_case_3_valid_buy_levels_remain_untouched(self):
        """Valid BUY setups must preserve their positive Entry, SL, T1, T2, RR."""
        for sym in ["DIVISLAB.NS", "LALPATHLAB.NS", "ZYDUSLIFE.NS"]:
            r = self._create_mock_scan_result(symbol=sym, signal=SignalStrength.BUY, total_score=85.0, price=1000.0)
            pipeline_mock_res = {
                "status": "APPROVED",
                "score": 85.0,
                "recommended_entry": 1000.0,
                "stop_loss": 970.0,
                "target_1": 1060.0,
                "target_2": 1090.0,
                "risk_reward": 2.0,
                "calibrated_confidence": 85.0,
                "reasons": []
            }
            with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
                with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": sym, "sector": "Pharma"}]):
                    with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                        mock_instance = MockScanner.return_value
                        mock_instance.scan_market.return_value = [r]
                        mock_instance.last_scan_stats = {}

                        scan_out = self.service.execute_swing_scan()
                        item = next((x for x in scan_out.get("qualified_results", []) if x.get("Symbol") == sym), None)
                        self.assertIsNotNone(item)
                        self.assertEqual(item.get("Signal"), "BUY")
                        self.assertEqual(float(item.get("Entry")), 1000.0)
                        self.assertEqual(float(item.get("Stop Loss")), 970.0)
                        self.assertEqual(float(item.get("Target 1")), 1060.0)
                        self.assertEqual(item.get("RR"), "1:2.0")

    def test_case_4_valid_sell_levels_remain_untouched(self):
        """Valid SELL setups must preserve their positive Entry, SL, T1, T2, RR."""
        r = self._create_mock_scan_result(symbol="TATACOMM.NS", signal=SignalStrength.SELL,
                                          trend_dir="STRONG_BEAR", trend_score=0.0, mom_score=0.0,
                                          structure_score=10.0, total_score=20.0, price=1600.0)
        pipeline_mock_res = {
            "status": "APPROVED",
            "score": 90.0,
            "recommended_entry": 1600.0,
            "stop_loss": 1650.0,
            "target_1": 1500.0,
            "target_2": 1450.0,
            "risk_reward": 2.0,
            "calibrated_confidence": 90.0,
            "reasons": []
        }
        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "TATACOMM.NS", "sector": "Telecom"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    item = next((x for x in scan_out.get("qualified_results", []) if x.get("Symbol") == "TATACOMM.NS"), None)
                    self.assertIsNotNone(item)
                    self.assertEqual(item.get("Signal"), "SELL")
                    self.assertEqual(float(item.get("Entry")), 1600.0)
                    self.assertEqual(float(item.get("Stop Loss")), 1650.0)
                    self.assertEqual(float(item.get("Target 1")), 1500.0)
                    self.assertEqual(item.get("RR"), "1:2.0")

    def test_case_5_valid_watch_reference_levels_remain_untouched(self):
        """Genuine WATCH candidates with mathematically valid brackets must not have levels wiped."""
        r = self._create_mock_scan_result(symbol="APOLLOHOSP.NS", signal=SignalStrength.WATCH,
                                          trend_dir="BULLISH", total_score=55.0, price=8889.0)
        pipeline_mock_res = {
            "status": "APPROVED",
            "score": 55.0,
            "recommended_entry": 8889.0,
            "stop_loss": 8711.22,
            "target_1": 9244.56,
            "target_2": 9422.20,
            "risk_reward": 2.0,
            "calibrated_confidence": 50.0,
            "reasons": []
        }
        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "APOLLOHOSP.NS", "sector": "Healthcare"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    item = next((x for x in scan_out.get("qualified_results", []) if x.get("Symbol") == "APOLLOHOSP.NS"), None)
                    self.assertIsNotNone(item)
                    self.assertEqual(item.get("Signal"), "WATCH")
                    self.assertEqual(float(item.get("Entry")), 8889.0)
                    self.assertEqual(float(item.get("Stop Loss")), 8711.22)
                    self.assertEqual(float(item.get("Target 1")), 9244.56)

if __name__ == '__main__':
    unittest.main()
