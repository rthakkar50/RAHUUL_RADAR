from typing import Dict, List

class PCRAnalyzer:
    @staticmethod
    def analyze(chain_data: Dict) -> Dict:
        """
        Calculates Put-Call Ratio and interprets sentiment.
        """
        total_ce_oi = 0
        total_pe_oi = 0
        total_ce_vol = 0
        total_pe_vol = 0
        
        for strike in chain_data.get("strikes", []):
            total_ce_oi += strike["CE"]["oi"]
            total_pe_oi += strike["PE"]["oi"]
            total_ce_vol += strike["CE"]["volume"]
            total_pe_vol += strike["PE"]["volume"]
            
        pcr_oi = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 1.0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 1.0
        
        sentiment = "NEUTRAL"
        if pcr_oi > 1.2:
            sentiment = "BULLISH"
        elif pcr_oi > 1.5:
            sentiment = "STRONG BULLISH"
        elif pcr_oi < 0.8:
            sentiment = "BEARISH"
        elif pcr_oi < 0.6:
            sentiment = "STRONG BEARISH"
            
        return {
            "pcr_oi": round(pcr_oi, 2),
            "pcr_vol": round(pcr_vol, 2),
            "sentiment": sentiment
        }
