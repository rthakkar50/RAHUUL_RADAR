import unittest
from datetime import datetime
from core.ai_exit_manager import AIExitManager, OpenPosition, ExitDecision

class TestAIExitManager(unittest.TestCase):
    def setUp(self):
        self.manager = AIExitManager()
        self.dummy_decision = ExitDecision(
            action="HOLD",
            confidence=100.0,
            exit_price=100.0,
            stop_loss=95.0,
            target_1=105.0,
            target_2=110.0,
            target_3=115.0,
            trailing_stop=98.0,
            partial_exit_percentage=0.0,
            reason="Dummy"
        )

    def test_open_position_fields_and_str(self):
        now = datetime.now()
        pos = OpenPosition(
            symbol="INFY",
            direction="BUY",
            entry_price=1500.0,
            current_price=1550.0,
            quantity=10,
            entry_time=now,
            current_pnl=3.33,
            holding_minutes=45
        )
        self.assertEqual(pos.symbol, "INFY")
        self.assertEqual(pos.direction, "BUY")
        self.assertEqual(pos.entry_price, 1500.0)
        self.assertEqual(pos.current_price, 1550.0)
        self.assertEqual(pos.quantity, 10)
        self.assertEqual(pos.entry_time, now)
        self.assertEqual(pos.current_pnl, 3.33)
        self.assertEqual(pos.holding_minutes, 45)
        
        self.assertIn("INFY", str(pos))
        self.assertIn("BUY", str(pos))

    def test_exit_decision_validation(self):
        # Valid instantiation
        decision = ExitDecision(
            action="HOLD",
            confidence=85.0,
            exit_price=100.0,
            stop_loss=95.0,
            target_1=105.0,
            target_2=110.0,
            target_3=115.0,
            trailing_stop=98.0,
            partial_exit_percentage=0.0,
            reason="Good state"
        )
        self.assertEqual(decision.action, "HOLD")
        
        # Validation fail: confidence out of bounds
        with self.assertRaises(ValueError):
            ExitDecision("HOLD", 105.0, 100.0, 95.0, 105.0, 110.0, 115.0, 98.0, 0.0, "")
            
        with self.assertRaises(ValueError):
            ExitDecision("HOLD", -5.0, 100.0, 95.0, 105.0, 110.0, 115.0, 98.0, 0.0, "")

        # Validation fail: partial exit percentage out of bounds
        with self.assertRaises(ValueError):
            ExitDecision("HOLD", 85.0, 100.0, 95.0, 105.0, 110.0, 115.0, 98.0, 120.0, "")
            
        with self.assertRaises(ValueError):
            ExitDecision("HOLD", 85.0, 100.0, 95.0, 105.0, 110.0, 115.0, 98.0, -10.0, "")

        # Validation fail: negative price field
        with self.assertRaises(ValueError):
            ExitDecision("HOLD", 85.0, -100.0, 95.0, 105.0, 110.0, 115.0, 98.0, 0.0, "")
            
        with self.assertRaises(ValueError):
            ExitDecision("HOLD", 85.0, 100.0, 95.0, 105.0, 110.0, 115.0, -98.0, 0.0, "")

    def test_serialization(self):
        now = datetime.now()
        pos = OpenPosition("INFY", "BUY", 1500.0, 1550.0, 10, now, 3.33, 45)
        pos_dict = pos.to_dict()
        self.assertEqual(pos_dict["symbol"], "INFY")
        self.assertEqual(pos_dict["entry_time"], now.isoformat())
        
        restored_pos = OpenPosition.from_dict(pos_dict)
        self.assertEqual(restored_pos.symbol, "INFY")
        self.assertEqual(restored_pos.quantity, 10)
        self.assertEqual(restored_pos.entry_time.isoformat(), now.isoformat())

        decision = ExitDecision("PARTIAL_EXIT", 90.0, 100.0, 95.0, 105.0, 110.0, 115.0, 98.0, 30.0, "Reason")
        decision_dict = decision.to_dict()
        self.assertEqual(decision_dict["action"], "PARTIAL_EXIT")
        self.assertEqual(decision_dict["partial_exit_percentage"], 30.0)
        
        restored_decision = ExitDecision.from_dict(decision_dict)
        self.assertEqual(restored_decision.action, "PARTIAL_EXIT")
        self.assertEqual(restored_decision.partial_exit_percentage, 30.0)

    def test_evaluate_position_hold(self):
        pos = OpenPosition("INFY", "BUY", 1500.0, 1520.0, 10, datetime.now(), 1.33, 30)
        decision = self.manager.evaluate_position(pos)
        self.assertEqual(decision.action, "HOLD")
        self.assertIn("No action required", decision.reason)
        # Verify calculated values are valid prices and positive
        self.assertGreater(decision.stop_loss, 0)
        self.assertGreater(decision.target_1, 0)

    def test_evaluate_position_closed(self):
        pos = OpenPosition("INFY", "BUY", 1500.0, 1520.0, 0, datetime.now(), 0.0, 30)
        decision = self.manager.evaluate_position(pos)
        self.assertEqual(decision.action, "CLOSED")
        self.assertIn("zero or negative quantity", decision.reason)

    def test_evaluate_position_review_loss(self):
        pos = OpenPosition("INFY", "BUY", 1500.0, 1200.0, 10, datetime.now(), -20.0, 30)
        decision = self.manager.evaluate_position(pos)
        self.assertEqual(decision.action, "REVIEW")
        self.assertIn("loss", decision.reason)

    def test_evaluate_position_review_time(self):
        pos = OpenPosition("INFY", "BUY", 1500.0, 1510.0, 10, datetime.now(), 0.67, 150)
        decision = self.manager.evaluate_position(pos)
        self.assertEqual(decision.action, "REVIEW")
        self.assertIn("holding time", decision.reason)

    def test_evaluate_position_review_profit(self):
        pos = OpenPosition("INFY", "BUY", 1500.0, 2000.0, 10, datetime.now(), 33.33, 30)
        decision = self.manager.evaluate_position(pos)
        self.assertEqual(decision.action, "REVIEW")
        self.assertIn("profit target reached", decision.reason)

    def test_recommend_exit(self):
        # Case HOLD
        pos_hold = OpenPosition("INFY", "BUY", 1500.0, 1520.0, 10, datetime.now(), 1.33, 30)
        self.assertEqual(self.manager.recommend_exit(pos_hold, self.dummy_decision), "HOLD")
        
        # Case PARTIAL_EXIT
        pos_partial = OpenPosition("INFY", "BUY", 1500.0, 1800.0, 10, datetime.now(), 20.0, 30)
        self.assertEqual(self.manager.recommend_exit(pos_partial, self.dummy_decision), "PARTIAL_EXIT")
        
        # Case FULL_EXIT (Profit)
        pos_full_profit = OpenPosition("INFY", "BUY", 1500.0, 2000.0, 10, datetime.now(), 33.33, 30)
        self.assertEqual(self.manager.recommend_exit(pos_full_profit, self.dummy_decision), "FULL_EXIT")

        # Case FULL_EXIT (Loss)
        pos_full_loss = OpenPosition("INFY", "BUY", 1500.0, 1200.0, 10, datetime.now(), -20.0, 30)
        self.assertEqual(self.manager.recommend_exit(pos_full_loss, self.dummy_decision), "FULL_EXIT")

        # Case REVIEW
        pos_review = OpenPosition("INFY", "BUY", 1500.0, 1510.0, 10, datetime.now(), 0.67, 150)
        self.assertEqual(self.manager.recommend_exit(pos_review, self.dummy_decision), "REVIEW")

    def test_recommend_trailing_stop_long_vs_short(self):
        # Long position trailing stop should be below current price
        pos_long = OpenPosition("INFY", "BUY", 1500.0, 1600.0, 10, datetime.now(), 6.67, 30)
        ts_long = self.manager.recommend_trailing_stop(pos_long, self.dummy_decision)
        self.assertEqual(ts_long, 1568.0) # 1600 - 2% (32.0)
        
        # Short position trailing stop should be above current price
        pos_short = OpenPosition("INFY", "SELL", 1500.0, 1400.0, 10, datetime.now(), 6.67, 30)
        ts_short = self.manager.recommend_trailing_stop(pos_short, self.dummy_decision)
        self.assertEqual(ts_short, 1428.0) # 1400 + 2% (28.0)

    def test_recommend_partial_exit_scaling(self):
        # Below 15% profit -> 0% partial exit
        pos_low = OpenPosition("INFY", "BUY", 1500.0, 1520.0, 10, datetime.now(), 5.0, 30)
        self.assertEqual(self.manager.recommend_partial_exit(pos_low, self.dummy_decision), 0.0)
        
        # 15% to 25% profit -> 30% partial exit
        pos_mid = OpenPosition("INFY", "BUY", 1500.0, 1800.0, 10, datetime.now(), 20.0, 30)
        self.assertEqual(self.manager.recommend_partial_exit(pos_mid, self.dummy_decision), 30.0)
        
        # Above 25% profit -> 50% partial exit
        pos_high = OpenPosition("INFY", "BUY", 1500.0, 1950.0, 10, datetime.now(), 28.0, 30)
        self.assertEqual(self.manager.recommend_partial_exit(pos_high, self.dummy_decision), 50.0)

if __name__ == "__main__":
    unittest.main()
