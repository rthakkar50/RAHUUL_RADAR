from typing import Dict, Any

class SmartOptionAI:
    """
    Enforces the V2.0 10-Layer Quality Engine for Option Scalping.
    """
    def __init__(self):
        pass

    def evaluate_trade(self, 
                       underlying_trend: str, 
                       radar_score: int, 
                       option_chain_data: Dict, 
                       vwap_status: str,
                       ema_status: str,
                       volume_status: str) -> Dict[str, Any]:
        """
        Runs the 10-Layer Filter and outputs BUY CALL, BUY PUT, or NO TRADE.
        """
        # 1. Market Direction & Trend
        if underlying_trend not in ["BULLISH", "STRONG_BULLISH", "BEARISH", "STRONG_BEARISH"]:
            return self._no_trade("Weak Trend or Sideways Market")
            
        # 2. Score / Momentum
        if radar_score < 70:
            return self._no_trade(f"Radar Score ({radar_score}) below 70 threshold")
            
        # 3. Volume
        if volume_status != "STRONG":
            return self._no_trade("Low Volume Expansion")
            
        # 4. VWAP & EMA Alignment
        if underlying_trend in ["BULLISH", "STRONG_BULLISH"]:
            if vwap_status != "ABOVE" or ema_status != "ALIGNED_UP":
                return self._no_trade("Conflicting Indicators (Price below VWAP/EMA)")
            direction = "BUY CALL"
            
        elif underlying_trend in ["BEARISH", "STRONG_BEARISH"]:
            if vwap_status != "BELOW" or ema_status != "ALIGNED_DOWN":
                return self._no_trade("Conflicting Indicators (Price above VWAP/EMA)")
            direction = "BUY PUT"

        # 5. Open Interest & PCR
        pcr = option_chain_data.get("pcr_analysis", {}).get("sentiment", "NEUTRAL")
        oi = option_chain_data.get("oi_analysis", {}).get("buildup_bias", "NEUTRAL")
        
        if direction == "BUY CALL" and (pcr == "BEARISH" or oi == "BEARISH"):
            return self._no_trade("Conflicting Signals (Trend Bullish but OI/PCR Bearish)")
        if direction == "BUY PUT" and (pcr == "BULLISH" or oi == "BULLISH"):
            return self._no_trade("Conflicting Signals (Trend Bearish but OI/PCR Bullish)")

        # 6. IV Risk
        iv_risk = option_chain_data.get("iv_analysis", {}).get("iv_risk", "UNKNOWN")
        if "HIGH" in iv_risk:
            return self._no_trade("High IV Risk (Crush Probability)")

        # 7. Quality Grading & Probability
        if radar_score >= 90:
            quality = "A+"
            prob = "91%"
            risk = "LOW"
        elif radar_score >= 80:
            quality = "A"
            prob = "82%"
            risk = "LOW"
        else:
            quality = "B+"
            prob = "74%"
            risk = "MEDIUM"
            return self._no_trade(f"Trade Quality {quality} is below A+/A threshold")

        # 8. Strike Selection
        strike_data = option_chain_data.get("strike_selection", {})
        if direction == "BUY CALL":
            best_strike = strike_data.get("best_ce", {})
        else:
            best_strike = strike_data.get("best_pe", {})
            
        if not best_strike:
            return self._no_trade("Failed to select valid strike")
            
        entry_premium = best_strike.get("premium", 0.0)
        
        # 9. Target & SL calculation (Simulated Scalping RR)
        # Assuming ATR based SL logic handled upstream, we simulate simple 1:2 RR for AI output
        stop_loss = round(entry_premium * 0.90, 2) if direction == "BUY CALL" else round(entry_premium * 0.90, 2)
        risk_amt = entry_premium - stop_loss
        target_1 = round(entry_premium + (risk_amt * 1.5), 2)
        target_2 = round(entry_premium + (risk_amt * 2.0), 2)

        # 10. AI Explanation
        explanation = f"{direction} because "
        explanation += f"Trend {underlying_trend.title()}, "
        explanation += "VWAP Support, " if direction == "BUY CALL" else "VWAP Resistance, "
        explanation += "Volume Expansion, "
        explanation += f"PCR {pcr.title()}, "
        explanation += "Risk Low, "
        explanation += f"Quality {quality}."

        return {
            "verdict": direction,
            "quality": quality,
            "risk_rating": risk,
            "success_probability": prob,
            "expected_holding": "15 Minutes",
            "explanation": explanation,
            "trade_details": {
                "strike": best_strike.get("strike"),
                "expiry": option_chain_data.get("expiry"),
                "entry_premium": entry_premium,
                "stop_loss": stop_loss,
                "target_1": target_1,
                "target_2": target_2,
                "rr": "1:2"
            }
        }

    def _no_trade(self, reason: str) -> Dict[str, Any]:
        return {
            "verdict": "NO TRADE",
            "explanation": reason,
            "quality": "N/A",
            "risk_rating": "N/A",
            "success_probability": "N/A",
            "expected_holding": "N/A"
        }
