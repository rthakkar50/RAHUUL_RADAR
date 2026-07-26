"""
Sprint M7 Unit Tests — Telegram Trading Intelligence Layer
Verifies Trade Alerts, Watchlist, Open Positions, Daily Summary, Order Alerts, Security, and Rate Limiting.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
from datetime import date

from core.telegram_intelligence import TelegramIntelligence
import telegram_controller


class TestSprintM7TelegramIntelligence(unittest.TestCase):

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        self.intel = TelegramIntelligence(rate_limit_file=self.tmp_file)

    def tearDown(self):
        if os.path.exists(self.tmp_file):
            os.remove(self.tmp_file)

    # ── Module 1: High Quality Trade Alerts & Filters ───────────────────────

    def test_high_quality_trade_alert_eligibility_success(self):
        setup = {
            "decision": "STRONG BUY",
            "confidence": 88.5,
            "risk_reward": 2.5,
            "passed_quality_gates": True,
            "symbol": "RELIANCE",
            "price": 2450.0,
            "sl": 2400.0
        }
        eligible, reason = self.intel.evaluate_trade_alert_eligibility(setup)
        self.assertTrue(eligible, f"Expected eligible, got: {reason}")

    def test_low_confidence_trade_alert_rejected(self):
        setup = {
            "decision": "STRONG BUY",
            "confidence": 75.0,  # Below 85%
            "risk_reward": 2.5,
            "passed_quality_gates": True
        }
        eligible, reason = self.intel.evaluate_trade_alert_eligibility(setup)
        self.assertFalse(eligible)
        self.assertIn("Confidence", reason)

    def test_low_rr_trade_alert_rejected(self):
        setup = {
            "decision": "STRONG BUY",
            "confidence": 90.0,
            "risk_reward": 1.5,  # Below 2.0
            "passed_quality_gates": True
        }
        eligible, reason = self.intel.evaluate_trade_alert_eligibility(setup)
        self.assertFalse(eligible)
        self.assertIn("Risk/Reward", reason)

    def test_non_strong_decision_rejected(self):
        setup = {
            "decision": "BUY",  # Not STRONG BUY
            "confidence": 90.0,
            "risk_reward": 2.5,
            "passed_quality_gates": True
        }
        eligible, reason = self.intel.evaluate_trade_alert_eligibility(setup)
        self.assertFalse(eligible)
        self.assertIn("STRONG BUY", reason)

    def test_trade_alert_formatting(self):
        setup = {
            "decision": "STRONG BUY",
            "symbol": "RELIANCE.NS",
            "price": 2450.0,
            "entry_price": 2450.0,
            "sl": 2400.0,
            "target_1": 2550.0,
            "target_2": 2600.0,
            "confidence": 88.5,
            "risk_reward": 2.5,
            "reasons": {
                "trend": "Bullish breakout",
                "momentum": "RSI expansion",
                "volume": "2.4x avg",
                "structure": "HH/HL confirmed"
            }
        }
        msg = self.intel.format_trade_alert(setup)
        self.assertIn("🟢 *STRONG BUY*", msg)
        self.assertIn("RELIANCE", msg)
        self.assertIn("2,450.00", msg)
        self.assertIn("88.5%", msg)
        self.assertIn("1:2.50", msg)
        self.assertIn("• Trend: Bullish breakout", msg)

    # ── Module 2: Watchlist (/watchlist) ────────────────────────────────────

    def test_watchlist_command_ranking(self):
        msg = self.intel.get_ranked_watchlist(limit=10)
        self.assertIn("TOP 10 WATCHLIST OPPORTUNITIES", msg)
        self.assertIn("1. RELIANCE", msg)

    # ── Module 3: Open Positions (/positions) ────────────────────────────────

    def test_open_positions_report(self):
        msg = self.intel.get_open_positions_report()
        self.assertIn("OPEN POSITIONS", msg)

    # ── Module 4: Daily Summary ──────────────────────────────────────────────

    def test_daily_summary_formatting(self):
        msg = self.intel.generate_daily_summary(
            scanned_count=200, buy_count=5, sell_count=2, watch_count=10,
            avg_confidence=89.2
        )
        self.assertIn("DAILY MARKET SUMMARY", msg)
        self.assertIn("200", msg)
        self.assertIn("89.2%", msg)

    # ── Module 5: Order Alerts ───────────────────────────────────────────────

    def test_order_event_alerts(self):
        details = {"symbol": "INFY", "quantity": 10, "price": 1500.0, "action": "BUY"}
        
        exec_msg = self.intel.format_order_event_alert("ORDER_EXECUTED", details)
        self.assertIn("ORDER EXECUTED", exec_msg)
        self.assertIn("INFY", exec_msg)

        details_hit = {"symbol": "INFY", "price": 1600.0, "pnl": 1000.0}
        tgt_msg = self.intel.format_order_event_alert("TARGET_HIT", details_hit)
        self.assertIn("TARGET HIT", tgt_msg)
        self.assertIn("+₹1,000.00", tgt_msg)

        sl_msg = self.intel.format_order_event_alert("STOP_LOSS_HIT", details_hit)
        self.assertIn("STOP LOSS HIT", sl_msg)

        rej_msg = self.intel.format_order_event_alert("ORDER_REJECTED", {"symbol": "TCS", "reason": "Insufficient funds"})
        self.assertIn("ORDER REJECTED", rej_msg)

    # ── Module 6: Security (Token & Credential Redaction) ───────────────────

    def test_security_sanitization_never_exposes_tokens(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        raw_msg = f"Alert setup info: access_token: '{jwt}', api_secret='ABC123XYZ999'"
        clean_msg = TelegramIntelligence.sanitize_text(raw_msg)
        
        self.assertNotIn(jwt, clean_msg)
        self.assertIn("[TOKEN_REDACTED]", clean_msg)
        self.assertNotIn("ABC123XYZ999", clean_msg)

    # ── Module 7: Rate Limiting (Max 10 trade alerts/day) ───────────────────

    def test_rate_limiting_enforces_max_10_trade_alerts_per_day(self):
        for i in range(10):
            self.assertTrue(self.intel.can_send_trade_alert(), f"Alert {i+1} should be allowed")
            self.intel._increment_trade_alert_count()
        
        # 11th alert must be rejected by rate limiter
        self.assertFalse(self.intel.can_send_trade_alert(), "11th alert must be rejected by rate limiter")

    # ── Controller Commands Integration ──────────────────────────────────────

    def test_telegram_controller_watchlist_positions_summary_commands(self):
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        chat_id = "999888777"

        with patch("telegram_controller.send_message") as mock_send:
            telegram_controller.handle_command("/watchlist", token, chat_id)
            mock_send.assert_called_once()
            self.assertIn("WATCHLIST", mock_send.call_args[0][2])

        with patch("telegram_controller.send_message") as mock_send:
            telegram_controller.handle_command("/positions", token, chat_id)
            mock_send.assert_called_once()
            self.assertIn("OPEN POSITIONS", mock_send.call_args[0][2])

        with patch("telegram_controller.send_message") as mock_send:
            telegram_controller.handle_command("/summary", token, chat_id)
            mock_send.assert_called_once()
            self.assertIn("DAILY MARKET SUMMARY", mock_send.call_args[0][2])


if __name__ == "__main__":
    unittest.main()
