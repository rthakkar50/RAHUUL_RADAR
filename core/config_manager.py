import logging
import json
import os
from dotenv import load_dotenv, set_key

class ConfigManager:
    def __init__(self, filepath=None):
        from config.settings import BASE_DIR
        self.base_dir = str(BASE_DIR)
        self.env_path = os.path.join(self.base_dir, ".env")
        if filepath is None:
            self.filepath = os.path.join(self.base_dir, "config.json")
        else:
            self.filepath = filepath
            
        load_dotenv(self.env_path)
            
        self.settings = {
            "capital": 100000,
            "risk_pct": 1.0,
            "holding_days": 45,
            "yahoo_refresh": "Auto",
            "telegram_token": "",
            "telegram_chat_id": "",
            
            # SPRINT-75 Risk Management Settings
            "max_daily_loss": 5000,
            "max_open_positions": 5,
            "max_exposure": 500000,
            "broker_charges": 20,
            "slippage_pct": 0.1
        }
        self.load_config()
        
    def load_config(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as _e:
                logging.getLogger(__name__).debug("Suppressed exception in config_manager.py:40: %s", _e)
                
        # Read from environment variables, overriding config.json
        self.settings["telegram_token"] = os.environ.get("TELEGRAM_TOKEN", self.settings.get("telegram_token", ""))
        self.settings["telegram_chat_id"] = os.environ.get("TELEGRAM_CHAT_ID", self.settings.get("telegram_chat_id", ""))
        self.settings["dhan_client_id"] = os.environ.get("DHAN_CLIENT_ID", self.settings.get("dhan_client_id", ""))
        self.settings["dhan_access_token"] = os.environ.get("DHAN_ACCESS_TOKEN", self.settings.get("dhan_access_token", ""))
        
        return self.settings
                
    def save_config(self, settings_dict):
        sensitive_keys = {
            "telegram_token": "TELEGRAM_TOKEN",
            "telegram_chat_id": "TELEGRAM_CHAT_ID",
            "dhan_client_id": "DHAN_CLIENT_ID",
            "dhan_access_token": "DHAN_ACCESS_TOKEN"
        }
        
        # Don't save actual secrets to config.json. Save to .env instead.
        for key, env_var in sensitive_keys.items():
            if key in settings_dict:
                val = settings_dict.pop(key)
                if val and not val.startswith("********"):
                    if not os.path.exists(self.env_path):
                        open(self.env_path, 'a').close()
                    set_key(self.env_path, env_var, val)
                    os.environ[env_var] = val
                    self.settings[key] = val # Keep in memory
                    
        self.settings.update(settings_dict)
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        
        # Make a copy for saving to disk, without the sensitive keys
        safe_settings = self.settings.copy()
        for key in sensitive_keys:
            safe_settings.pop(key, None)
            
        with open(self.filepath, 'w') as f:
            json.dump(safe_settings, f, indent=4)
