import smtplib
from email.message import EmailMessage
from .base import BaseChannel
from ..models import AlertEvent
import os

class EmailChannel(BaseChannel):
    def __init__(self):
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.username = os.environ.get("SMTP_USER", "")
        self.password = os.environ.get("SMTP_PASS", "")
        self.to_email = os.environ.get("ALERT_EMAIL", "")

    def send(self, event: AlertEvent):
        if not self.username or not self.password or not self.to_email:
            print("Email channel not configured. Skipping.")
            return

        msg = EmailMessage()
        msg.set_content(f"Symbol: {event.symbol}\nPrice: {event.price}\nEvent: {event.alert_type.value}\n\n{event.message}")
        msg['Subject'] = f"RAHUUL RADAR Alert: {event.symbol}"
        msg['From'] = self.username
        msg['To'] = self.to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email alert: {e}")
