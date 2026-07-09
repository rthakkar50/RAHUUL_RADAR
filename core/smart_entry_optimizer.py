from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class EntryCandidate:
    """
    Data container for a potential trade entry evaluated by the optimizer.
    """
    symbol: str
    price: float
    signal_direction: str
    signal_strength: float
    timeframe: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "signal_direction": self.signal_direction,
            "signal_strength": self.signal_strength,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntryCandidate':
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.now()
        
        return cls(
            symbol=data.get("symbol", ""),
            price=float(data.get("price", 0.0)),
            signal_direction=data.get("signal_direction", "UNKNOWN"),
            signal_strength=float(data.get("signal_strength", 0.0)),
            timeframe=data.get("timeframe", ""),
            timestamp=ts
        )

    def __str__(self) -> str:
        return f"[{self.symbol}] {self.signal_direction} @ {self.price} | Strength: {self.signal_strength:.2f} | TF: {self.timeframe}"


@dataclass
class EntryEvaluation:
    """
    Data container holding the structured evaluation outcome for an entry point.
    """
    entry_quality: str
    entry_score: float
    risk_reward: float
    recommended_entry: float
    stop_loss: float
    target_1: float
    target_2: float
    confidence: float
    remarks: str

    def __post_init__(self):
        if not (0 <= self.entry_score <= 100):
            raise ValueError(f"Entry score must remain between 0 and 100. Got: {self.entry_score}")
        if not (0 <= self.confidence <= 100):
            raise ValueError(f"Confidence must remain between 0 and 100. Got: {self.confidence}")
        if self.risk_reward < 0:
            raise ValueError(f"Risk Reward must be >= 0. Got: {self.risk_reward}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_quality": self.entry_quality,
            "entry_score": self.entry_score,
            "risk_reward": self.risk_reward,
            "recommended_entry": self.recommended_entry,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "confidence": self.confidence,
            "remarks": self.remarks
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntryEvaluation':
        return cls(
            entry_quality=data.get("entry_quality", "UNKNOWN"),
            entry_score=float(data.get("entry_score", 0.0)),
            risk_reward=float(data.get("risk_reward", 0.0)),
            recommended_entry=float(data.get("recommended_entry", 0.0)),
            stop_loss=float(data.get("stop_loss", 0.0)),
            target_1=float(data.get("target_1", 0.0)),
            target_2=float(data.get("target_2", 0.0)),
            confidence=float(data.get("confidence", 0.0)),
            remarks=data.get("remarks", "")
        )

    def __str__(self) -> str:
        return (f"Quality: {self.entry_quality} | Score: {self.entry_score:.2f} | "
                f"RR: {self.risk_reward:.2f} | Entry: {self.recommended_entry} | "
                f"Stop: {self.stop_loss} | T1: {self.target_1} | T2: {self.target_2}")


class SmartEntryOptimizer:
    """
    Evaluates the quality of a specific entry point before a trade is executed.
    This engine never generates BUY or SELL signals; it only evaluates entry quality.
    """
    
    def __init__(self) -> None:
        pass
        
    def evaluate_entry(self):
        """
        Main orchestration method to evaluate whether NOW is the right entry point.
        """
        pass
        
    def calculate_entry_score(self, candidate: EntryCandidate, 
                              relative_strength: float = 50.0, 
                              trend_strength: float = 50.0, 
                              volume_confirmation: float = 50.0, 
                              mtf_alignment: float = 50.0) -> float:
        """
        Calculates a numeric score reflecting the absolute quality of the entry.
        Accepts all metric inputs as parameters directly to avoid calculating indicator values.
        Clamps the final returned score between 0.0 and 100.0.

        Args:
            candidate: EntryCandidate instance containing signal strength.
            relative_strength: Float rating for asset strength (0-100).
            trend_strength: Float rating for directional trend power (0-100).
            volume_confirmation: Float rating for volume validation (0-100).
            mtf_alignment: Float rating for alignment across timeframes (0-100).

        Returns:
            float: Entry quality score clamped between 0.0 and 100.0.
        """
        signal_strength = candidate.signal_strength if candidate else 0.0
        
        # Calculate a unified score based on parameters
        total = (signal_strength + relative_strength + trend_strength + volume_confirmation + mtf_alignment)
        score = total / 5.0
        
        # Clamp between 0.0 and 100.0
        clamped_score = max(0.0, min(100.0, score))
        
        return round(clamped_score, 2)
        
    def calculate_risk_reward(self):
        """
        Calculates the risk-to-reward ratio for the given entry structure.
        """
        pass
        
    def recommend_entry(self, candidate: EntryCandidate, entry_score: float) -> float:
        """
        Calculates the ideal entry price based on the signal constraints.
        Currently returns the candidate's proposed price directly as a placeholder.

        Args:
            candidate: EntryCandidate instance.
            entry_score: Numeric entry evaluation score.

        Returns:
            float: Recommended entry price.
        """
        return candidate.price if candidate else 0.0
        
    def recommend_stop_loss(self, candidate: EntryCandidate, entry_price: float, risk_reward: float, atr: float = 0.0, structure_details: dict = None) -> float:
        """
        Calculates the required defensive stop loss structure for the entry.
        Delegates to MASTER-25 (RiskRewardEngine).
        """
        if structure_details is None:
            structure_details = {}
            
        direction = candidate.signal_direction.upper() if candidate else "BUY"
        from core.risk_reward_engine import RiskRewardEngine
        srre = RiskRewardEngine()
        return srre.generate_stop_loss(entry_price, direction, atr, structure_details)
        
    def recommend_targets(self, candidate: EntryCandidate, entry_price: float, stop_loss: float, structure_details: dict = None) -> tuple:
        """
        Calculates layered take-profit targets (T1, T2, T3) for the optimal entry path.
        Delegates to MASTER-25 (RiskRewardEngine).
        """
        if structure_details is None:
            structure_details = {}
            
        direction = candidate.signal_direction.upper() if candidate else "BUY"
        from core.risk_reward_engine import RiskRewardEngine
        srre = RiskRewardEngine()
        return srre.generate_targets(entry_price, stop_loss, direction, structure_details)
