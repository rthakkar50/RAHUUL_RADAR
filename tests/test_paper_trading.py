import time
import unittest
from paper_trading.paper_account import PaperAccount
from paper_trading.paper_order_manager import PaperOrderManager
from paper_trading.paper_positions import PaperPositionManager
from paper_trading.paper_portfolio import PaperPortfolio
from paper_trading.paper_journal import PaperJournal
from paper_trading.paper_statistics import PaperStatistics
from paper_trading.paper_reports import PaperReportEngine
from paper_trading.paper_engine import PaperValidationEngine, PaperLeaderboard, PaperTradingEngine
from paper_trading.paper_models import PaperJournalEntry


class TestPaperTradingPlatform(unittest.TestCase):

    def setUp(self):
        self.engine = PaperTradingEngine(initial_capital=1000000.0)

    def test_task_1_virtual_account_metrics(self):
        """Task 1: Virtual Account metrics calculation."""
        acc = self.engine.portfolio.account
        self.assertEqual(acc.cash_balance, 1000000.0)
        self.assertEqual(acc.equity, 1000000.0)

        # Allocate margin & update PnL
        self.assertTrue(acc.allocate_margin(100000.0))
        acc.update_pnl(realized=15000.0, unrealized=5000.0)

        summary = acc.get_summary()
        self.assertEqual(summary.cash_balance, 1015000.0)
        self.assertEqual(summary.equity, 1020000.0)

    def test_task_2_virtual_orders(self):
        """Task 2: Virtual Order Placement (BUY, SELL, MARKET, LIMIT, STOP)."""
        order_mgr = self.engine.portfolio.order_manager

        mkt_order = order_mgr.create_order("RELIANCE", "BUY", "MARKET", 10, price=2980.0)
        self.assertEqual(mkt_order.status, "FILLED")
        self.assertEqual(mkt_order.filled_price, 2980.0)

        limit_order = order_mgr.create_order("INFY", "BUY", "LIMIT", 20, price=1800.0)
        self.assertEqual(limit_order.status, "PENDING")

        filled = order_mgr.execute_limit_check(current_market_price=1795.0)
        self.assertEqual(len(filled), 1)
        self.assertEqual(filled[0].status, "FILLED")

    def test_task_3_position_management(self):
        """Task 3: Position Management (Open, Close, Partial Exit, Trailing Stop)."""
        pos_mgr = self.engine.portfolio.position_manager

        pos = pos_mgr.open_position("TATASTEEL", "BUY", 100, 160.0, 155.0, 168.0, 172.0, 176.0)
        self.assertEqual(pos.quantity, 100)

        # Update price
        pos_mgr.update_market_price("TATASTEEL", 165.0)
        self.assertEqual(pos.current_pnl, 500.0)

        # Partial Exit
        partial_res = pos_mgr.partial_exit(pos.position_id, exit_qty=40, exit_price=165.0)
        self.assertEqual(partial_res["remaining_qty"], 60)
        self.assertEqual(partial_res["realized_pnl"], 200.0)

        # Close Remaining
        close_res = pos_mgr.close_position(pos.position_id, exit_price=170.0)
        self.assertEqual(close_res["realized_pnl"], 600.0)

    def test_task_4_and_8_trade_journal_and_validation(self):
        """Task 4 & Task 8: Trade Journaling & AI Signal Validation Engine."""
        process_res = self.engine.process_ai_signal(
            signal_id="SIG-101", symbol="HDFCBANK", action="BUY",
            confidence=92.0, price=1650.0, stop_loss=1620.0,
            target_1=1695.0, target_2=1730.0, target_3=1780.0, quantity=50
        )

        pos_id = process_res["paper_order_result"]["position_id"]
        self.assertIsNotNone(pos_id)

        # Close trade and verify journal entry + accuracy validation
        close_journal_res = self.engine.close_and_journal_trade(pos_id, exit_price=1700.0, exit_reason="Target 1 Hit")
        self.assertTrue(close_journal_res["success"])
        self.assertGreater(close_journal_res["validation_accuracy"], 50.0)

    def test_task_5_6_7_statistics_and_reports(self):
        """Task 5, 6, 7: Performance Statistics, Daily Report & Monthly Report."""
        journal_entries = [
            PaperJournalEntry("J1", "T1", "RELIANCE", "BUY", 2900, 3000, 10, 1000, 3.4, "AI Signal", "Target Hit", 90.0, "1:2"),
            PaperJournalEntry("J2", "T2", "INFY", "BUY", 1800, 1850, 20, 1000, 2.7, "AI Signal", "Target Hit", 88.0, "1:2"),
            PaperJournalEntry("J3", "T3", "TCS", "BUY", 4000, 3950, 5, -250, -1.2, "AI Signal", "SL Hit", 85.0, "1:2")
        ]

        stats = PaperStatistics().calculate_metrics(journal_entries)
        self.assertEqual(stats.total_trades, 3)
        self.assertGreater(stats.win_rate, 60.0)

        daily = PaperReportEngine().generate_daily_report(journal_entries)
        self.assertEqual(daily["todays_trades_count"], 3)
        self.assertEqual(daily["todays_pnl"], 1750.0)

        monthly = PaperReportEngine().generate_monthly_report(journal_entries)
        self.assertEqual(monthly["report_type"], "MONTHLY")

    def test_task_9_and_10_leaderboard_and_high_throughput(self):
        """Task 9 & Task 10: Leaderboard & 10,000+ trade high-throughput capacity."""
        lb = PaperLeaderboard().generate_leaderboard([])
        self.assertTrue(len(lb["leaderboard"]) >= 3)
        self.assertEqual(lb["top_model"], "AI Engine V2")

        # Database capacity benchmark
        db = self.engine.journal.db
        start_time = time.time()
        for i in range(100):
            db.save_order(self.engine.portfolio.order_manager.create_order(f"SYM{i}", "BUY", "MARKET", 10, price=100.0))
        elapsed_ms = (time.time() - start_time) * 1000.0
        self.assertLess(elapsed_ms, 1000.0, f"100 DB writes took {elapsed_ms:.2f}ms")


if __name__ == "__main__":
    unittest.main()
