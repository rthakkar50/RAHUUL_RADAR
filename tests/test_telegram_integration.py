import os
import time
import pytest
from unittest.mock import patch, MagicMock
from utils.telegram_bot import TelegramBot
from telegram_controller import validate_user_session, handle_command

# --- Objective 1: Telegram Authentication & Session Validation ---

def test_session_validation_valid():
    config = {
        "paytm": {
            "api_key": "valid_key_123",
            "access_token": "valid_token_string_897234"
        }
    }
    is_valid, reason = validate_user_session(config)
    assert is_valid is True
    assert "validated and operational" in reason

def test_session_validation_missing_key():
    config = {"paytm": {"access_token": "token_123"}}
    with patch.dict(os.environ, {}, clear=True):
        is_valid, reason = validate_user_session(config)
        assert is_valid is False
        assert "API Key not configured" in reason

def test_session_validation_invalid_token():
    config = {
        "paytm": {
            "api_key": "valid_key_123",
            "access_token": "placeholder_token"
        }
    }
    is_valid, reason = validate_user_session(config)
    assert is_valid is False
    assert "invalid" in reason

@patch("telegram_controller.send_message")
def test_handle_login_graceful_missing_credentials(mock_send):
    """Ensure /login command gracefully handles missing credentials without ValueError crash."""
    with patch("telegram_controller.get_config", return_value={}), patch.dict(os.environ, {}, clear=True):
        handle_command("/login", "bot_token", "123456")
        mock_send.assert_called_once()
        sent_msg = mock_send.call_args[0][2]
        assert "Login Failed" in sent_msg
        assert "PAYTM_API_KEY" in sent_msg

@patch("telegram_controller.send_message")
def test_handle_login_success_with_session_check(mock_send):
    config = {
        "paytm": {
            "api_key": "valid_key_123",
            "access_token": "active_token_987654321"
        }
    }
    with patch("telegram_controller.get_config", return_value=config):
        handle_command("/login", "bot_token", "123456")
        mock_send.assert_called_once()
        sent_msg = mock_send.call_args[0][2]
        assert "PAYTM MONEY DAILY LOGIN" in sent_msg
        assert "*Current Session*: Active and Valid!" in sent_msg
        assert "login.paytmmoney.com/merchant-login" in sent_msg

@patch("telegram_controller.send_message")
def test_handle_session_command(mock_send):
    with patch("telegram_controller.get_config", return_value={"paytm": {"api_key": "k", "access_token": "valid_token_898989"}}):
        handle_command("/session", "bot_token", "123456")
        mock_send.assert_called_once()
        assert "User Session Validation" in mock_send.call_args[0][2]


# --- Objective 2: Scanner Alerts ---

@patch.object(TelegramBot, "_send", return_value=True)
def test_send_scanner_alert_buy(mock_send):
    bot = TelegramBot()
    bot.clear_dedup_cache()
    
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        result = bot.send_scanner_alert("RELIANCE", "BUY", 85.0, 92.5, "1:2.5")
        assert result is True
        mock_send.assert_called_once()
        msg = mock_send.call_args[0][2]
        assert "RAHUUL RADAR SCANNER ALERT" in msg
        assert "RELIANCE" in msg
        assert "BUY" in msg
        assert "85.0" in msg
        assert "92.5%" in msg
        assert "1:2.5" in msg

@patch.object(TelegramBot, "_send", return_value=True)
def test_send_scanner_alert_high_risk_and_strong_buy(mock_send):
    bot = TelegramBot()
    bot.clear_dedup_cache()
    
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        bot.send_scanner_alert("NIFTY", "STRONG_BUY", 95.0, 98.0, "1:3.0")
        assert "🚀 *STRONG BUY*" in mock_send.call_args[0][2]
        
        bot.clear_dedup_cache()
        bot.send_scanner_alert("HIGH_VOL_STOCK", "HIGH RISK", 60.0, 50.0, "1:1.0", is_high_risk=True)
        assert "HIGH RISK" in mock_send.call_args[0][2]

@patch.object(TelegramBot, "_send", return_value=True)
def test_send_scanner_alert_ignores_unlisted(mock_send):
    bot = TelegramBot()
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        # HOLD or NEUTRAL should be skipped unless is_high_risk=True
        result = bot.send_scanner_alert("SBIN", "NEUTRAL", 50.0, 45.0, "1:1.0")
        assert result is False
        mock_send.assert_not_called()


