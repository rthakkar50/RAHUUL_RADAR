"""
Decision Engine module for RAHUUL_RADAR.
Aggregates technical scores and market state to generate final trading decisions.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from utils.logger import get_logger
from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult

logger = get_logger(__name__)


@dataclass
class MarketState:
    """
    Data structure representing the overall market conditions.
    Used to provide contextual bonuses or penalties to individual stock decisions.
    """
    trend: str
    strength: float
    volatility: float
    market_bias: str
    confidence: float


@dataclass
class DecisionResult:
    """
    Data structure representing the final actionable decision from the engine.
    """
    raw_score: float
    market_adjustment: float
    adjusted_score: float
    confidence: float
    decision: str
    reasons: List[str] = field(default_factory=list)
    
    @property
    def total_score(self) -> float:
        """Alias for backward compatibility with ScannerEngine."""
        return self.adjusted_score


class DecisionEngine:
    """
    Engine responsible for aggregating the outputs of all technical engines 
    and overall market state into a final, actionable trading decision.
    """
    
    def __init__(self) -> None:
        """Initializes the DecisionEngine."""
        logger.debug("DecisionEngine instantiated securely.")
        
    def calculate(
        self,
        trend_result: TrendResult,
        momentum_result: MomentumResult,
        structure_result: StructureResult,
        market_state: Optional[MarketState] = None,
        mode: str = "SWING",
        sector_result = None,
        oi_activity = None,
        adx_result = None,
        avwap_result = None,
        mtf_result = None
    ) -> DecisionResult:
        """
        Calculates the final trading decision by mathematically aggregating sub-engine results.
        """
        reasons: List[str] = []
        
        # 1. Base Scores Extraction
        trend_score = trend_result.score
        momentum_score = momentum_result.score
        structure_score = structure_result.score
        
        reasons.append(f"Trend Base Score: {trend_score}")
        reasons.append(f"Momentum Base Score: {momentum_score}")
        reasons.append(f"Structure Base Score: {structure_score}")
        
        # Calculate Raw Score
        raw_score = float(trend_score + momentum_score + structure_score)
        
        # 2. Calculate Confidence (Agreement between engines)
        # Convert engine scores into normalized -1 to +1 directional vectors
        t_dir = (trend_score / 30.0) * 2.0 - 1.0
        m_dir = (momentum_score / 25.0) * 2.0 - 1.0
        s_dir = (structure_score / 25.0) * 2.0 - 1.0
        
        # Absolute mean of directional vectors represents engine agreement (0 to 1)
        agreement = abs(t_dir + m_dir + s_dir) / 3.0
        confidence = min(100.0, max(0.0, agreement * 100.0))
        
        # 3. Market State Bonus Application
        market_bonus = 0.0
        
        if market_state:
            # Scale down the strength to avoid artificially boosting scores massively
            # Market adjustment should be a slight edge, not a complete override
            bonus = market_state.strength / 10.0
            if market_state.market_bias in ["BULLISH", "STRONG_BULL"]:
                market_bonus = bonus
                reasons.append(f"Bullish Market Context Bonus applied: +{market_bonus:.2f}")
            elif market_state.market_bias in ["BEARISH", "STRONG_BEAR"]:
                # Penalty for fighting a bearish market
                market_bonus = -bonus
                reasons.append(f"Bearish Market Context Penalty applied: {market_bonus:.2f}")
            else:
                reasons.append("Neutral Market Context: No bonus applied")
        else:
            reasons.append("No broader MarketState provided. Operating in isolation.")
            
        # 4. Final Aggregation
        adjusted_score = raw_score + market_bonus
        
        # Clamp strictly to Minimum = 0, Maximum = 100
        adjusted_score = max(0.0, min(100.0, adjusted_score))
        
        # 5. Decision Matrix Routing
        if mode == "OPTIONS":
            # For intraday options, we want aggressive accuracy.
            # Require minimum 70 adjusted score (out of ~80) to BUY.
            if adjusted_score >= 70.0:
                decision = "BUY"
                reasons.append(f"Score ({adjusted_score:.2f}) >= 70 threshold (OPTIONS mode) -> [BUY]")
            elif adjusted_score <= 20.0:
                decision = "SELL"
                reasons.append(f"Score ({adjusted_score:.2f}) <= 20 threshold (OPTIONS mode) -> [SELL]")
            else:
                decision = "WATCH"
                reasons.append(f"Score ({adjusted_score:.2f}) between 20-70 (OPTIONS mode) -> [WATCH]")
        else:
            if adjusted_score >= 50.0:
                decision = "BUY"
                reasons.append(f"Score ({adjusted_score:.2f}) >= 50 threshold -> [BUY]")
            elif adjusted_score >= 40.0:
                decision = "WATCH"
                reasons.append(f"Score ({adjusted_score:.2f}) in 40-49 threshold -> [WATCH]")
            else:
                decision = "SELL"
                reasons.append(f"Score ({adjusted_score:.2f}) below 40 threshold -> [SELL]")
            
        # Console Output exactly as required
        print("\n=== DECISION ENGINE CONSOLE OUTPUT ===")
        print(f"Trend Score:       {trend_score}")
        print(f"Momentum Score:    {momentum_score}")
        print(f"Structure Score:   {structure_score}")
        print(f"Raw Score:         {raw_score}")
        print(f"Market Adjustment: {market_bonus:.2f}")
        print(f"Adjusted Score:    {adjusted_score:.2f}")
        print(f"Decision:          {decision}")
        print(f"Confidence:        {confidence:.2f}")
        print("======================================\n")
            
        logger.debug(f"Decision Calculation Complete | Adjusted Score: {adjusted_score:.2f} | Decision: {decision}")
        
        # Combine all upstream reasons for a complete audit trail
        upstream_reasons = trend_result.reasons + momentum_result.reasons + structure_result.reasons
        all_reasons = upstream_reasons + ["--- Decision Math ---"] + reasons
        
        return DecisionResult(
            raw_score=round(raw_score, 2),
            market_adjustment=round(market_bonus, 2),
            adjusted_score=round(adjusted_score, 2),
            confidence=round(confidence, 2),
            decision=decision,
            reasons=all_reasons
        )
