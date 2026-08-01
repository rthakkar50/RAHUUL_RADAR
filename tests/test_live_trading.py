import unittest
from live_trading.capital_manager import CapitalPhaseManager
from live_trading.order_gate import LiveOrderGate
from live_trading.stop_condition_monitor import EmergencyStopConditionMonitor
from live_trading.live_trade_logger import LiveTradeLogger
from live_trading.live_reports import LiveReportEngine
from live_trading.live_orchestrator import LiveTradingOrchestrator
from live_trading.live_models import LiveTradeRecord


class TestLiveTradingPhase1(unittest.TestCase):

    def setUp(self):
        self.capital_manager = CapitalPhaseManager(initial_phase="Phase-1")
        self.order_gate = LiveOrderGate(self.capital_manager)
        self.stop_monitor = EmergencyStopConditionMonitor(initial_capital=10000.0)
        self.logger = LiveTradeLogger()
        self.report_engine = LiveReportEngine()
        self.orchestrator = LiveTradingOrchestrator()

    def test_task_1_capital_manager_phase_1_limits(self):
        """Phase-1 Capital & Risk Limits validation (0.5% max risk per trade)."""
        limits = self.capital_manager.get_current_limits()
        self.assertEqual(limits.capital_balance, 10000.0)
        self.assertEqual(limits.max_risk_per_trade_pct, 0.5)
        self.assertEqual(limits.max_daily_loss_pct, 1.0)
        self.assertEqual(limits.max_weekly_loss_pct, 3.0)

        # Risk validation pass (₹40 risk < ₹50 limit)
        is_ok, msg = self.capital_manager.validate_trade_risk(position_size=2000.0, stop_loss_pts=20.0, price=1000.0)
        self.assertTrue(is_ok)

        # Risk validation fail (₹100 risk > ₹50 limit)
        is_ok_fail, msg_fail = self.capital_manager.validate_trade_risk(position_size=5000.0, stop_loss_pts=20.0, price=1000.0)
        self.assertFalse(is_ok_fail)

    def test_task_2_order_gate_manual_confirmation(self):
        """Manual Confirmation Gate requirement test."""
        # Unconfirmed order blocked
        res_no_conf = self.order_gate.process_order_request(
            symbol="RELIANCE", action="BUY", quantity=10, price=2980.0, stop_loss=2935.0, manual_confirmation=False
        )
        self.assertFalse(res_no_conf["allowed"])
        self.assertIn("Manual confirmation required", res_no_conf["reason"])

        # Confirmed order allowed
        res_conf = self.order_gate.process_order_request(
            symbol="RELIANCE", action="BUY", quantity=1, price=2980.0, stop_loss=2935.0, manual_confirmation=True
        )
        self.assertTrue(res_conf["allowed"])

    def test_task_3_emergency_stop_condition_monitor(self):
        """Emergency Circuit Breaker Stop Conditions (Daily Loss > 1%, Weekly Loss > 3%)."""
        # Normal operations
        s1 = self.stop_monitor.evaluate_stop_conditions(todays_pnl=-50.0, weekly_pnl=-100.0)
        self.assertFalse(s1.is_stopped)

        # Daily loss breached (> ₹100 / 1%)
        s2 = self.stop_monitor.evaluate_stop_conditions(todays_pnl=-150.0, weekly_pnl=-150.0)
        self.assertTrue(s2.is_stopped)
        self.assertIn("Daily Loss", s2.trigger_reason)

        # System failures breached (>= 2)
        s3 = self.stop_monitor.evaluate_stop_conditions(todays_pnl=0.0, weekly_pnl=0.0, system_failures=2)
        self.assertTrue(s3.is_stopped)

    def test_task_4_live_trade_logger_18_fields(self):
        """Live Trade Audit Logger (all 18 mandatory fields recorded)."""
        rec = LiveTradeRecord(
            trade_id="LIVE-P1-001", date="2026-08-01", time="14:30:00", broker_order_id="PM-12345",
            ai_signal="BUY", confidence=92.0, entry_price=2980.0, exit_price=3040.0,
            actual_fill_price=2980.5, slippage=0.5, broker_charges=20.0, taxes=5.0,
            latency_ms=3.2, pnl=600.0, net_pnl=574.5, risk_pct=0.5, reason="Phase-1 Signal",
            market_regime="Bull Trend"
        )
        self.logger.record_live_trade(rec)
        all_trades = self.logger.get_all_live_trades()
        self.assertTrue(len(all_trades) > 0)
        self.assertEqual(all_trades[0].trade_id, "LIVE-P1-001")

    def test_task_5_reports_and_orchestrator(self):
        """Phase-1 Live Validation Orchestrator (50 trades executed with zero risk violations)."""
        summary = self.orchestrator.run_phase_1_live_validation(target_trades_count=50)
        self.assertEqual(summary.total_live_trades_completed, 50)
        self.assertEqual(summary.risk_violations_count, 0)
        self.assertEqual(summary.critical_bugs_count, 0)
        self.assertEqual(summary.audit_trail_completeness_pct, 100.0)
        self.assertIn("APPROVED FOR PHASE-2", summary.final_recommendation)


if __name__ == "__main__":
    unittest.main()
