import threading
import logging
from typing import List
from .models import AlertEvent
from .channels.base import BaseChannel
from .channels.desktop import DesktopChannel
from .channels.email import EmailChannel
from .channels.telegram_channel import TelegramChannel
from .channels.push import PushChannel

logger = logging.getLogger("AlertEngine")

class AlertEngine:
    """
    Central dispatcher for trading alerts. Registers output channels and 
    dispatches events asynchronously to avoid blocking the main thread.
    """
    def __init__(self):
        self.channels: List[BaseChannel] = []
        
        # Auto-register all supported channels.
        # Channels will gracefully skip sending if their respective tokens are missing.
        self.register_channel(DesktopChannel())
        self.register_channel(EmailChannel())
        self.register_channel(TelegramChannel())
        self.register_channel(PushChannel())
        
    def register_channel(self, channel: BaseChannel):
        self.channels.append(channel)
        
    def dispatch(self, event: AlertEvent):
        """
        Spawns a daemon thread to dispatch the event to all registered channels concurrently.
        """
        def _send():
            for channel in self.channels:
                try:
                    channel.send(event)
                except Exception as e:
                    logger.error(f"Failed to dispatch alert to {channel.__class__.__name__}: {e}")
                    
        # Dispatch in background to ensure zero latency impact on core loops
        t = threading.Thread(target=_send, daemon=True)
        t.start()
