"""
Composite Decision Layer for RAHUUL_RADAR.
Implements the Institutional Quality Modifier logic (Sprint 87B) without altering core mathematical scoring.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from core.models.domain_models import CompositeRelativeStrength
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class CompositeEvaluation:
    """
    Data structure representing the output of the Composite Layer.
    """
    is_valid: bool = True
    signal_modifier: str = "NEUTRAL" # "UPGRADE", "DOWNGRADE", "NEUTRAL"
    reasons: List[str] = field(default_factory=list)
    quality_category: str = "Standard"

class CompositeLayer:
    """
    Evaluates a stock's institutional quality based on the Composite Relative Strength
    framework to validate or modify the core DecisionEngine signals.
    """
    
    def __init__(self):
        logger.debug("CompositeLayer initialized securely.")
        
    def evaluate(self, composite_rs: Optional[CompositeRelativeStrength], base_decision: str) -> CompositeEvaluation:
        """
        Evaluate the composite signals and determine if the base decision should be modified.
        Currently operates in PASS-THROUGH mode (no actual signal modification), returning reasons only.
        """
        evaluation = CompositeEvaluation()
        
        if not composite_rs:
            evaluation.reasons.append("Composite Signals: Missing or None (No institutional overlay applied)")
            return evaluation
            
        market_alpha = composite_rs.market_alpha
        sector_alpha = composite_rs.sector_alpha
        momentum = composite_rs.relative_momentum
        persistence = composite_rs.trend_persistence
        
        reasons = []
        
        # 1. Market Alpha (Primary Key)
        alpha_state = "Neutral"
        if market_alpha >= 60.0:
            alpha_state = "Strong"
            reasons.append(f"Market Alpha: Strong ({market_alpha:.2f})")
        elif market_alpha <= 40.0:
            alpha_state = "Weak"
            reasons.append(f"Market Alpha: Weak ({market_alpha:.2f})")
        else:
            reasons.append(f"Market Alpha: Neutral ({market_alpha:.2f})")
            
        # 2. Sector Alpha (Contextual Key)
        if alpha_state == "Strong":
            reasons.append("Sector Alpha: Redundant (Market Alpha dominates)")
        else:
            if sector_alpha > 0:
                reasons.append(f"Sector Alpha: Positive ({sector_alpha:.2f})")
            else:
                reasons.append(f"Sector Alpha: Negative ({sector_alpha:.2f})")
                
        # 3. Momentum Interpretation (Pullback paradigm)
        if momentum <= 30.0:
            if alpha_state == "Strong":
                reasons.append(f"Momentum: Deep Pullback ({momentum:.2f}) -> Optimal Entry")
                evaluation.quality_category = "High-Quality Pullback"
            else:
                reasons.append(f"Momentum: Low ({momentum:.2f}) -> Structurally Weak")
                evaluation.quality_category = "Structurally Broken"
        elif momentum >= 70.0:
            if alpha_state == "Strong":
                reasons.append(f"Momentum: Extended Breakout ({momentum:.2f}) -> Chasing Risk")
                evaluation.quality_category = "Extended Breakout"
            else:
                reasons.append(f"Momentum: High ({momentum:.2f}) -> Counter-trend Bounce")
                evaluation.quality_category = "Counter-trend Bounce"
        else:
            reasons.append(f"Momentum: Neutral ({momentum:.2f})")
            evaluation.quality_category = "Standard"
            
        # 4. Persistence
        if persistence >= 55.0:
            reasons.append(f"Persistence: High Stability ({persistence:.2f})")
        elif persistence <= 45.0:
            reasons.append(f"Persistence: Low Stability ({persistence:.2f})")
        else:
            reasons.append(f"Persistence: Moderate ({persistence:.2f})")
            
        evaluation.reasons = reasons
        
        # Note: In Phase 1 / Phase 2, signal_modifier remains NEUTRAL.
        # We explicitly do NOT alter the final decision yet, just provide explainability.
        
        return evaluation
