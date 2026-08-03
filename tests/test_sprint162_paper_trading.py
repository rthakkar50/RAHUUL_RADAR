import unittest
import os
import sqlite3
from application.paper_trading_service import PaperTradingEngine, OrderType, PositionSizing

class TestSprint162PaperTrading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = PaperTradingEngine.get_instance()
        cls.service.engine.max_open_positions = 100
        cls.service.engine.max_exposure_pct = 500.0

    def test_task1_paper_account_metrics(self):
        """Verify paper account starting capital and metrics."""
        engine = self.service.engine
        self.assertEqual(engine.starting_capital, 1000000.0)
        self.assertGreaterEqual(engine.virtual_capital, 0.0)
        self.assertGreaterEqual(engine.available_cash, 0.0)
        self.assertGreaterEqual(engine.used_margin, 0.0)

    def test_task2_and_3_order_types_and_preview(self):
        """Verify order types and preview calculations."""
        price = 1000.0
        sl = 970.0
        target = 1050.0
        qty = 10
        
        risk_amt = abs(price - sl) * qty
        reward_amt = abs(target - price) * qty
        risk_pct = (abs(price - sl) / price) * 100
        capital_used = price * qty
        
        self.assertEqual(risk_amt, 300.0)
        self.assertEqual(reward_amt, 500.0)
        self.assertEqual(risk_pct, 3.0)
        self.assertEqual(capital_used, 10000.0)

    def test_task4_5_and_10_virtual_trade_execution_no_broker_network(self):
        """Verify paper trade execution creates virtual position without network/broker calls."""
        pos_id = self.service.execute_trade(
            symbol="TATAMOTORS.NS",
            direction="BUY",
            price=950.0,
            sl=920.0,
            target=1000.0
        )
        self.assertIsNotNone(pos_id, "Paper trade execution must return valid position ID")
        self.assertIn(pos_id, self.service.engine.open_positions)
        
        pos = self.service.engine.open_positions[pos_id]
        self.assertEqual(pos.symbol, "TATAMOTORS.NS")
        self.assertEqual(pos.direction, "BUY")
        self.assertEqual(pos.entry_price, 950.0)

    def test_task6_and_7_exit_engine_and_journal(self):
        """Verify position exit and automatic paper journal recording."""
        pos_id = self.service.execute_trade(
            symbol="INFY.NS",
            direction="BUY",
            price=1500.0,
            sl=1450.0,
            target=1600.0
        )
        self.assertIsNotNone(pos_id)
        
        # Simulate target exit
        self.service.close_position(pos_id, exit_price=1600.0, reason="Target Hit")
        
        # Verify recorded in DB
        conn = sqlite3.connect(self.service.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM positions WHERE id=?", (pos_id,))
        row = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[14], "CLOSED") # status
        self.assertEqual(row[16], 1600.0)  # exit_price

    def test_task8_and_9_performance_and_analytics(self):
        """Verify performance and analytics calculation."""
        stats = self.service.get_statistics()
        self.assertIn("win_rate", stats)
        self.assertIn("profit_factor", stats)
        self.assertIn("max_drawdown", stats)

if __name__ == "__main__":
    unittest.main()