# --- Objective 3: Daily Summary ---

@patch.object(TelegramBot, "_send", return_value=True)
def test_send_daily_summary(mock_send):
    bot = TelegramBot()
    bot.clear_dedup_cache()
    
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        result = bot.send_daily_summary(
            total_scanned=250,
            buy_count=12,
            sell_count=8,
            watch_count=30,
            best_trade="TATAMOTORS (BUY @ 985.0)",
            market_bias="BULLISH"
        )
        assert result is True
        msg = mock_send.call_args[0][2]
        assert "RAHUUL RADAR DAILY SUMMARY" in msg
        assert "*Market Bias*  : *BULLISH*" in msg
        assert "*Total Scanned*: 250 symbols" in msg
        assert "BUY Count  : 12" in msg
        assert "SELL Count : 8" in msg
        assert "WATCH Count: 30" in msg
        assert "*Best Trade*  : `TATAMOTORS (BUY @ 985.0)`" in msg


# --- Objective 4: Error Notifications ---

@patch.object(TelegramBot, "_send", return_value=True)
def test_error_notification_allowed_types(mock_send):
    bot = TelegramBot()
    bot.clear_dedup_cache()
    
    allowed_errors = ["Broker Disconnected", "Token Expired", "Scanner Failure", "Database Failure"]
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        for err in allowed_errors:
            bot.clear_dedup_cache()
            res = bot.send_error_notification(err, f"Details for {err}")
            assert res is True
            msg = mock_send.call_args[0][2]
            assert "CRITICAL SYSTEM ALERT" in msg
            assert err.upper() in msg

@patch.object(TelegramBot, "_send", return_value=True)
def test_error_notification_ignores_minor_errors(mock_send):
    bot = TelegramBot()
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        res = bot.send_error_notification("Minor UI Warning", "Button click slow")
        assert res is False
        mock_send.assert_not_called()


# --- Objective 5: Reliability (Deduplication, Retries, Unavailable Handling) ---

@patch("urllib.request.urlopen")
def test_reliability_deduplication(mock_urlopen):
    """Verify duplicate messages are suppressed within the TTL window."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    bot = TelegramBot()
    bot.clear_dedup_cache()
    
    with patch.object(bot.config_manager, "load_config", return_value={"telegram_token": "t", "telegram_chat_id": "c"}):
        # First send hits API
        res1 = bot.send_scanner_alert("RELIANCE", "BUY", 85.0, 90.0, "1:2.0")
        assert res1 is True
        assert mock_urlopen.call_count == 1

        # Second identical send within TTL should return True without calling urlopen again
        res2 = bot.send_scanner_alert("RELIANCE", "BUY", 85.0, 90.0, "1:2.0")
        assert res2 is True
        assert mock_urlopen.call_count == 1  # Still 1!

@patch("urllib.request.urlopen")
@patch("time.sleep", return_value=None)  # avoid actual delays in test
def test_reliability_retries_on_failure(mock_sleep, mock_urlopen):
    """Verify automatic exponential backoff retry on temporary failure."""
    bot = TelegramBot()
    bot.clear_dedup_cache()

    # Fail attempt 1 & 2 with timeout exception, succeed on attempt 3
    mock_response_ok = MagicMock()
    mock_response_ok.status = 200
    mock_urlopen.side_effect = [Exception("Network Timeout"), Exception("500 Internal Error"), MagicMock(__enter__=return_value_func(mock_response_ok))]

    res = bot._send("t", "c", "Test retry message", dedupe_key="retry_key_1")
    assert res is True
    assert mock_urlopen.call_count == 3
    assert mock_sleep.call_count == 2

@patch("urllib.request.urlopen")
@patch("time.sleep", return_value=None)
def test_reliability_graceful_unavailable_handling(mock_sleep, mock_urlopen):
    """Verify graceful return when Telegram API is completely unreachable after all retries."""
    bot = TelegramBot()
    bot.clear_dedup_cache()

    mock_urlopen.side_effect = Exception("Connection Refused / Service Unavailable")
    
    res = bot._send("t", "c", "Test failure message", dedupe_key="fail_key_1")
    assert res is False
    assert mock_urlopen.call_count == 3

def return_value_func(val):
    return lambda *args, **kwargs: val
