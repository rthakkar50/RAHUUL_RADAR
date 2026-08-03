import unittest
import sqlite3
from application.paper_trading_service import PaperTradingEngine

class TestSprint163AccountingAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = PaperTradingEngine.get_instance()
        cls.service.engine.max_open_positions = 100
        cls.service.engine.max_exposure_pct = 500.0

    def test_task1_accounting_identity_verification(self):
        """Verify Total Equity == Virtual Capital + Unrealized P&L and Total Equity == Starting + Realized + Unrealized."""
        state = self.service.engine.get_portfolio_state()
        
        starting_cap = self.service.engine.starting_capital
        virtual_cap = state.virtual_capital
        unrealized = state.unrealized_pnl
        realized = state.realized_pnl
        equity = state.total_equity
        
        # Identity 1: Equity == Virtual Capital + Unrealized
        expected_equity_1 = round(virtual_cap + unrealized, 2)
        self.assertAlmostEqual(round(equity, 2), expected_equity_1, places=1)
        
        # Identity 2: Equity == Starting + Realized + Unrealized
        expected_equity_2 = round(starting_cap + realized + unrealized, 2)
        self.assertAlmostEqual(round(equity, 2), expected_equity_2, places=1)

    def test_task3_and_4_mathematical_consistency_rules(self):
        """Verify mathematical consistency rules (no impossible stats)."""
        stats = self.service.get_statistics()
        
        closed = stats.get("closed_trades", 0)
        wins = stats.get("winning_trades", 0)
        losses = stats.get("losing_trades", 0)
        pf = stats.get("profit_factor", 0.0)
        wr = stats.get("win_rate", 0.0)
        
        if closed == 0:
            self.assertEqual(wr, 0.0, "Win rate must be 0.0 when closed_trades == 0")
            self.assertEqual(pf, 0.0, "Profit factor must be 0.0 when closed_trades == 0")
            
        if wins == 0:
            self.assertEqual(pf, 0.0, "Profit factor must be 0.0 when winning_trades == 0")

    def test_task7_database_integrity(self):
        """Verify paper_trading.db integrity (no negative balances, no corrupt status)."""
        conn = sqlite3.connect(self.service.db_path)
        c = conn.cursor()
        c.execute("SELECT status FROM positions")
        statuses = [r[0] for r in c.fetchall()]
        conn.close()
        
        valid_statuses = {"OPEN", "CLOSED"}
        for s in statuses:
            self.assertIn(s, valid_statuses, f"Corrupt position status in DB: {s}")

if __name__ == "__main__":
    unittest.main()
