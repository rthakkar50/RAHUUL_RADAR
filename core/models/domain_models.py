"""
Core domain models for RAHUUL_RADAR.
Contains the primary data structures that flow through the scanner pipeline.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from ranking.scoring_rules import SignalStrength

@dataclass
class CompositeRelativeStrength:
    """
    Encapsulates all relative strength dimensions into a unified framework.
    """
    market_alpha: float = 0.0
    sector_alpha: float = 0.0
    sector_benchmark: str = "NIFTY50"
    relative_momentum: float = 50.0
    trend_persistence: float = 50.0
    
@dataclass
class ScanResult:
    """
    Data structure representing the final output of a complete market scan for a single stock.
    Aggregates metadata, technical scores, and the generated trading signal.
    """
    symbol: str
    company_name: str
    sector: str
    
    trend_direction: str
    trend_score: float
    momentum_score: float
    structure_score: float
    volume_score: float
    volatility_score: float
    relative_strength_score: float
    risk_score: float
    mtf_score: float  # Multi-timeframe confirmation score
    total_score: float
    
    price: float
    volume: float
    
    signal: SignalStrength
    timestamp: datetime
    composite_relative_strength: Optional[CompositeRelativeStrength] = None
    composite_evaluation: Optional[Any] = None
    relative_momentum: float = 50.0
    trend_persistence: float = 50.0
    breakdown_detail: dict = None
    quality_grade: str = "N/A"
    status: str = "RANKED"
    adx_value: float = 0.0
    avwap_status: str = "Neutral"
    mtf_data: Any = None
    legacy_decision: Optional[str] = None

    def is_strong_buy(self) -> bool:
        """
        Checks if the scan resulted in a STRONG_BUY signal.
        
        Returns:
            bool: True if STRONG_BUY, else False.
        """
        return self.signal == SignalStrength.STRONG_BUY

    def is_buy(self) -> bool:
        """
        Checks if the scan resulted in a BUY signal.
        Note: This strictly checks for BUY, use is_strong_buy() for the highest tier.
        
        Returns:
            bool: True if BUY, else False.
        """
        return self.signal == SignalStrength.BUY

    def is_watch(self) -> bool:
        """
        Checks if the scan resulted in a WATCH signal.
        
        Returns:
            bool: True if WATCH, else False.
        """
        return self.signal == SignalStrength.WATCH

    def is_sell(self) -> bool:
        """
        Checks if the scan resulted in a WEAK or AVOID signal (interpreted as Sell/Short conditions).
        
        Returns:
            bool: True if the signal indicates weakness/avoidance, else False.
        """
        return self.signal in (SignalStrength.WEAK, SignalStrength.AVOID)
