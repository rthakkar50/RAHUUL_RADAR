import os
import time
import requests
from .base import BaseChannel
from ..models import AlertEvent

class TelegramChannel(BaseChannel):
    _recent_alerts = {}
    _dedupe_ttl = 300  # 5 minutes deduplication window

    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        
    @classmethod
    def clear_dedup_cache(cls):
        cls._recent_alerts.clear()
        
    def send(self, event: AlertEvent):
        if not self.bot_token or not self.chat_id:
            print("Telegram channel not configured. Skipping.")
            return
            
        dedupe_key = f"{event.symbol}:{event.alert_type.value}:{event.message}"
        current_time = time.time()
        if dedupe_key in TelegramChannel._recent_alerts:
            if current_time - TelegramChannel._recent_alerts[dedupe_key] < TelegramChannel._dedupe_ttl:
                print(f"Duplicate Telegram alert prevented for {event.symbol} ({event.alert_type.value}).")
                return
                
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        text = f"🚨 *{event.alert_type.value}* 🚨\n\n*Symbol*: {event.symbol}\n*Price*: {event.price}\n*Time*: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n{event.message}"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        for attempt in range(1, 4):
            try:
                resp = requests.post(url, json=payload, timeout=5)
                if resp.status_code == 200:
                    TelegramChannel._recent_alerts[dedupe_key] = current_time
                    return
            except Exception as e:
                print(f"Failed to send Telegram alert (attempt {attempt}/3): {e}")
                if attempt < 3:
                    time.sleep(0.5 * attempt)
        print("Telegram channel temporarily unavailable after retries. Handling gracefully.")
