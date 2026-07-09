import time
from datetime import datetime, timedelta
from typing import Dict, Any

class TradeManager:
    """
    Manages the lifecycle, execution status, and trade timer for active setups.
    """
    def __init__(self):
        self.active_trades: Dict[str, Any] = {}

    def register_trade(self, trade_id: str, execution_card: Dict[str, Any]):
        """
        Registers a new trade and starts its timer.
        """
        now = datetime.now()
        self.active_trades[trade_id] = {
            "card": execution_card,
            "status": "WAITING",
            "prepared_time": now,
            "entered_time": None,
            "exited_time": None,
            # Signal valid for 5 minutes for scalping
            "valid_until": now + timedelta(minutes=5)
        }
        
    def get_trade_status(self, trade_id: str) -> Dict[str, Any]:
        """
        Calculates Trade Timer dynamically.
        """
        trade = self.active_trades.get(trade_id)
        if not trade:
            return {}
            
        now = datetime.now()
        prepared = trade["prepared_time"]
        valid_until = trade["valid_until"]
        
        signal_age_sec = (now - prepared).total_seconds()
        signal_age = f"{int(signal_age_sec // 60):02d}:{int(signal_age_sec % 60):02d}"
        
        is_expired = now > valid_until and trade["status"] == "WAITING"
        if is_expired:
            trade["status"] = "EXPIRED"
            
        expires_str = valid_until.strftime("%I:%M %p")
        
        return {
            "status": trade["status"],
            "signal_age": signal_age,
            "entry_window": "Expired" if is_expired else "Next 5 Minutes",
            "expires": expires_str,
            "details": trade["card"]
        }

    def update_status(self, trade_id: str, new_status: str):
        """
        Manual or automated status updates (ENTERED, TARGET1 HIT, EXITED, etc.)
        """
        trade = self.active_trades.get(trade_id)
        if trade:
            trade["status"] = new_status
            if new_status == "ENTERED":
                trade["entered_time"] = datetime.now()
            elif new_status in ["EXITED", "TARGET1 HIT", "TARGET2 HIT", "STOP LOSS HIT"]:
                if not trade["exited_time"]:
                    trade["exited_time"] = datetime.now()
