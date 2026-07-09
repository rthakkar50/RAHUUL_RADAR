from typing import Dict, Any

class OrderExecutionAssistant:
    """
    Prepares the final trade execution summary based on the AI's verdict
    and user's capital risk preferences. Does NOT place live broker orders.
    """
    def __init__(self, capital: float = 100000.0, max_risk_pct: float = 0.01):
        self.capital = capital
        self.max_risk_pct = max_risk_pct

    def prepare_execution_card(self, symbol: str, ai_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates position sizing and prepares the final Execution Card.
        """
        if ai_output.get("verdict") == "NO TRADE":
            return {"status": "NO TRADE", "reason": ai_output.get("explanation")}

        trade_details = ai_output.get("trade_details", {})
        
        entry = trade_details.get("entry_premium", 0.0)
        sl = trade_details.get("stop_loss", 0.0)
        
        # Risk per lot (assuming standard lot sizes, e.g., NIFTY=50, BANKNIFTY=15)
        lot_size = 15 if "BANK" in symbol else 50
        risk_per_lot = (entry - sl) * lot_size
        
        max_total_risk = self.capital * self.max_risk_pct
        
        if risk_per_lot <= 0:
            suggested_lots = 0
            max_loss = 0.0
            capital_used = 0.0
        else:
            suggested_lots = int(max_total_risk // risk_per_lot)
            if suggested_lots == 0:
                suggested_lots = 1 # Minimum 1 lot if willing to exceed 1% slightly
                
            max_loss = suggested_lots * risk_per_lot
            capital_used = suggested_lots * entry * lot_size
            
        tp1 = trade_details.get("target_1", 0.0)
        expected_profit = (tp1 - entry) * lot_size * suggested_lots
        
        return {
            "status": "READY",
            "underlying": symbol,
            "direction": ai_output.get("verdict"),
            "strike": trade_details.get("strike"),
            "expiry": trade_details.get("expiry"),
            "entry_premium": entry,
            "stop_loss": sl,
            "target_1": tp1,
            "target_2": trade_details.get("target_2", 0.0),
            "risk_reward": trade_details.get("rr", "1:2"),
            "capital_used": capital_used,
            "maximum_loss": max_loss,
            "expected_profit": expected_profit,
            "suggested_lots": suggested_lots,
            "holding_time": ai_output.get("expected_holding"),
            "trade_quality": ai_output.get("quality"),
            "confidence": ai_output.get("success_probability")
        }
