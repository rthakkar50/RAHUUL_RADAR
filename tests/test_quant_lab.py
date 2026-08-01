import time
import unittest
from quant_lab.analytics_engine import StrategyAnalyticsEngine
from quant_lab.equity_curve import EquityCurveEngine
from quant_lab.drawdown_engine import DrawdownEngine
from quant_lab.monte_carlo import MonteCarloEngine
from quant_lab.walk_forward import WalkForwardEngine
from quant_lab.market_regime import MarketRegimeAnalytics
from quant_lab.strategy_ranker import StrategyRanker
from quant_lab.risk_metrics import RiskMetricsEngine, AIPerformanceAnalytics
from quant_lab.research_reports import ResearchReportEngine
from quant_lab.performance_engine import HighThroughputQuantEngine


class TestQuantResearchLab(unittest.TestCase):

    def setUp(self):
        self.pnls = [1500.0, -800.0, 2200.0, 1200.0, -600.0, 1800.0, -900.0, 3100.0, 1100.0, 2500.0]
        self.analytics_engine = StrategyAnalyticsEngine()
        self.equity_engine = EquityCurveEngine()
        self.drawdown_engine = DrawdownEngine()
        self.monte_carlo_engine = MonteCarloEngine()
        self.walk_forward_engine = WalkForwardEngine()
        self.regime_analytics = MarketRegimeAnalytics()
        self.strategy_ranker = StrategyRanker()
        self.risk_engine = RiskMetricsEngine()
        self.ai_analytics = AIPerformanceAnalytics()
        self.report_engine = ResearchReportEngine()
        self.throughput_engine = HighThroughputQuantEngine()

    def test_task_1_strategy_analytics(self):
        """Task 1: Strategy Analytics metrics."""
        res = self.analytics_engine.analyze_trades(self.pnls)
        self.assertEqual(res.total_trades, 10)
        self.assertEqual(res.win_rate, 70.0)
        self.assertGreater(res.profit_factor, 1.5)
        self.assertGreater(res.expectancy, 0.0)

    def test_task_2_equity_curve(self):
        """Task 2: Daily, Weekly, Monthly Equity Curves."""
        eq = self.equity_engine.generate_equity_curves(self.pnls)
        self.assertEqual(len(eq.daily_equity), 10)
        self.assertEqual(len(eq.drawdown_curve), 10)
        self.assertEqual(len(eq.rolling_win_rate), 10)

    def test_task_3_drawdown_engine(self):
        """Task 3: Drawdown metrics and streaks."""
        dd = self.drawdown_engine.calculate_drawdown_metrics(self.pnls)
        self.assertGreaterEqual(dd.max_drawdown_pct, 0.0)
        self.assertEqual(dd.largest_winner, 3100.0)
        self.assertEqual(dd.largest_loser, -900.0)

    def test_task_4_monte_carlo_simulation(self):
        """Task 4: Monte Carlo 5,000 bootstrap simulations."""
        mc = self.monte_carlo_engine.run_simulation(self.pnls, num_simulations=5000, horizon_trades=50)
        self.assertEqual(mc.num_simulations, 5000)
        self.assertGreaterEqual(mc.prob_of_ruin_pct, 0.0)
        self.assertTrue(len(mc.confidence_interval_95) == 2)

    def test_task_5_walk_forward_analysis(self):
        """Task 5: Walk Forward In-Sample vs Out-of-Sample stability."""
        wf = self.walk_forward_engine.analyze_stability(self.pnls)
        self.assertGreater(wf.in_sample_sharpe, 0.0)
        self.assertGreater(wf.out_of_sample_sharpe, 0.0)

    def test_task_6_7_8_9_regime_ranker_risk_and_ai(self):
        """Task 6, 7, 8, 9: Regime Breakdown, Strategy Ranker, Risk Metrics & AI Analytics."""
        regimes = self.regime_analytics.analyze_regimes([{"market_regime": "Bull Trend", "pnl": 1500.0}])
        self.assertTrue(len(regimes) > 0)

        ranks = self.strategy_ranker.rank_strategies([])
        self.assertEqual(ranks[0]["rank"], 1)

        risk = self.risk_engine.calculate_risk_metrics(self.pnls)
        self.assertGreater(risk.sharpe_ratio, 0.0)
        self.assertGreater(risk.sortino_ratio, 0.0)

        ai_perf = self.ai_analytics.analyze_ai_performance([{"was_correct": True, "ai_signal": "BUY"}])
        self.assertEqual(ai_perf.ai_accuracy_pct, 100.0)

    def test_task_10_11_reports_and_charts(self):
        """Task 10 & 11: Reports & Charts payload generation."""
        report = self.report_engine.generate_report("MONTHLY", self.pnls)
        self.assertEqual(report["report_type"], "MONTHLY")
        self.assertIn("chart_payloads", report)
        self.assertIn("equity_curve", report["chart_payloads"])

    def test_task_12_large_scale_100k_trades_sub_2_seconds(self):
        """Task 12: High-Throughput Engine analyzing 100,000+ trades in <2 seconds."""
        res = self.throughput_engine.generate_large_scale_report(num_trades=100000)
        self.assertEqual(res["num_trades_processed"], 100000)
        self.assertTrue(res["is_sub_2_seconds"], f"100,000 trade analysis took {res['generation_time_sec']}s (Exceeded 2s limit!)")
        self.assertLess(res["generation_time_sec"], 2.0)


if __name__ == "__main__":
    unittest.main()
