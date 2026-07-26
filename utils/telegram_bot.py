import urllib.request
import urllib.parse
import json
import time
from core.config_manager import ConfigManager
from utils.logger import get_logger

logger = get_logger(__name__)

class TelegramBot:
    _recent_messages = {}
    _dedupe_ttl = 300  # 5 minutes deduplication window

    def __init__(self):
        self.config_manager = ConfigManager()

    @classmethod
    def clear_dedup_cache(cls):
        """Clear recent messages cache (useful for testing)."""
        cls._recent_messages.clear()

    def _send(self, token: str, chat_id: str, message: str, dedupe_key: str = None) -> bool:
        if not token or not chat_id:
            logger.warning("Telegram token or chat_id missing in _send. Skipping.")
            return False

        key = dedupe_key or hash(message)
        current_time = time.time()
        if key in TelegramBot._recent_messages:
            if current_time - TelegramBot._recent_messages[key] < TelegramBot._dedupe_ttl:
                logger.info(f"Duplicate Telegram message prevented for key: {key}")
                return True  # Treat suppressed duplicate as handled

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": str(chat_id),
            "text": message,
            "parse_mode": "Markdown"
        }).encode("utf-8")

        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(url, data=data)
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        TelegramBot._recent_messages[key] = current_time
                        return True
            except Exception as e:
                logger.warning(f"Telegram API send attempt {attempt}/3 failed: {e}")
                if attempt < 3:
                    time.sleep(0.5 * attempt)
                else:
                    logger.error(f"Failed to send Telegram message after 3 attempts. Gracefully handling failure: {e}")
        return False

    def send_alert(self, symbol: str, signal: str, score: float):
        config = self.config_manager.load_config()
        token   = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID not configured. Skipping alert.")
            return False

        emoji = "🟢" if "BUY" in signal else "🔴"
        if signal == "STRONG BUY" or signal == "STRONG_BUY":
            emoji = "🚀"

        message = (
            f"⚡ *RAHUUL RADAR ALERT* ⚡\n\n"
            f"*Symbol*: {symbol}\n"
            f"*Signal*: {emoji} {signal}\n"
            f"*Score*:  {score}\n\n"
            f"#Trading #Breakout"
        )
        dedupe_key = f"legacy_alert:{symbol}:{signal}:{score}"
        return self._send(token, chat_id, message, dedupe_key=dedupe_key)

    def send_trade_alert(self, symbol: str, signal: str, entry: float,
                         sl: float, target1: float, target2: float,
                         score: float, mode: str = "SWING") -> bool:
        """Send a rich trade alert with full entry/SL/target setup."""
        config = self.config_manager.load_config()
        token   = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            logger.warning("Telegram not configured. Skipping trade alert.")
            return False

        emoji = "🚀" if signal in ("BUY", "STRONG_BUY", "STRONG BUY") else "🔴"
        mode_tag = "⚡ F&O INTRADAY" if mode == "OPTIONS" else "📊 SWING"

        message = (
            f"{emoji} *RAHUUL RADAR — {mode_tag}*\n"
            f"{'='*30}\n"
            f"*Symbol*  : `{symbol}`\n"
            f"*Signal*  : *{signal}*\n"
            f"*Score*   : {score}\n\n"
            f"📌 *Trade Setup*\n"
            f"  Entry    : ₹{entry:.2f}\n"
            f"  Stop Loss: ₹{sl:.2f}\n"
            f"  Target 1 : ₹{target1:.2f}\n"
            f"  Target 2 : ₹{target2:.2f}\n\n"
            f"{'⚡ Buy ATM Call option.' if mode == 'OPTIONS' else '📈 Swing setup.'}\n"
            f"#RahuulRadar #{'FNO' if mode == 'OPTIONS' else 'Swing'}"
        )
        dedupe_key = f"trade_alert:{symbol}:{signal}:{entry}:{sl}"
        result = self._send(token, chat_id, message, dedupe_key=dedupe_key)
        if result:
            logger.info(f"Trade alert sent for {symbol}")
        return result

    def send_scanner_alert(self, symbol: str, signal: str, score: float, confidence: float, risk_reward: str, is_high_risk: bool = False) -> bool:
        """
        Send scanner notification exclusively for BUY, STRONG BUY, SELL, or HIGH RISK signals.
        Includes Symbol, Signal, Score, Confidence, and Risk Reward.
        """
        signal_upper = str(signal).upper().replace("_", " ")
        valid_triggers = ("BUY", "STRONG BUY", "SELL", "STRONG SELL", "HIGH RISK")
        if signal_upper not in valid_triggers and not is_high_risk:
            logger.debug(f"Signal '{signal}' for {symbol} not in notification target list. Skipping alert.")
            return False

        config = self.config_manager.load_config()
        token = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            logger.warning("Telegram not configured. Skipping scanner alert.")
            return False

        display_signal = "HIGH RISK" if (is_high_risk or signal_upper == "HIGH RISK") else signal_upper
        emoji = "🚀" if "STRONG BUY" in display_signal else ("🟢" if "BUY" in display_signal else ("⚠️" if "RISK" in display_signal else "🔴"))

        message = (
            f"⚡ *RAHUUL RADAR SCANNER ALERT* ⚡\n"
            f"{'='*30}\n"
            f"*Symbol*     : `{symbol}`\n"
            f"*Signal*     : {emoji} *{display_signal}*\n"
            f"*Score*      : {score}\n"
            f"*Confidence* : {confidence}%\n"
            f"*Risk Reward*: {risk_reward}\n"
            f"{'='*30}\n"
            f"#Trading #Scanner #RahuulRadar"
        )
        dedupe_key = f"scanner_alert:{symbol}:{display_signal}:{score}"
        return self._send(token, chat_id, message, dedupe_key=dedupe_key)

    def send_daily_summary(self, total_scanned: int, buy_count: int, sell_count: int, watch_count: int, best_trade: str, market_bias: str) -> bool:
        """
        Generate and send daily market summary report.
        """
        config = self.config_manager.load_config()
        token = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            logger.warning("Telegram not configured. Skipping daily summary.")
            return False

        message = (
            f"📊 *RAHUUL RADAR DAILY SUMMARY* 📊\n"
            f"{'='*30}\n"
            f"📈 *Market Bias*  : *{market_bias}*\n"
            f"🔍 *Total Scanned*: {total_scanned} symbols\n"
            f"{'-'*30}\n"
            f"📌 *Signal Breakdown*:\n"
            f"   🟢 BUY Count  : {buy_count}\n"
            f"   🔴 SELL Count : {sell_count}\n"
            f"   🟡 WATCH Count: {watch_count}\n\n"
            f"🏆 *Best Trade*  : `{best_trade}`\n"
            f"{'='*30}\n"
            f"#DailySummary #MarketWrap #RahuulRadar"
        )
        dedupe_key = f"daily_summary:{total_scanned}:{best_trade}:{market_bias}"
        return self._send(token, chat_id, message, dedupe_key=dedupe_key)

    def send_error_notification(self, error_type: str, details: str = "") -> bool:
        """
        Send critical error notifications. Strictly restricted to:
        Broker Disconnected, Token Expired, Scanner Failure, Database Failure.
        """
        allowed_errors = {
            "BROKER DISCONNECTED",
            "TOKEN EXPIRED",
            "SCANNER FAILURE",
            "DATABASE FAILURE"
        }
        error_key = str(error_type).strip().upper().replace("_", " ")
        if error_key not in allowed_errors:
            logger.warning(f"Error type '{error_type}' is not in allowed critical notification list. Skipping Telegram notification.")
            return False

        config = self.config_manager.load_config()
        token = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            logger.warning("Telegram not configured. Skipping error notification.")
            return False

        message = (
            f"🚨 *CRITICAL SYSTEM ALERT* 🚨\n"
            f"{'='*30}\n"
            f"⚠️ *Error*  : *{error_key}*\n"
            f"📝 *Details*: `{details or 'No additional details available.'}`\n"
            f"⏰ *Action* : Immediate inspection recommended.\n"
            f"{'='*30}\n"
            f"#SystemAlert #Error #RahuulRadar"
        )
        dedupe_key = f"error_notification:{error_key}:{details}"
        return self._send(token, chat_id, message, dedupe_key=dedupe_key)
