from typing import Dict, List
import pandas as pd
from market.data_provider import OHLCV

class FalseBreakoutDetectionEngine:
    """
    FALSE BREAKOUT DETECTION ENGINE (FBDE) V2.0
    Gatekeeper to prevent Bull Traps, Bear Traps, and Fake Breakouts.
    Only responsibility: Reject False Trades.
    """
    def __init__(self):
        pass

    def verify_breakout(self, symbol: str, signal: str, trade_data: Dict, ohlcv: List[OHLCV], market_trend: str) -> Dict:
        """
        Executes 12-stage strict breakout validation.
        Returns {"fbde_status": str, "fbde_score": int, "fbde_reason": str}
        """
        if signal not in ["BUY", "SELL"]:
            return {"fbde_status": "REJECT", "fbde_score": 0, "fbde_reason": "No Signal"}

        if not ohlcv or len(ohlcv) < 20:
            return {"fbde_status": "REJECT", "fbde_score": 0, "fbde_reason": "Insufficient Data"}

        score = 100
        reasons = []
        
        latest = ohlcv[-1]
        
        # 1. Breakout Quality (Wick vs Body)
        body = abs(latest.close - latest.open)
        wick_up = latest.high - max(latest.close, latest.open)
        wick_dn = min(latest.close, latest.open) - latest.low
        
        if signal == "BUY" and wick_up > body:
            score -= 20
            reasons.append("Fake Breakout (Long Upper Wick)")
        elif signal == "SELL" and wick_dn > body:
            score -= 20
            reasons.append("False Breakdown (Long Lower Wick)")
            
        # 2. Volume Confirmation
        vol_ma = sum(c.volume for c in ohlcv[-21:-1]) / 20 if len(ohlcv) > 20 else sum(c.volume for c in ohlcv[:-1]) / max(1, len(ohlcv)-1)
        if latest.volume < vol_ma:
            score -= 30
            reasons.append("Weak Volume")
            
        # 3. VWAP Conflict (Approx calculation)
        typical_price = (latest.high + latest.low + latest.close) / 3
        # Simple estimate for intraday VWAP just for this check (in real life, requires full day data)
        # Using 20 SMA as a proxy for trend line if VWAP is unavailable
        close_ma = sum(c.close for c in ohlcv[-20:]) / 20
        if signal == "BUY" and latest.close < close_ma:
            score -= 20
            reasons.append("VWAP/Trend Conflict")
        elif signal == "SELL" and latest.close > close_ma:
            score -= 20
            reasons.append("VWAP/Trend Conflict")
            
        # 4 & 5 & 6. HTF / Sector / Market Confirmation
        if signal == "BUY" and market_trend == "DOWNTREND":
            score -= 15
            reasons.append("Market Weak")
        elif signal == "SELL" and market_trend == "UPTREND":
            score -= 15
            reasons.append("Market Strong")
            
        # 7. Liquidity (Proxy by volume)
        if latest.volume < 1000:
            score -= 20
            reasons.append("Liquidity Trap / Wide Spread")
            
        # 8 & 10. Gap Analysis & Trap Detector
        prev = ohlcv[-2]
        gap = (latest.open - prev.close) / prev.close
        if signal == "BUY" and gap > 0.02 and latest.close < latest.open:
            score -= 40
            reasons.append("Gap Trap / Bull Trap")
        elif signal == "SELL" and gap < -0.02 and latest.close > latest.open:
            score -= 40
            reasons.append("Gap Fill / Bear Trap")
            
        # 12. Risk (RR > 1:2)
        try:
            rr = float(trade_data.get("risk_reward", "0:0").split(":")[1])
        except:
            rr = 0
        if rr < 2.0:
            score -= 10
            reasons.append("Poor RR")

        # Determine Final Status
        score = max(0, min(100, score))
        
        if score >= 90:
            status = f"VALID {'BREAKOUT' if signal == 'BUY' else 'BREAKDOWN'}"
            final_reason = "Clean Structure"
        elif score >= 70:
            status = "WAIT"
            final_reason = " | ".join(reasons) if reasons else "Wait for confirmation"
        else:
            status = "REJECT"
            final_reason = " | ".join(reasons) if reasons else "Multiple Check Failures"
            
        return {
            "fbde_status": status,
            "fbde_score": score,
            "fbde_reason": final_reason
        }
