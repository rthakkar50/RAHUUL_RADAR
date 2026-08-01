import unittest
from campaign.trade_generator import CampaignTradeGenerator
from campaign.campaign_evaluator import CampaignEvaluator
from campaign.execution_quality import ExecutionQualityEngine
from campaign.campaign_reports import CampaignReportEngine
from campaign.campaign_dashboard import CampaignDashboard
from campaign.bug_tracker import CampaignBugTracker
from campaign.campaign_runner import MasterCampaignRunner


class TestMarketValidationCampaign(unittest.TestCase):

    def setUp(self):
        self.generator = CampaignTradeGenerator()
        self.evaluator = CampaignEvaluator()
        self.quality_engine = ExecutionQualityEngine()
        self.report_engine = CampaignReportEngine()
        self.dashboard = CampaignDashboard()
        self.bug_tracker = CampaignBugTracker()
        self.runner = MasterCampaignRunner()

    def test_task_1_and_2_generate_1000_trades(self):
        """Task 1 & Task 2: 1,000 Paper Trades (500 Swing, 500 F&O) with 17 metadata fields."""
        trades = self.generator.generate_1000_campaign_trades()
        self.assertEqual(len(trades), 1000)

        swing_count = sum(1 for t in trades if "SW" in t.trade_id)
        fno_count = sum(1 for t in trades if "FNO" in t.trade_id)
        self.assertEqual(swing_count, 500)
        self.assertEqual(fno_count, 500)

        # Check 17 metadata fields on first trade
        t1 = trades[0]
        self.assertTrue(len(t1.trade_id) > 0)
        self.assertTrue(len(t1.symbol) > 0)
        self.assertGreater(t1.entry_price, 0.0)
        self.assertGreater(t1.brokerage, 0.0)
        self.assertGreater(t1.slippage, 0.0)

    def test_task_3_market_regime_validation(self):
        """Task 3: Market Regime Breakdown statistics."""
        trades = self.generator.generate_1000_campaign_trades()
        regimes = self.evaluator.evaluate_regimes(trades)
        self.assertTrue(len(regimes) >= 4)
        self.assertIn("Bull Trend", regimes)

    def test_task_4_strategy_validation(self):
        """Task 4: Strategy Validation rankings."""
        trades = self.generator.generate_1000_campaign_trades()
        strats = self.evaluator.evaluate_strategies(trades)
        self.assertTrue(len(strats) >= 3)
        self.assertEqual(strats[0]["rank"], 1)

    def test_task_5_execution_quality(self):
        """Task 5: Execution Quality (Latency, Fill Accuracy, Slippage)."""
        trades = self.generator.generate_1000_campaign_trades()
        exec_qual = self.quality_engine.analyze_execution_quality(trades)
        self.assertGreater(exec_qual.fill_accuracy_pct, 95.0)
        self.assertLess(exec_qual.avg_signal_latency_ms, 10.0)

    def test_task_6_7_8_reports_and_dashboard(self):
        """Task 6, 7, 8: Daily/Weekly Reports & Validation Dashboard payload."""
        trades = self.generator.generate_1000_campaign_trades()[:20]
        daily = self.report_engine.generate_daily_report(trades)
        self.assertEqual(daily["report_type"], "DAILY_VALIDATION")

        weekly = self.report_engine.generate_weekly_report(trades)
        self.assertEqual(weekly["report_type"], "WEEKLY_VALIDATION")

        dash = self.dashboard.get_dashboard_summary(trades)
        self.assertIn("current_win_rate_pct", dash)

    def test_task_9_bug_tracker(self):
        """Task 9: Critical Bug Tracker."""
        b1 = self.bug_tracker.log_bug("MEDIUM", "PaperTrading", "Minor slippage rounding display")
        self.assertEqual(b1.severity, "MEDIUM")
        summary = self.bug_tracker.get_summary()
        self.assertEqual(summary["MEDIUM"], 1)

    def test_task_10_master_campaign_runner_and_cto_decision(self):
        """Task 10: Master Campaign Orchestrator executing 1,000 trades & CTO Decision."""
        summary = self.runner.run_full_validation_campaign()
        self.assertEqual(summary.total_trades_completed, 1000)
        self.assertEqual(summary.swing_trades_count, 500)
        self.assertEqual(summary.fno_trades_count, 500)
        self.assertGreater(summary.win_rate_pct, 70.0)
        self.assertIn("GO FOR LIMITED LIVE TRADING", summary.cto_go_decision)


if __name__ == "__main__":
    unittest.main()
