"""
Application settings and constants for RAHUUL_RADAR.
"""
import os
from pathlib import Path

import sys

# Base Paths for Persistent Data (DB, config, logs)
if getattr(sys, 'frozen', False):
    if sys.platform == "darwin":
        BASE_DIR = Path(sys.executable).parent.parent.parent.parent
    else:
        BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = str(BASE_DIR)
    return os.path.join(base_path, relative_path)

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Application Metadata
APP_NAME = "RAHUUL_RADAR"
APP_VERSION = "1.0.0"
