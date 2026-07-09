"""
Centralized logging configuration for RAHUUL_RADAR.
"""
import sys
import logging
from config.settings import LOG_LEVEL, LOGS_DIR

def get_logger(name: str) -> logging.Logger:
    """
    Returns a standard configured logger for the given module name.
    """
    logger = logging.getLogger(name)
    
    # Avoid configuring multiple times if already set
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        
        # File handler (production logging)
        import os
        from logging.handlers import RotatingFileHandler
        log_dir = LOGS_DIR if 'LOGS_DIR' in globals() else os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Implement rotating logs: max 5MB per file, up to 5 backups
        fh = RotatingFileHandler(
            os.path.join(log_dir, "production.log"),
            maxBytes=5*1024*1024,
            backupCount=5
        )
        fh.setLevel(logging.INFO)
        
        # Standard format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        logger.addHandler(ch)
        logger.addHandler(fh)
        
    return logger
