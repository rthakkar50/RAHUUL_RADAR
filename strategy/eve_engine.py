import logging
from typing import Dict, List
from market.data_provider import OHLCV

eve_logger = logging.getLogger("EVE")
eve_logger.setLevel(logging.INFO)

class EntryValidationEngine:
    """
    ENTRY VALIDATION ENGINE (EVE) V2.0
    Only responsibility: "Should the trader enter NOW?"
    Does NOT generate BUY/SELL signals. Validates entry quality.
    """
    def __init__(self):
        pass

    def validate_entry(self, symbol: str, signal: str, trade_data: Dict, ohlcv: List[OHLCV]) -> Dict:
        """
        Takes a qualified trade signal and validates if it should be entered NOW.
        Returns the updated trade_data with EVE fields.
        """
        if signal not in ["BUY", "SELL"]:
            return self._attach_eve_result(trade_data, "AVOID", 0, "F", "No valid signal.")

        score = 60 # Base score
        reason = []
        
        latest_vol = ohlcv[-1].volume if ohlcv else 0
        prev_vol = ohlcv[-2].volume if len(ohlcv) > 1 else 0
        
        # 1. Breakout Quality / Fake Breakout Probability
        breakout_type = trade_data.get("breakout_type", "None")
        if "Fake" in breakout_type or breakout_type == "None":
            score -= 20
            reason.append("Breakout not confirmed.")
        else:
            score += 10
            
        # 2. Volume Confirmation
        vol_status = trade_data.get("volume_status", "")
        if "Inst. Buying" in vol_status or "Inst. Selling" in vol_status:
            score += 10
        elif "Volume Spike" in vol_status:
            score += 5
        else:
            score -= 10
            reason.append("Volume confirmation pending.")
            
        # 3. HTF Alignment
        if trade_data.get("trend") != "NEUTRAL":
            score += 10
        else:
            score -= 10
            reason.append("HTF Alignment missing.")
            
        # 4. Confidence
        try:
            conf_str = str(trade_data.get("confidence", "0")).replace("%", "")
            conf = int(conf_str)
        except:
            conf = 0
            
        if conf >= 90:
            score += 10
        elif conf < 85:
            score -= 20
            reason.append("Low Confidence.")
            
        # 5. Spread / Liquidity check (proxy via absolute volume size)
        if latest_vol < 1000:
            score -= 20
            reason.append("Low Liquidity / High Spread.")
            
        # 6. Risk Reward
        rr_str = trade_data.get("risk_reward", "0:0")
        try:
            rr = float(rr_str.split(":")[1])
        except:
            rr = 0
        if rr >= 3.0:
            score += 5
        elif rr < 2.0:
            score -= 15
            reason.append("Poor Risk Reward.")
            
        # Bound Score
        score = max(0, min(100, score))
        
        # Determine State
        if score >= 90:
            decision = "ENTER NOW"
            grade = "A+" if score >= 95 else "A"
            final_reason = "Perfect Entry Setup" if not reason else " | ".join(reason)
        elif score >= 70:
            decision = "WAIT"
            grade = "B"
            final_reason = " | ".join(reason) if reason else "Waiting for optimal condition."
        else:
            decision = "AVOID"
            grade = "C" if score >= 50 else "F"
            final_reason = " | ".join(reason) if reason else "Setup degraded."
            
        return self._attach_eve_result(trade_data, decision, score, grade, final_reason)

    def _attach_eve_result(self, trade_data: Dict, decision: str, score: int, grade: str, reason: str) -> Dict:
        td = trade_data.copy()
        td["eve_decision"] = decision
        td["eve_score"] = score
        td["eve_grade"] = grade
        td["eve_reason"] = reason
        return td
