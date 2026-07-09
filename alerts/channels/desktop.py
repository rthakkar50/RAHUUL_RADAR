import platform
import subprocess
from .base import BaseChannel
from ..models import AlertEvent

class DesktopChannel(BaseChannel):
    def send(self, event: AlertEvent):
        title = f"RAHUUL RADAR: {event.alert_type.value} - {event.symbol}"
        message = event.message
        
        system = platform.system()
        if system == "Darwin": # macOS
            apple_script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", apple_script])
        elif system == "Windows":
            # Basic fallback for windows via powershell or generic print if module missing
            # A full implementation might use plyer or win10toast
            print(f"DESKTOP NOTIFICATION [WIN]: {title} - {message}")
        else: # Linux
            subprocess.run(["notify-send", title, message])
