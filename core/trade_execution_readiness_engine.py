"""
MASTER-29: Trade Execution Readiness Engine (TERE)
Determines whether an approved trade is ready for execution right now.
Separates "Signal Quality" from "Execution Timing".
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class ExecutionInput:
    elite_score: float = 50.0
    confidence: float = 50.0
    structure_score: float = 50.0
    adx_value: float = 0.0
    volume_score: float = 50.0
    risk_reward_score: float = 50.0
    market_regime: str = "Neutral"
    breakout_status: str = "Confirmed"
    
@dataclass
class ExecutionResult:
    status: str
    score: float
    reason: str
    
class TradeExecutionReadinessEngine:
    def __init__(self):
        pass

    def evaluate_readiness(self, inputs: ExecutionInput) -> ExecutionResult:
        score = 100.0
        status = "ENTER NOW"
        reason = "Perfect alignment. Ready for immediate execution."
        
        # 1. Hard Rejections (Capital Protection & Structure)
        if inputs.risk_reward_score < 50:
            return ExecutionResult("REJECT", 0.0, "Poor Risk/Reward. Capital Protection active.")
        if inputs.structure_score < 40:
            return ExecutionResult("REJECT", 0.0, "Market Structure broken.")
        if "BEAR" in inputs.market_regime.upper() and inputs.elite_score < 90:
            return ExecutionResult("REJECT", 0.0, "Fighting Bear Market Regime without extreme setup quality.")
            
        # 2. Not Ready (Weak underlying health)
        if inputs.volume_score < 40:
            return ExecutionResult("NOT READY", 50.0, "Volume confirmation is severely lacking.")
        if inputs.elite_score < 80:
            return ExecutionResult("NOT READY", 60.0, "Elite score too low for immediate execution.")
            
        # 3. Retest First (Price is extended)
        if "Extended" in inputs.breakout_status or "Overbought" in inputs.breakout_status:
            return ExecutionResult("RETEST FIRST", 85.0, "Breakout already occurred. Price is extended. Wait for pullback.")
            
        # 4. Wait (Pending confirmations)
        wait_reasons = []
        if inputs.confidence < 80:
            wait_reasons.append("Confidence below 80%.")
            score -= 10
        if inputs.adx_value > 0 and inputs.adx_value < 20:
            wait_reasons.append("ADX below 20 (Weak Trend).")
            score -= 10
        if inputs.volume_score < 60:
            wait_reasons.append("Waiting for volume expansion.")
            score -= 5
        if "Pending" in inputs.breakout_status or "Approaching" in inputs.breakout_status:
            wait_reasons.append("Waiting for breakout candle to close.")
            score -= 10
            
        if wait_reasons:
            status = "WAIT"
            reason = " ".join(wait_reasons)
            score = max(70.0, score)
            return ExecutionResult(status, score, reason)
            
        # 5. Ready / Enter Now
        if score >= 95:
            status = "ENTER NOW"
            reason = "Flawless execution timing. Breakout and volume confirmed."
        else:
            status = "READY"
            reason = "Trade is ready to trigger."
            
        return ExecutionResult(status, score, reason)
