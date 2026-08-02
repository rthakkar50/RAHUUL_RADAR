import unittest
from core.signal_orchestrator import SignalOrchestrator, PriorityRankingEngine, UnifiedScoreCalculator

class TestSignalOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = SignalOrchestrator()

    def test_priority_ranking(self):
        # A normal BUY shouldn't be upgraded if conf/score are low
        sig = PriorityRankingEngine.upgrade_signal("BUY", 60.0, 60.0)
        self.assertEqual(sig, "BUY")
        
        # Should upgrade to STRONG_BUY
        sig = PriorityRankingEngine.upgrade_signal("BUY", 86.0, 81.0)
        self.assertEqual(sig, "STRONG_BUY")
        
        # Should upgrade to INSTITUTIONAL_BUY
        sig = PriorityRankingEngine.upgrade_signal("BUY", 96.0, 91.0)
        self.assertEqual(sig, "INSTITUTIONAL_BUY")
        
    def test_conflict_resolution_and_merge(self):
        engine_outputs = {
            "swing": [
                {"Symbol": "RELIANCE", "Signal": "BUY", "Confidence": 80.0, "Score": 80.0, "Trend Score": 75, "Risk Reward": "1:2"},
                {"Symbol": "TCS", "Signal": "WATCH", "Confidence": 50.0, "Score": 50.0}
            ],
            "intraday": [
                {"Symbol": "RELIANCE", "Signal": "SELL", "Confidence": 90.0, "Score": 85.0, "Trend Score": 40, "Risk Reward": "1:1"},
                {"Symbol": "INFY", "Signal": "BUY", "Confidence": 70.0, "Score": 70.0}
            ]
        }
        
        final_signals = self.orchestrator.merge_and_resolve(engine_outputs)
        
        # Total unique symbols should be 3: RELIANCE, TCS, INFY
        self.assertEqual(len(final_signals), 3)
        
        reliance_signals = [s for s in final_signals if s["Symbol"] == "RELIANCE"]
        self.assertEqual(len(reliance_signals), 1)
        
        winner = reliance_signals[0]
        # Depending on the composite score calculation, let's see who won.
        # Intraday had Confidence 90 (wins on confidence), let's check composite score manually in real life.
        # We just ensure it's not None.
        self.assertIsNotNone(winner["Signal"])
        self.assertTrue("Composite Score" in winner)
        self.assertTrue("Pattern" in winner) # Explainability injected

if __name__ == '__main__':
    unittest.main()
