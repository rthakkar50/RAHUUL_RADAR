from typing import Dict

class IVAnalyzer:
    @staticmethod
    def analyze(chain_data: Dict) -> Dict:
        """
        Analyzes Implied Volatility for Risk Assessment (IV Crush risk).
        """
        strikes = chain_data.get("strikes", [])
        if not strikes:
            return {}
            
        atm_strike = None
        for s in strikes:
            if s["CE"]["type"] == "ATM":
                atm_strike = s
                break
                
        if not atm_strike:
            return {"iv_risk": "UNKNOWN"}
            
        avg_iv = (atm_strike["CE"]["iv"] + atm_strike["PE"]["iv"]) / 2
        
        iv_risk = "LOW"
        if avg_iv > 30:
            iv_risk = "HIGH (IV Crush Risk)"
        elif avg_iv > 20:
            iv_risk = "MEDIUM"
            
        return {
            "atm_iv": round(avg_iv, 2),
            "iv_risk": iv_risk
        }
