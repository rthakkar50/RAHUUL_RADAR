import os
import requests
from .base import BaseChannel
from ..models import AlertEvent

class TelegramChannel(BaseChannel):
    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        
    def send(self, event: AlertEvent):
        if not self.bot_token or not self.chat_id:
            print("Telegram channel not configured. Skipping.")
            return
            
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        text = f"🚨 *{event.alert_type.value}* 🚨\n\n*Symbol*: {event.symbol}\n*Price*: {event.price}\n*Time*: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n{event.message}"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")
