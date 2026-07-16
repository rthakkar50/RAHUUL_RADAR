import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "portfolio.json")

class PortfolioService:
    def __init__(self):
        self.data = self._load()
        
    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(PORTFOLIO_FILE):
            os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
            default = {
                "capital": 100000.0,
                "positions": []
            }
            try:
                with open(PORTFOLIO_FILE, "w") as f:
                    json.dump(default, f, indent=4)
            except Exception as _e:
                logging.getLogger(__name__).debug("Suppressed exception in portfolio_service.py:23: %s", _e)
            return default
            
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load portfolio: {e}")
            return {"capital": 100000.0, "positions": []}

    def get_summary(self) -> Dict[str, Any]:
        positions = self.data.get("positions", [])
        invested = sum((p.get("quantity", 0) * p.get("avg_entry", 0.0)) for p in positions if p.get("status") == "OPEN")
        total_capital = self.data.get("capital", 100000.0)
        
        # Calculate P&L
        overall_pnl = sum(((p.get("current_price", 0.0) - p.get("avg_entry", 0.0)) * p.get("quantity", 0)) for p in positions if p.get("status") == "OPEN")
        
        closed_positions = [p for p in positions if p.get("status") == "CLOSED"]
        wins = [p for p in closed_positions if (p.get("exit_price", p.get("current_price", 0.0)) - p.get("avg_entry", 0.0)) * (1 if p.get("side", "BUY") == "BUY" else -1) > 0]
        win_rate = round((len(wins) / len(closed_positions)) * 100, 1) if closed_positions else 0.0
        
        return {
            "total_capital": total_capital,
            "available_cash": total_capital - invested,
            "invested_capital": invested,
            "today_pnl": 0.0, # Requires EOD data integration
            "overall_pnl": overall_pnl,
            "open_positions": len([p for p in positions if p.get("status") == "OPEN"]),
            "closed_positions": len(closed_positions),
            "win_rate": win_rate
        }
        
    def get_positions(self) -> List[Dict[str, Any]]:
        # Hydrate dynamic fields
        positions = self.data.get("positions", [])
        hydrated = []
        for p in positions:
            q = p.get("quantity", 0)
            entry = p.get("avg_entry", 0.0)
            price = p.get("current_price", entry)
            
            p["market_value"] = q * price
            p["overall_pnl"] = (price - entry) * q
            p["today_pnl"] = 0.0
            hydrated.append(p)
        return hydrated
