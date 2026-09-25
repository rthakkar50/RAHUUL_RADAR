import unittest
from unittest.mock import MagicMock, patch
from application.swing_scanner_service import SwingScannerService
from core.models import ScanResult
from ranking.scoring_rules import SignalStrength
from core.false_signal_report import FalseSignalReport

class TestFix3RejectionReasonTrace(unittest.TestCase):
    def setUp(self):
        self.service = SwingScannerService()

    def _create_mock_scan_result(self, symbol="TEST.NS", signal=SignalStrength.BUY,
                                  trend_dir="BULLISH", trend_score=25.0, mom_score=20.0,
                                  structure_score=75.0, total_score=80.0, price=100.0,
                                  reasons=None):
        if reasons is None:
            reasons = ["EMA20 above EMA50", "Price above EMA20", "RSI rising"]
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
        setattr(res, "adx_value", 18.0)
        setattr(res, "avwap_status", "Neutral")
        setattr(res, "breakdown_detail", {"atr": 2.0, "rsi": 58.0, "structure": {"type": "HH_HL"}})
        return res

    def test_case_1_watch_execution_gate_rejection_trace(self):
        """
        Input reasons: ["EMA20 above EMA50", "Price above EMA20", "RSI rising", "No active signal to validate (WATCH)."]
        Expected rejection_reason: "No active signal to validate (WATCH)."
        NOT: "EMA20 above EMA50"
        """
        # We test a rejected item directly through the trace generator in execute_swing_scan
        rej_item = {
            "Symbol": "TEST_WATCH_REJ.NS",
            "Company": "Test Company",
            "Sector": "Pharma",
            "Price": 100.0,
            "Signal": "REJECTED",
            "Score": 50.0,
            "Raw Score": 50.0,
            "Confidence": 0.0,
            "Trend": "Bullish",
            "Volume": "1000000",
            "Risk Reward": "0.0",
            "RR": "0.0",
            "RS Score": 50.0,
            "RS Rank": "--",
            "OI Activity": "--",
            "Entry": 0.0,
            "Stop Loss": 0.0,
            "Target 1": 0.0,
            "Target 2": 0.0,
            "Trade Grade": "REJECTED",
            "Risk Grade": "HIGH",
            "Execution Status": "REJECTED",
            "Execution Score": 0.0,
            "Execution Reason": "No active signal to validate (WATCH).",
            "status": "REJECTED",
            "execution_time_ms": 10.0,
            "_raw_data": {"report": FalseSignalReport(status="REJECTED", reasons=["No active signal to validate (WATCH)."], confidence=0.0, score=0.0)},
            "_reasons": ["EMA20 above EMA50", "Price above EMA20", "RSI rising", "No active signal to validate (WATCH)."]
        }

        # Run post-scan qualification loop on this item
        r = self._create_mock_scan_result(symbol="TEST_WATCH_REJ.NS", signal=SignalStrength.WATCH)
        with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "TEST_WATCH_REJ.NS", "sector": "Pharma"}]):
            with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                mock_instance = MockScanner.return_value
                mock_instance.scan_market.return_value = [r]
                mock_instance.last_scan_stats = {}

                # Force process_post_scan to return rej_item
                with patch.object(self.service, 'pipeline'):
                    with patch('concurrent.futures.ThreadPoolExecutor') as MockExecutor:
                        mock_exec = MockExecutor.return_value
                        mock_future = MagicMock()
                        mock_future.result.return_value = rej_item
                        mock_exec.submit.return_value = mock_future
                        # Make as_completed yield mock_future
                        with patch('concurrent.futures.as_completed', return_value=[mock_future]):
                            scan_out = self.service.execute_swing_scan()
                            traces = scan_out.get("symbol_decision_traces", [])
                            self.assertEqual(len(traces), 1)
                            trace = traces[0]

                            self.assertEqual(trace.get("rejection_reason"), "No active signal to validate (WATCH).")
                            self.assertNotEqual(trace.get("rejection_reason"), "EMA20 above EMA50")
                            # Verify positive reasons are preserved in full reasons list
                            self.assertIn("EMA20 above EMA50", trace.get("reasons", []))
                            self.assertIn("Price above EMA20", trace.get("reasons", []))
                            self.assertIn("RSI rising", trace.get("reasons", []))

    def test_case_2_genuine_trend_rejection_trace(self):
        """
        Input reasons: ["EMA20 below EMA50", "Trend alignment failure: Buying in a BEAR trend."]
        Expected rejection_reason: "Trend alignment failure: Buying in a BEAR trend."
        """
        r = self._create_mock_scan_result(
            symbol="BEAR_TREND.NS",
            signal=SignalStrength.BUY,
            reasons=["EMA20 below EMA50"]
        )

        pipeline_mock_res = {
            "status": "REJECTED",
            "score": 30.0,
            "report": FalseSignalReport(status="REJECTED", reasons=["Trend alignment failure: Buying in a BEAR trend."], confidence=0.0, score=30.0),
            "reasons": ["Trend alignment failure: Buying in a BEAR trend."]
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "BEAR_TREND.NS", "sector": "Metal"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    traces = scan_out.get("symbol_decision_traces", [])
                    trace = next((t for t in traces if t.get("symbol") == "BEAR_TREND.NS"), None)

                    self.assertIsNotNone(trace)
                    self.assertEqual(trace.get("rejection_reason"), "Trend alignment failure: Buying in a BEAR trend.")
                    self.assertNotEqual(trace.get("rejection_reason"), "EMA20 below EMA50")
                    self.assertIn("EMA20 below EMA50", trace.get("reasons", []))

    def test_case_3_genuine_volume_rejection_trace(self):
        """
        Expected rejection_reason: "Volume confirmation failure: Low volume."
        """
        r = self._create_mock_scan_result(
            symbol="LOW_VOL.NS",
            signal=SignalStrength.BUY,
            reasons=["Supertrend Bullish", "RSI above 50"]
        )

        pipeline_mock_res = {
            "status": "REJECTED",
            "score": 30.0,
            "report": FalseSignalReport(status="REJECTED", reasons=["Volume confirmation failure: Low volume."], confidence=0.0, score=30.0),
            "reasons": ["Volume confirmation failure: Low volume."]
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "LOW_VOL.NS", "sector": "Auto"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    traces = scan_out.get("symbol_decision_traces", [])
                    trace = next((t for t in traces if t.get("symbol") == "LOW_VOL.NS"), None)

                    self.assertIsNotNone(trace)
                    self.assertEqual(trace.get("rejection_reason"), "Volume confirmation failure: Low volume.")
                    self.assertNotEqual(trace.get("rejection_reason"), "Supertrend Bullish")
                    self.assertIn("Supertrend Bullish", trace.get("reasons", []))

    def test_case_4_fix1_buy_candidates_regression(self):
        """DIVISLAB.NS and LALPATHLAB.NS must remain BUY."""
        for sym in ["DIVISLAB.NS", "LALPATHLAB.NS"]:
            r = self._create_mock_scan_result(symbol=sym, signal=SignalStrength.BUY, total_score=88.0)
            pipeline_mock_res = {
                "status": "APPROVED",
                "score": 88.0,
                "recommended_entry": 5000.0,
                "stop_loss": 4900.0,
                "target_1": 5200.0,
                "target_2": 5300.0,
                "risk_reward": 2.0,
                "calibrated_confidence": 88.0,
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

    def test_case_5_zyduslife_fix2_regression(self):
        """ZYDUSLIFE.NS from Fix #2 must remain BUY and not regress to REJECTED."""
        r = self._create_mock_scan_result(symbol="ZYDUSLIFE.NS", signal=SignalStrength.WATCH, total_score=80.0)
        r.price = 1199.0
        r.volume = 1500000.0

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

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "ZYDUSLIFE.NS", "sector": "Pharma"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    item = next((x for x in scan_out.get("qualified_results", []) if x.get("Symbol") == "ZYDUSLIFE.NS"), None)
                    self.assertIsNotNone(item)
                    self.assertEqual(item.get("Signal"), "BUY")
                    self.assertGreaterEqual(float(item.get("Confidence")), 80.0)

    def test_case_6_genuine_watch_candidate(self):
        """Genuine WATCH candidate must remain WATCH."""
        r = self._create_mock_scan_result(symbol="NEUTRAL.NS", signal=SignalStrength.WATCH,
                                          trend_dir="SIDEWAYS", trend_score=15.0, mom_score=12.0,
                                          total_score=60.0)
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

                    scan_out = self.service.execute_swing_scan()
                    item = next((x for x in scan_out.get("qualified_results", []) if x.get("Symbol") == "NEUTRAL.NS"), None)
                    self.assertIsNotNone(item)
                    self.assertEqual(item.get("Signal"), "WATCH")

    def test_case_7_genuine_sell_candidate(self):
        """Genuine SELL candidate must remain SELL."""
        r = self._create_mock_scan_result(symbol="BEAR.NS", signal=SignalStrength.SELL,
                                          trend_dir="BEAR", trend_score=5.0, mom_score=5.0,
                                          structure_score=20.0, total_score=25.0)
        setattr(r, "price_below_ema50", True)
        setattr(r, "breakdown_detail", {"atr": 2.0, "rsi": 35.0, "structure": {"type": "LH_LL"}})

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
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "BEAR.NS", "sector": "Auto"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    item = next((x for x in scan_out.get("qualified_results", []) if x.get("Symbol") == "BEAR.NS"), None)
                    self.assertIsNotNone(item)
                    self.assertIn(item.get("Signal"), ["SELL", "STRONG_SELL", "EARLY SELL"])

    def test_case_8_genuine_non_watch_rejected_candidate(self):
        """Genuine non-WATCH rejection candidate must remain REJECTED."""
        r = self._create_mock_scan_result(symbol="BAD_SECTOR.NS", signal=SignalStrength.BUY, total_score=75.0)
        pipeline_mock_res = {
            "status": "REJECTED",
            "score": 30.0,
            "report": FalseSignalReport(status="REJECTED", reasons=["Sector strength failure: Buying in a WEAK sector."], confidence=0.0, score=30.0),
            "reasons": ["Sector strength failure: Buying in a WEAK sector."]
        }

        with patch.object(self.service.pipeline, 'run', return_value=pipeline_mock_res):
            with patch('market.universe.get_nifty200_symbols', return_value=[{"symbol": "BAD_SECTOR.NS", "sector": "Auto"}]):
                with patch('application.swing_scanner_service.ScannerEngine') as MockScanner:
                    mock_instance = MockScanner.return_value
                    mock_instance.scan_market.return_value = [r]
                    mock_instance.last_scan_stats = {}

                    scan_out = self.service.execute_swing_scan()
                    qualified = scan_out.get("qualified_results", [])
                    traces = scan_out.get("symbol_decision_traces", [])

                    self.assertEqual(len(qualified), 0)
                    trace = next((t for t in traces if t.get("symbol") == "BAD_SECTOR.NS"), None)
                    self.assertIsNotNone(trace)
                    self.assertEqual(trace.get("signal"), "REJECTED")
                    self.assertEqual(trace.get("rejection_reason"), "Sector strength failure: Buying in a WEAK sector.")

if __name__ == '__main__':
    unittest.main()
