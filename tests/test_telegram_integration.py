"""
Sprint M6 Unit Tests — Telegram Bot Controller & Paytm Auto-Refresh Logic
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import json
import time

import telegram_controller
from broker.paytm.paytm_broker import PaytmBroker


class TestSprintM6TelegramAndTokenRefresh(unittest.TestCase):

    def test_send_message_sanitizes_tokens(self):
        """Rule 6: Never send access token or refresh token to Telegram."""
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        chat_id = "999888777"
        raw_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        msg_with_token = f"Here is your secret session: {raw_jwt}"

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            telegram_controller.send_message(token, chat_id, msg_with_token)

            # Check that urllib received data with sanitized text
            args, kwargs = mock_urlopen.call_args
            req = args[0]
            data_bytes = req.data.decode("utf-8")
            import urllib.parse
            unquoted_data = urllib.parse.unquote(data_bytes)
            self.assertNotIn(raw_jwt, unquoted_data)
            self.assertIn("[TOKEN_REDACTED]", unquoted_data)

    def test_token_command_deprecated_and_sanitized(self):
        """Rule 5 & 6: Deprecate manual /token and ensure no tokens sent."""
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        chat_id = "999888777"

        with patch("telegram_controller.send_message") as mock_send:
            telegram_controller.handle_command("/token eyJ0eXAi...", token, chat_id)
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            text = args[2]
            self.assertIn("Deprecation Warning", text)
            self.assertNotIn("eyJ0eXAi...", text)

    def test_ping_command(self):
        """Requirement 4: /ping command returns latency and server status."""
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        chat_id = "999888777"

        with patch("telegram_controller.send_message") as mock_send:
            telegram_controller.handle_command("/ping", token, chat_id)
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            text = args[2]
            self.assertIn("Pong!", text)
            self.assertIn("Latency", text)
            self.assertIn("Active & Operational", text)

    def test_logs_command(self):
        """Requirement 4: /logs command returns recent log output."""
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        chat_id = "999888777"

        with patch("telegram_controller.send_message") as mock_send:
            telegram_controller.handle_command("/logs", token, chat_id)
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            text = args[2]
            self.assertIn("Recent System Logs", text)

    def test_refresh_command_retries_and_succeeds(self):
        """Requirement 1, 2, 3: Automatic Paytm access-token refresh with retries."""
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        chat_id = "999888777"

        with patch("telegram_controller.auto_refresh_paytm_token") as mock_auto:
            mock_auto.return_value = (True, "Token session validated & refreshed on attempt 1/3.")
            with patch("telegram_controller.send_message") as mock_send:
                telegram_controller.handle_command("/refresh", token, chat_id)
                self.assertEqual(mock_send.call_count, 2)
                last_call_text = mock_send.call_args_list[1][0][2]
                self.assertIn("Automatic Token Refresh Succeeded!", last_call_text)

    def test_auto_refresh_paytm_token_retry_3_times_on_failure(self):
        """Requirement 3: Retry 3 times if refresh fails."""
        with patch("telegram_controller.get_config") as mock_cfg:
            mock_cfg.return_value = {
                "paytm": {
                    "api_key": "TEST_KEY",
                    "api_secret": "TEST_SECRET",
                    "read_access_token": "TEST_READ_TOKEN"
                }
            }
            with patch("urllib.request.urlopen", side_effect=Exception("Connection refused")):
                success, msg = telegram_controller.auto_refresh_paytm_token(max_retries=3)
                self.assertFalse(success)
                self.assertIn("failed after 3 attempts", msg)

    def test_paytm_broker_auto_refresh_token_retries(self):
        """PaytmBroker.auto_refresh_token retry logic test."""
        with patch("broker.paytm.paytm_broker.PaytmMoneyProvider"):
            with patch.object(PaytmBroker, "connect", return_value=True):
                broker = PaytmBroker()
                with patch.object(broker, "refresh_token", side_effect=Exception("Token expired")):
                    res = broker.auto_refresh_token(max_retries=3)
                    self.assertFalse(res)


if __name__ == "__main__":
    unittest.main()
