"""Notifier implementations (email, webhook, Slack)."""
import smtplib
import logging
from email.message import EmailMessage
import requests

from .base import Notifier

logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    def __init__(self, host: str, port: int, username: str, password: str, sender: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender

    def send(self, message: str, *, subject: str = "OSINT Alert", to: str) -> None:
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = to

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            logger.info("Email alert sent to %s", to)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to send email: %s", exc)


class WebhookNotifier(Notifier):
    def __init__(self, url: str):
        self.url = url

    def send(self, message: str, **kwargs) -> None:
        payload = {"text": message}
        # Allow caller to pass a custom payload dict
        if "payload" in kwargs and isinstance(kwargs["payload"], dict):
            payload = kwargs["payload"]
        try:
            resp = requests.post(self.url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Webhook notification sent")
        except Exception as exc:  # pragma: no cover
            logger.error("Webhook failed: %s", exc)
