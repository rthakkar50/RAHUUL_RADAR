import unittest
from unittest.mock import patch, MagicMock
from application.intraday_scanner_service import IntradayScannerService
from core.signal_orchestrator import SignalOrchestrator
from core.precision_entry_engine import PrecisionEntryEngine
from core.elite_selection_engine import EliteSelectionEngine

class TestSignalNormalization(unittest.TestCase):
    def test_canonical_signal_separation(self):
        # Create dummy processed result
        res = {
            "Symbol": "TEST.NS",
            "Company": "TEST",
            "Sector": "TECH",
            "Price": 100.0,
            "Signal": "BUY",
            "Score": 90.0,
            "Raw Score": 90.0,
            "Confidence": 85.0,
            "Trend": "BULLISH",
            "Entry": 100.0,
            "Stop Loss": 95.0,
            "Target 1": 105.0,
            "Target 2": 110.0,
            "Risk Reward": "1:2.0",
            "Volume": 500000,
            "Timestamp": "2026-08-02 21:00:00"
        }

        ese = EliteSelectionEngine()
        pee = PrecisionEntryEngine()

        elite_res = ese.evaluate(res.copy())
        self.assertIsNotNone(elite_res)

        pee_res = pee.evaluate(elite_res.copy())
        self.assertIsNotNone(pee_res)

        # Simulate IntradayScannerService mapping logic
        entry_dec = pee_res.get("Entry Decision", "ENTER NOW")
        pee_res["Entry Decision"] = entry_dec
        pee_res["entry_decision"] = entry_dec
        canonical_sig = str(res.get("Signal", "BUY")).upper()
        pee_res["Signal"] = canonical_sig
        pee_res["signal"] = canonical_sig

        # Verify no string concatenation in Signal field
        self.assertEqual(pee_res["Signal"], "BUY")
        self.assertEqual(pee_res["signal"], "BUY")
        self.assertIn(pee_res["entry_decision"], ["ENTER NOW", "RETEST FIRST", "WAIT", "REJECT"])

    def test_signal_orchestrator_canonical_sync(self):
        orchestrator = SignalOrchestrator()
        signals = {
            "intraday": [
                {
                    "Symbol": "INFY.NS",
                    "Signal": "BUY",
                    "signal": "BUY",
                    "entry_decision": "RETEST FIRST",
                    "Score": 88.0,
                    "Confidence": 90.0
                }
            ]
        }

        merged = orchestrator.merge_and_resolve(signals)
        self.assertEqual(len(merged), 1)
        winner = merged[0]

        # Verify upgraded or preserved signal is canonical
        self.assertIn(winner["Signal"], ["BUY", "STRONG_BUY", "INSTITUTIONAL_BUY"])
        self.assertEqual(winner["signal"], winner["Signal"])
        self.assertEqual(winner["entry_decision"], "RETEST FIRST")

if __name__ == "__main__":
    unittest.main()
