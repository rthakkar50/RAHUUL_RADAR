"""
MASTER-25: Smart Risk Reward Engine (SRRE)
Validates whether a trade offers a professional risk/reward profile.
Capital protection engine that rejects trades with poor R/R.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RiskRewardResult:
    entry: float = 0.0
    stop_loss: float = 0.0
    target_1: float = 0.0
    target_2: float = 0.0
    risk: float = 0.0
    reward: float = 0.0
    rr_ratio: float = 0.0
    risk_score: int = 0
    recommendation: str = "WAIT"
    reasons: List[str] = field(default_factory=list)


class RiskRewardEngine:
    def __init__(self):
        logger.debug("Smart Risk Reward Engine (SRRE) instantiated securely.")

    def evaluate(
        self,
        entry_price: float,
        stop_loss: float,
        target_1: float,
        target_2: float = 0.0,
        atr: float = 0.0,
        trade_direction: str = "BUY"
    ) -> RiskRewardResult:
        
        reasons = []
        score = 0
        recommendation = "WAIT"
        
        # 1. Base Validations
        if entry_price <= 0 or stop_loss <= 0 or target_1 <= 0:
            reasons.append("Invalid Entry, SL, or Target values.")
            return RiskRewardResult(recommendation="REJECT", reasons=reasons)
            
        if trade_direction.upper() == "BUY":
            if stop_loss >= entry_price:
                reasons.append("BUY Trade: Stop Loss must be below Entry Price.")
                return RiskRewardResult(recommendation="REJECT", reasons=reasons)
            if target_1 <= entry_price:
                reasons.append("BUY Trade: Target must be above Entry Price.")
                return RiskRewardResult(recommendation="REJECT", reasons=reasons)
        elif trade_direction.upper() == "SELL":
            if stop_loss <= entry_price:
                reasons.append("SELL Trade: Stop Loss must be above Entry Price.")
                return RiskRewardResult(recommendation="REJECT", reasons=reasons)
            if target_1 >= entry_price:
                reasons.append("SELL Trade: Target must be below Entry Price.")
                return RiskRewardResult(recommendation="REJECT", reasons=reasons)
                
        # 2. Risk / Reward Calculation
        risk = abs(entry_price - stop_loss)
        reward = abs(target_1 - entry_price)
        
        if risk == 0:
            risk = 1e-5
            
        rr_ratio = reward / risk
        reasons.append(f"Risk: {risk:.2f}, Reward: {reward:.2f} -> R/R Ratio: 1:{rr_ratio:.2f}")
        
        # 3. RR Scoring Logic
        if rr_ratio < 1.5:
            score = 0
            recommendation = "REJECT"
            reasons.append("SRRE Rejection: R/R < 1:1.5. Poor risk profile.")
        elif rr_ratio < 2.0:
            score = 55
            recommendation = "ACCEPT"
            reasons.append("Minimum Acceptable R/R (1:1.5 to 1:2.0).")
        elif rr_ratio < 2.5:
            score = 80
            recommendation = "ACCEPT"
            reasons.append("Strong R/R (1:2.0 to 1:2.5).")
        elif rr_ratio <= 4.0:
            score = 95
            recommendation = "ACCEPT"
            reasons.append("Excellent R/R (1:2.5 to 1:4.0).")
        else:
            score = 85
            recommendation = "ACCEPT"
            reasons.append("R/R > 1:4.0. Review for realism (Check if SL is too tight).")
            
        # 4. ATR Validation
        if atr > 0:
            sl_distance = risk
            if sl_distance < atr * 0.5:
                score -= 20
                reasons.append(f"Warning: SL distance ({sl_distance:.2f}) is < 0.5x ATR ({atr:.2f}). Highly vulnerable to volatility noise.")
            elif sl_distance > atr * 3.0:
                score -= 10
                reasons.append(f"Warning: SL distance ({sl_distance:.2f}) is > 3.0x ATR ({atr:.2f}). Inefficient capital allocation.")
            else:
                reasons.append(f"SL safely placed beyond ATR noise (Distance: {sl_distance:.2f}, ATR: {atr:.2f}).")
                
        score = max(0, min(100, score))
        
        return RiskRewardResult(
            entry=entry_price,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            risk=risk,
            reward=reward,
            rr_ratio=rr_ratio,
            risk_score=score,
            recommendation=recommendation,
            reasons=reasons
        )

    def generate_stop_loss(self, entry_price: float, direction: str, atr: float, structure_details: dict) -> float:
        """
        MASTER-25 Dynamic Stop Loss Generation.
        Combines Market Structure (Primary) and ATR Buffer (Secondary).
        """
        direction = direction.upper()
        swing_high = float(structure_details.get("swing_high", 0.0))
        swing_low = float(structure_details.get("swing_low", 0.0))
        
        # Fallback if structure is missing
        if swing_high == 0.0:
            swing_high = entry_price * 1.02
        if swing_low == 0.0:
            swing_low = entry_price * 0.98
            
        atr_buffer = atr * 1.5 if atr > 0 else entry_price * 0.02
        
        if direction in ("BUY", "BULL", "BULLISH"):
            structural_stop = swing_low
            atr_stop = entry_price - atr_buffer
            # Use the safer (lower) stop to survive volatility
            return round(min(structural_stop, atr_stop), 2)
        else:
            structural_stop = swing_high
            atr_stop = entry_price + atr_buffer
            # Use the safer (higher) stop to survive volatility
            return round(max(structural_stop, atr_stop), 2)

    def generate_targets(self, entry_price: float, stop_loss: float, direction: str, structure_details: dict) -> tuple:
        """
        MASTER-25 Dynamic Targets Generation.
        Ensures a professional minimum Risk/Reward profile.
        """
        direction = direction.upper()
        risk = abs(entry_price - stop_loss)
        if risk == 0:
            risk = entry_price * 0.02
            
        swing_high = float(structure_details.get("swing_high", 0.0))
        swing_low = float(structure_details.get("swing_low", 0.0))

        if direction in ("BUY", "BULL", "BULLISH"):
            # Target 1: Minimum 1:2 RR
            t1 = entry_price + (risk * 2.0)
            
            # Target 2: 1:3 RR or Nearest Resistance if it offers better RR
            structural_t2 = swing_high if swing_high > t1 else 0.0
            rr_t2 = entry_price + (risk * 3.0)
            t2 = max(structural_t2, rr_t2)
            
            t3 = entry_price + (risk * 4.0)
        else:
            # Target 1: Minimum 1:2 RR
            t1 = entry_price - (risk * 2.0)
            
            # Target 2: 1:3 RR or Nearest Support if it offers better RR
            structural_t2 = swing_low if (swing_low < t1 and swing_low > 0) else 0.0
            rr_t2 = entry_price - (risk * 3.0)
            t2 = min(structural_t2, rr_t2) if structural_t2 > 0 else rr_t2
            
            t3 = entry_price - (risk * 4.0)
            
        return round(t1, 2), round(t2, 2), round(t3, 2)

    def generate_trade_plan(self, entry_price: float, direction: str, atr: float, structure_details: dict) -> RiskRewardResult:
        """
        Orchestrates full trade management generation and returns evaluated result.
        """
        sl = self.generate_stop_loss(entry_price, direction, atr, structure_details)
        t1, t2, t3 = self.generate_targets(entry_price, sl, direction, structure_details)
        
        return self.evaluate(
            entry_price=entry_price,
            stop_loss=sl,
            target_1=t1,
            target_2=t2,
            atr=atr,
            trade_direction=direction
        )
