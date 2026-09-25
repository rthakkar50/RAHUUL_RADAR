import unittest
from unittest.mock import MagicMock, patch
from application.swing_scanner_service import SwingScannerService
from core.models import ScanResult
from ranking.scoring_rules import SignalStrength
from core.false_signal_report import FalseSignalReport

class TestFix2WatchRejection(unittest.TestCase):
    def setUp(self):
        self.service = SwingScannerService()

    def _create_mock_scan_result(self, symbol="TEST.NS", signal=SignalStrength.WATCH,
                                  trend_dir="BULLISH", trend_score=25.0, mom_score=20.0,
                                  structure_score=75.0, total_score=80.0, price=100.0):
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
        setattr(res, "reasons", ["EMA20 above EMA50", "Supertrend Bullish", "ADX < 20 Sideways Filter: Downgrading BUY to WATCH."])
        setattr(res, "adx_value", 18.0)
        setattr(res, "avwap_status", "Neutral")
        setattr(res, "breakdown_detail", {"atr": 2.0, "rsi": 58.0, "structure": {"type": "HH_HL"}})
        return res

    def test_watch_execution_gate_rejection_does_not_abort_scanner(self):
        """
        When upstream decision is WATCH, FalseSignalDetector produces:
        status='REJECTED', reasons=['No active signal to validate (WATCH).'].
        SwingScannerService must NOT fatally reject the asset for screening.
        """
        r = self._create_mock_scan_result(symbol="ZYDUSLIFE.NS", signal=SignalStrength.WATCH, total_score=80.0)

        # Mock MasterSignalPipeline to return the exact execution-gate rejection for WATCH
        watch_rejection_report = FalseSignalReport(
            status="REJECTED",
            reasons=["No active signal to validate (WATCH)."],
            confidence=80.0,
            score=40.0
        )
        pipeline_mock_res = {
            "status": "REJECTED",
            "score": 40.0,
            "report": watch_rejection_report,
            "reasons": ["No active signal to validate (WATCH)."]
        }

        # Extract process_post_scan through a mock or by running scan with controlled data
        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            # We simulate the exact process_post_scan logic using an isolated execution
            # by executing on a single stock list
            r.price = 1199.0
            r.volume = 1500000.0
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "ZYDUSLIFE.NS", "sector": "Pharma"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_output = self.service.execute_swing_scan()
                    
                    qualified = scan_output.get("qualified_results", [])
                    symbols_qual = [item.get("Symbol") for item in qualified]
                    
                    # ZYDUSLIFE.NS must NOT be discarded
                    self.assertIn("ZYDUSLIFE.NS", symbols_qual)
                    
                    zydus_item = next(item for item in qualified if item.get("Symbol") == "ZYDUSLIFE.NS")
                    # Dual scoring: Bullish score=80, Bearish score=0 -> delta=+80 >= 10 -> BUY!
                    self.assertEqual(zydus_item.get("Signal"), "BUY")
                    self.assertNotEqual(zydus_item.get("status"), "REJECTED")
                    self.assertGreater(float(zydus_item.get("Entry")), 0.0)
                    self.assertGreater(float(zydus_item.get("Stop Loss")), 0.0)
                    self.assertGreater(float(zydus_item.get("Target 1")), 0.0)

    def test_genuine_pipeline_rejection_unrelated_to_watch_is_preserved(self):
        """
        When MasterSignalPipeline produces a genuine rejection (e.g. Trend alignment failure),
        SwingScannerService must still fatally reject the asset.
        """
        r = self._create_mock_scan_result(symbol="BADTREND.NS", signal=SignalStrength.BUY, total_score=75.0)

        genuine_rejection_report = FalseSignalReport(
            status="REJECTED",
            reasons=["Trend alignment failure: Buying in a BEAR trend."],
            confidence=50.0,
            score=30.0
        )
        pipeline_mock_res = {
            "status": "REJECTED",
            "score": 30.0,
            "report": genuine_rejection_report,
            "reasons": ["Trend alignment failure: Buying in a BEAR trend."]
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "BADTREND.NS", "sector": "Auto"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_output = self.service.execute_swing_scan()
                    qualified = scan_output.get("qualified_results", [])
                    traces = scan_output.get("symbol_decision_traces", [])

                    # Must NOT be qualified
                    self.assertEqual(len(qualified), 0)

                    # Must be logged as REJECTED in decision traces
                    bad_trace = next((t for t in traces if t.get("symbol") == "BADTREND.NS"), None)
                    self.assertIsNotNone(bad_trace)
                    self.assertEqual(bad_trace.get("signal"), "REJECTED")
                    self.assertFalse(bad_trace.get("accepted"))

    def test_genuine_watch_candidate_qualifies_as_watch(self):
        """
        An asset where dual scoring produces WATCH (neutral delta) must qualify as WATCH,
        and not be discarded.
        """
        # Bullish score 50, Bearish score 50 -> delta = 0 -> WATCH
        r = self._create_mock_scan_result(symbol="NEUTRAL.NS", signal=SignalStrength.WATCH,
                                          trend_dir="SIDEWAYS", trend_score=15.0, mom_score=12.0,
                                          total_score=62.0)
        setattr(r, "adjusted_score", 62.0)

        watch_rejection_report = FalseSignalReport(
            status="REJECTED",
            reasons=["No active signal to validate (WATCH)."],
            confidence=60.0,
            score=50.0
        )
        pipeline_mock_res = {
            "status": "REJECTED",
            "score": 50.0,
            "report": watch_rejection_report,
            "reasons": ["No active signal to validate (WATCH)."]
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "NEUTRAL.NS", "sector": "Metal"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_output = self.service.execute_swing_scan()
                    qualified = scan_output.get("qualified_results", [])
                    neutral_item = next((item for item in qualified if item.get("Symbol") == "NEUTRAL.NS"), None)

                    self.assertIsNotNone(neutral_item)
                    self.assertEqual(neutral_item.get("Signal"), "WATCH")
                    self.assertNotEqual(neutral_item.get("status"), "REJECTED")

    def test_genuine_sell_candidate(self):
        """
        An asset where dual scoring produces SELL (strongly negative delta)
        must qualify as SELL and remain unaffected.
        """
        # Bullish score 20, Bearish score 75 -> delta = -55 <= -10 -> SELL
        r = self._create_mock_scan_result(symbol="BEARISH.NS", signal=SignalStrength.SELL,
                                          trend_dir="BEAR", trend_score=5.0, mom_score=5.0,
                                          structure_score=20.0, total_score=25.0)
        setattr(r, "adjusted_score", 25.0)
        setattr(r, "price_below_ema50", True)
        setattr(r, "breakdown_detail", {"atr": 2.0, "rsi": 35.0, "structure": {"type": "LH_LL"}})

        # Mock approved SELL from pipeline
        pipeline_mock_res = {
            "status": "APPROVED",
            "score": 75.0,
            "recommended_entry": 100.0,
            "stop_loss": 102.0,
            "target_1": 96.0,
            "target_2": 94.0,
            "risk_reward": 2.0,
            "calibrated_confidence": 75.0,
            "reasons": []
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "BEARISH.NS", "sector": "Auto"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_output = self.service.execute_swing_scan()
                    qualified = scan_output.get("qualified_results", [])
                    sell_item = next((item for item in qualified if item.get("Symbol") == "BEARISH.NS"), None)

                    self.assertIsNotNone(sell_item)
                    self.assertIn(sell_item.get("Signal"), ["SELL", "STRONG_SELL", "EARLY SELL"])
                    self.assertNotEqual(sell_item.get("status"), "REJECTED")

    def test_fix1_buy_candidates_regression(self):
        """
        Verify that DIVISLAB.NS and LALPATHLAB.NS produce BUY results,
        confirming that Fix #1 behavior is completely preserved.
        """
        for sym, score_val in [("DIVISLAB.NS", 89.0), ("LALPATHLAB.NS", 88.0)]:
            r = self._create_mock_scan_result(symbol=sym, signal=SignalStrength.BUY,
                                              trend_dir="BULL", trend_score=25.0, mom_score=22.0,
                                              structure_score=85.0, total_score=score_val)
            setattr(r, "adjusted_score", score_val)

            pipeline_mock_res = {
                "status": "APPROVED",
                "score": score_val,
                "recommended_entry": 5000.0,
                "stop_loss": 4900.0,
                "target_1": 5200.0,
                "target_2": 5300.0,
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

                        scan_output = self.service.execute_swing_scan()
                        qualified = scan_output.get("qualified_results", [])
                        item = next((x for x in qualified if x.get("Symbol") == sym), None)

                        self.assertIsNotNone(item, f"{sym} should be qualified")
                        self.assertEqual(item.get("Signal"), "BUY", f"{sym} must remain BUY")
                        self.assertNotEqual(item.get("status"), "REJECTED")

if __name__ == '__main__':
    unittest.main()
