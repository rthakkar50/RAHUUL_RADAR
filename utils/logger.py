"""
Centralized logging configuration for RAHUUL_RADAR.
"""
import sys
import os
import re
import logging
from logging.handlers import RotatingFileHandler
from config.settings import LOG_LEVEL, LOGS_DIR

# Regex patterns for redacting sensitive authentication parameters
_SENSITIVE_PATTERNS = [
    # Match Bearer and JWT authorization headers
    (re.compile(r'(?i)\b(Bearer|JWT)\s+([a-zA-Z0-9_\-\.\+=]+)'), r'\1 ***'),
    # Match key-value assignments in strings or JSON for Access Tokens, Bearer Tokens, JWT, Passwords, API Keys, Request Tokens
    (re.compile(r'(?i)\b(access[_-]?token|bearer[_-]?token|jwt|password|passwd|pwd|api[_-]?key|apiKey|api[_-]?secret[_-]?key|request[_-]?token|requestToken|x-jwt-token)\b\s*[=:]\s*(["\']?)[a-zA-Z0-9_\-\.\+%=\/~@#\$^&*!]+\2'), r'\1=***'),
    # Match URL query parameters containing tokens or keys
    (re.compile(r'(?i)([?&])(api_key|apiKey|request_token|requestToken|access_token|accessToken|jwt)=([a-zA-Z0-9_\-\.\+%=\/~@#\$^&*!]+)'), r'\1\2=***'),
]

def redact_sensitive_data(text: str) -> str:
    """
    Automatically masks Access Tokens, Bearer Tokens, JWT, Passwords, API Keys, and Request Tokens,
    replacing sensitive values with *** while preserving useful operational logging.
    """
    if not isinstance(text, str):
        return str(text)
    redacted = text
    for pattern, replacement in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted

class SensitiveDataFilter(logging.Filter):
    """
    Automated logging filter to redact sensitive credentials from LogRecord messages before emission.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_sensitive_data(record.msg)
        if record.args:
            try:
                record.msg = record.getMessage()
                record.args = ()
                record.msg = redact_sensitive_data(record.msg)
            except Exception:
                pass
        return True

class SensitiveDataFormatter(logging.Formatter):
    """
    Automated logging formatter that masks Access Tokens, Bearer Tokens, JWT, Passwords, API Keys, and Request Tokens.
    """
    def format(self, record: logging.LogRecord) -> str:
        formatted_message = super().format(record)
        return redact_sensitive_data(formatted_message)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a standard configured logger for the given module name with automatic credential masking.
    """
    logger = logging.getLogger(name)
    
    # Avoid configuring multiple times if already set
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        logger.addFilter(SensitiveDataFilter())
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.addFilter(SensitiveDataFilter())
        
        log_dir = LOGS_DIR if 'LOGS_DIR' in globals() else os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Implement rotating logs: max 5MB per file, up to 5 backups
        fh = RotatingFileHandler(
            os.path.join(log_dir, "production.log"),
            maxBytes=5*1024*1024,
            backupCount=5
        )
        fh.setLevel(logging.INFO)
        fh.addFilter(SensitiveDataFilter())
        
        # Standard format with automated masking
        formatter = SensitiveDataFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        logger.addHandler(ch)
        logger.addHandler(fh)
        
    return logger
