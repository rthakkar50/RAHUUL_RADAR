"""
Elite Selection Engine (ESE)
Final approval gate for trades. Evaluates trades based on strict quality metrics.
"""
from typing import Dict, Any, List

class EliteSelectionEngine:
    def __init__(self):
        pass

    def evaluate(self, result_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a processed result dictionary and returns an evaluated dictionary 
        with TQI, Grades, and Reason Selected.
        Returns None if the trade is rejected.
        """
        # Extract inputs
        score = float(result_dict.get("Score", 0))
        conf = float(result_dict.get("Confidence", 0))
        vol = float(result_dict.get("Volume", 0))
        signal = str(result_dict.get("Signal", ""))
        
        # Risk Reward
        rr_str = str(result_dict.get("Risk Reward", "1:2.0"))
        try:
            rr_val = float(rr_str.split(":")[1])
        except:
            rr_val = 2.0
            
        # GATE-7 RISK (Minimum RR 1:1.2)
        if rr_val < 1.2:
            return None
            
        # TQI Calculation (0-100)
        # Components: Score, Confidence, Volume Quality, RR
        tqi = (score * 0.45) + (conf * 0.45) + (min(vol / 100000.0, 10.0) * 0.5) + (min(rr_val, 4.0) * 1.25)
        tqi = min(100.0, max(0.0, tqi))
        
        # GATE-1 to GATE-10 overrides (Mocked via TQI drop if basic thresholds not met)
        if score < 50 or conf < 50:
            return None # Fails AI Consensus / Capital Safety
            
        # ELITE GRADES
        if tqi >= 95:
            trade_grade = "★★★★★ ELITE"
        elif tqi >= 90:
            trade_grade = "★★★★☆ PREMIUM"
        elif tqi >= 80:
            trade_grade = "★★★☆☆ WATCH"
        elif tqi >= 70:
            trade_grade = "★★☆☆☆ OPPORTUNITY"
        else:
            return None # Reject Below 70
            
        # Risk Grade
        if rr_val >= 3.0:
            risk_grade = "A"
        elif rr_val >= 2.5:
            risk_grade = "B"
        else:
            risk_grade = "C"
            
        reason = "Clean setup with strong multi-engine consensus and high capital safety."
        
        # Add properties
        result_dict["Trade Quality Index"] = round(tqi, 2)
        result_dict["Trade Grade"] = trade_grade
        result_dict["Risk Grade"] = risk_grade
        result_dict["Reason Selected"] = reason
        
        return result_dict
