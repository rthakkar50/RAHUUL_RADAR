import urllib.request
import urllib.parse
import json
from core.config_manager import ConfigManager
from utils.logger import get_logger

logger = get_logger(__name__)

class TelegramBot:
    def __init__(self):
        self.config_manager = ConfigManager()

    def _send(self, token: str, chat_id: str, message: str) -> bool:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_alert(self, symbol: str, signal: str, score: float):
        config = self.config_manager.load_config()
        token   = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")
        if not token or not chat_id:
            logger.warning("Telegram Bot Token or Chat ID not configured. Skipping alert.")
            return False

        emoji = "🟢" if "BUY" in signal else "🔴"
        if signal == "STRONG BUY":
            emoji = "🚀"

        message = (
            f"⚡ *RAHUUL RADAR ALERT* ⚡\n\n"
            f"*Symbol*: {symbol}\n"
            f"*Signal*: {emoji} {signal}\n"
            f"*Score*:  {score}\n\n"
            f"#Trading #Breakout"
        )
        return self._send(token, chat_id, message)

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

        emoji = "🚀" if signal in ("BUY", "STRONG_BUY") else "🔴"
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
        result = self._send(token, chat_id, message)
        if result:
            logger.info(f"Trade alert sent for {symbol}")
        return result
