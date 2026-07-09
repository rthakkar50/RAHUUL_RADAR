"""
Precision Entry Engine (PEE)
Finalizes the safest entry, avoiding FOMO. Outputs Entry Decision, Entry Score, and Buffer.
"""
from typing import Dict, Any

class PrecisionEntryEngine:
    def __init__(self):
        self.entry_buffer_pct = 0.002 # 0.2% buffer on breakout entries

    def evaluate(self, trade_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates an Elite Pick for optimal entry timing.
        Returns the updated dictionary with PEE parameters.
        """
        score = float(trade_dict.get("Score", 0)) # Actually TQI because ESE runs first
        vol = float(trade_dict.get("Volume", 0))
        entry_price = float(trade_dict.get("Entry", 0))
        signal = str(trade_dict.get("Signal", ""))
        
        # Risk Reward processing
        rr_str = str(trade_dict.get("Risk Reward", "1:2.0"))
        try:
            rr_val = float(rr_str.split(":")[1]) if ":" in rr_str else float(rr_str)
        except:
            rr_val = 2.0

        # Calculate Buffer (Only for breakout/breakdown signals, but we apply to all entries for safety)
        if "BUY" in signal:
            buffered_entry = entry_price * (1 + self.entry_buffer_pct)
        elif "SELL" in signal:
            buffered_entry = entry_price * (1 - self.entry_buffer_pct)
        else:
            buffered_entry = entry_price
            
        buffered_entry = round(buffered_entry, 2)
        
        # Entry Score Calculation (0-100)
        # Higher RR and High Volume lead to better immediate entries.
        entry_score = 50.0 + (min(rr_val, 4.0) * 10) + (min(vol / 200000.0, 1.0) * 10)
        
        # ESE TQI provides the baseline quality
        if score >= 90:
            entry_score += 10
            
        entry_score = min(100.0, max(0.0, entry_score))
        
        # Entry Decision Logic
        if entry_score >= 92 and rr_val >= 2.5:
            decision = "ENTER NOW"
            expected_hold = "1-2 Hours"
        elif entry_score >= 85 and rr_val >= 2.0:
            decision = "RETEST FIRST"
            expected_hold = "3-4 Hours"
        elif entry_score >= 80:
            decision = "WAIT"
            expected_hold = "Hold till EOD"
        else:
            decision = "REJECT"
            expected_hold = "N/A"
            
        # Update Dictionary
        trade_dict["Entry"] = buffered_entry
        trade_dict["Entry Score"] = round(entry_score, 1)
        trade_dict["Entry Decision"] = decision
        trade_dict["Expected Holding Time"] = expected_hold
        
        # Append Reason
        existing_reason = trade_dict.get("Reason Selected", "")
        trade_dict["Reason Selected"] = f"{existing_reason} | PEE: {decision} (Score: {trade_dict['Entry Score']})"
        
        return trade_dict if decision != "REJECT" else None
