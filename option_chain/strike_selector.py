from typing import Dict, Optional

class StrikeSelector:
    @staticmethod
    def select_strikes(chain_data: Dict, market_trend: str) -> Dict:
        """
        Dynamically selects ATM, ITM, or OTM strikes based on V2.0 Architecture Rules.
        Default: ATM. ITM for strong trend. OTM for volume expansion + momentum breakout.
        """
        strikes = chain_data.get("strikes", [])
        if not strikes:
            return {}
            
        # Find ATM
        atm_index = 0
        for i, s in enumerate(strikes):
            if s["CE"]["type"] == "ATM":
                atm_index = i
                break
                
        # V2.0 Rule implementation
        best_ce = strikes[atm_index] # Default ATM
        best_pe = strikes[atm_index] # Default ATM
        
        if market_trend == "STRONG_BULLISH":
            # Select slightly ITM for better delta
            if atm_index > 0:
                best_ce = strikes[atm_index - 1]
        elif market_trend == "STRONG_BEARISH":
            if atm_index < len(strikes) - 1:
                best_pe = strikes[atm_index + 1]
                
        return {
            "best_ce": {
                "strike": best_ce["strike"],
                "premium": best_ce["CE"]["premium"],
                "type": best_ce["CE"]["type"]
            },
            "best_pe": {
                "strike": best_pe["strike"],
                "premium": best_pe["PE"]["premium"],
                "type": best_pe["PE"]["type"]
            }
        }
