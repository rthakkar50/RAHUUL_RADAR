import os
import json
from datetime import datetime
from config.settings import BASE_DIR

class TradeLockEngine:
    """
    Manages active trade setups to prevent overwriting Entry, SL, and Targets
    across multiple scanner runs.
    """
    def __init__(self):
        self.lock_file = os.path.join(str(BASE_DIR), 'data', 'locked_trades.json')
        self._ensure_dir()
        self.locked_trades = self._load()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.lock_file), exist_ok=True)

    def _load(self) -> dict:
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        try:
            with open(self.lock_file, 'w') as f:
                json.dump(self.locked_trades, f, indent=4)
        except Exception as e:
            print(f"Error saving locked trades: {e}")

    def get_locked_trade(self, symbol: str, mode: str) -> dict:
        """
        Returns the locked trade dict for the symbol and mode if it exists.
        """
        key = f"{symbol}_{mode}"
        return self.locked_trades.get(key)

    def lock_trade(self, symbol: str, mode: str, trade_data: dict):
        """
        Locks a new trade setup. Adds timestamp and ID.
        """
        key = f"{symbol}_{mode}"
        if "timestamp" not in trade_data:
            trade_data["timestamp"] = datetime.now().isoformat()
        if "trade_id" not in trade_data:
            trade_data["trade_id"] = f"{symbol}-{int(datetime.now().timestamp())}"
            
        self.locked_trades[key] = trade_data
        self._save()

    def release_trade(self, symbol: str, mode: str):
        """
        Removes a trade from the lock file (e.g., when closed).
        """
        key = f"{symbol}_{mode}"
        if key in self.locked_trades:
            del self.locked_trades[key]
            self._save()

    def is_signal_flipped(self, locked_signal: str, new_signal: str) -> bool:
        """
        Checks if the new signal completely flips the previous one.
        e.g., BUY to SELL or SELL to BUY.
        Does NOT flip for BUY -> STRONG_BUY or BUY -> WATCH.
        """
        locked_base = "BUY" if "BUY" in locked_signal else "SELL" if "SELL" in locked_signal else "WATCH"
        new_base = "BUY" if "BUY" in new_signal else "SELL" if "SELL" in new_signal else "WATCH"
        
        if locked_base in ["BUY", "SELL"] and new_base in ["BUY", "SELL"]:
            return locked_base != new_base
        return False
