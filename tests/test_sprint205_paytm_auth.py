import unittest
from unittest.mock import patch, MagicMock
from market.paytm_auth_manager import PaytmAuthManager
from market.paytm_provider import PaytmMoneyProvider
import telegram_controller

class TestSprint205PaytmAuth(unittest.TestCase):

    def setUp(self):
        self.auth_mgr = PaytmAuthManager.get_instance()

    def test_auth_manager_singleton(self):
        inst1 = PaytmAuthManager.get_instance()
        inst2 = PaytmAuthManager.get_instance()
        self.assertIs(inst1, inst2)

    def test_unauthenticated_status(self):
        with patch.object(self.auth_mgr, 'get_valid_jwt', return_value=None):
            self.assertFalse(self.auth_mgr.is_authenticated())
            st = self.auth_mgr.get_auth_status()
            self.assertEqual(st["login_status"], "Login Required")
            self.assertTrue(st["fallback_active"])

    def test_refresh_token_failure_handled_gracefully(self):
        with patch.object(self.auth_mgr, 'notify_telegram_login_required') as mock_notify:
            success, msg = self.auth_mgr.refresh_token()
            self.assertFalse(success)
            self.assertIn("Login Required", msg)
            mock_notify.assert_called_once()

    def test_paytm_provider_connect_uses_auth_manager(self):
        provider = PaytmMoneyProvider()
        with patch.object(self.auth_mgr, 'is_authenticated', return_value=False), \
             patch.object(self.auth_mgr, 'refresh_token', return_value=(False, "Failed")):
            connected = provider.connect()
            self.assertFalse(connected)
            self.assertFalse(provider.is_connected())
            self.assertTrue(getattr(provider, '_use_fallback_only', False))

    def test_telegram_auth_commands(self):
        intel = telegram_controller.intel
        with patch.object(intel, 'get_auth_status_report', return_value="AUTH_STATUS_OK"), \
             patch.object(intel, 'trigger_paytm_token_refresh', return_value="REFRESH_OK"), \
             patch.object(intel, 'get_login_status_report', return_value="LOGIN_OK"):
            
            with patch("telegram_controller.is_authorized", return_value=True), \
                 patch("telegram_controller.send_message") as mock_send:
                
                telegram_controller.handle_text_command("/authstatus", "dummy_token", "12345")
                mock_send.assert_called_with("dummy_token", "12345", "AUTH_STATUS_OK")
                
                telegram_controller.handle_text_command("/refreshtoken", "dummy_token", "12345")
                mock_send.assert_called_with("dummy_token", "12345", "REFRESH_OK")
                
                telegram_controller.handle_text_command("/loginstatus", "dummy_token", "12345")
                mock_send.assert_called_with("dummy_token", "12345", "LOGIN_OK")

if __name__ == "__main__":
    unittest.main()
