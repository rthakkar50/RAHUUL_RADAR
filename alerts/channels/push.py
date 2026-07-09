import os
import requests
from .base import BaseChannel
from ..models import AlertEvent

class PushChannel(BaseChannel):
    """
    Implements mobile push notifications using Pushover as a primary provider stub.
    """
    def __init__(self):
        self.api_token = os.environ.get("PUSHOVER_API_TOKEN", "")
        self.user_key = os.environ.get("PUSHOVER_USER_KEY", "")
        
    def send(self, event: AlertEvent):
        if not self.api_token or not self.user_key:
            print("Push channel not configured. Skipping.")
            return
            
        url = "https://api.pushover.net/1/messages.json"
        
        payload = {
            "token": self.api_token,
            "user": self.user_key,
            "title": f"Radar: {event.alert_type.value} on {event.symbol}",
            "message": event.message,
        }
        
        try:
            requests.post(url, data=payload, timeout=5)
        except Exception as e:
            print(f"Failed to send Push alert: {e}")
