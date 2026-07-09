from typing import Dict

class OIAnalyzer:
    @staticmethod
    def analyze(chain_data: Dict) -> Dict:
        """
        Analyzes Open Interest buildup to detect Support/Resistance.
        """
        strikes = chain_data.get("strikes", [])
        if not strikes:
            return {}
            
        highest_ce_oi = max(strikes, key=lambda x: x["CE"]["oi"])
        highest_pe_oi = max(strikes, key=lambda x: x["PE"]["oi"])
        
        # Determine Market Bias
        # If PE OI is building rapidly ATM/OTM, it indicates strong support
        ce_change_sum = sum(s["CE"]["oi_change"] for s in strikes)
        pe_change_sum = sum(s["PE"]["oi_change"] for s in strikes)
        
        buildup_bias = "NEUTRAL"
        if pe_change_sum > ce_change_sum * 1.5:
            buildup_bias = "BULLISH"
        elif ce_change_sum > pe_change_sum * 1.5:
            buildup_bias = "BEARISH"
            
        return {
            "major_resistance_strike": highest_ce_oi["strike"],
            "major_support_strike": highest_pe_oi["strike"],
            "ce_oi_change_total": ce_change_sum,
            "pe_oi_change_total": pe_change_sum,
            "buildup_bias": buildup_bias
        }
