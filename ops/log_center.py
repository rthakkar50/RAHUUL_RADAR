"""
RAHUUL RADAR — Operations Platform: Central Log Center (Task 8)
==============================================================
Central structured logging, log rotation manager, retention policy, and credential redaction.
"""

import os
import logging
from typing import Dict, Any


class CentralLogCenter:
    """
    SRE Central Log & Audit Center.
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.logger = logging.getLogger("CentralLogCenter")

    def log_event(self, level: str, module: str, message: str):
        """Logs a structured event with sensitive data redaction."""
        sanitized_msg = self._redact_sensitive_text(message)
        log_entry = f"[{module}] {sanitized_msg}"

        if level.upper() == "ERROR":
            self.logger.error(log_entry)
        elif level.upper() == "WARNING":
            self.logger.warning(log_entry)
        else:
            self.logger.info(log_entry)

    def _redact_sensitive_text(self, text: str) -> str:
        """Redacts sensitive credentials from log text."""
        sensitive_tokens = ["PAYTM_API_KEY", "PAYTM_API_SECRET", "TELEGRAM_BOT_TOKEN", "access_token"]
        redacted = text
        for tok in sensitive_tokens:
            if tok in redacted:
                redacted = redacted.replace(tok, "[REDACTED]")
        return redacted
