import os
import sys
from pathlib import Path

def get_app_data_dir() -> Path:
    """Returns the cross-platform application data directory."""
    app_name = "RAHUUL_RADAR"
    
    if sys.platform == "darwin":
        # macOS: ~/Library/Application Support/RAHUUL_RADAR
        base_dir = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        # Windows: %LOCALAPPDATA%/RAHUUL_RADAR
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            base_dir = Path(local_app_data)
        else:
            base_dir = Path.home() / "AppData" / "Local"
    else:
        # Linux / Unix: ~/.local/share/RAHUUL_RADAR
        base_dir = Path.home() / ".local" / "share"
        
    app_dir = base_dir / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_logs_dir() -> Path:
    logs_dir = get_app_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_config_dir() -> Path:
    config_dir = get_app_data_dir() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_database_dir() -> Path:
    db_dir = get_app_data_dir() / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir

def get_exports_dir() -> Path:
    exports_dir = get_app_data_dir() / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir
