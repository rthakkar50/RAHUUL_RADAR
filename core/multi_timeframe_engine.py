from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List

@dataclass
class TimeframeSignal:
    """
    Data container for a signal evaluated on a specific timeframe.
    """
    timeframe: str
    trend: str
    score: float
    confidence: float
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timeframe or not self.timeframe.strip():
            raise ValueError("Timeframe must not be empty.")
        if not (0 <= self.score <= 100):
            raise ValueError(f"Score must remain between 0 and 100. Got: {self.score}")
        if not (0 <= self.confidence <= 100):
            raise ValueError(f"Confidence must remain between 0 and 100. Got: {self.confidence}")
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeframe": self.timeframe,
            "trend": self.trend,
            "score": self.score,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeframeSignal':
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.now()
        
        return cls(
            timeframe=data.get("timeframe", ""),
            trend=data.get("trend", "UNKNOWN"),
            score=float(data.get("score", 0.0)),
            confidence=float(data.get("confidence", 0.0)),
            timestamp=ts
        )

    def __str__(self) -> str:
        return f"[{self.timeframe}] Trend: {self.trend} | Score: {self.score:.2f} | Confidence: {self.confidence:.2f}%"


class MultiTimeframeEngine:
    """
    Architecture for validating trading signals across multiple timeframes.
    This module never generates trading signals. Its only responsibility is 
    confirming whether different timeframes agree.
    """
    
    SUPPORTED_TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h"]
    
    def __init__(self) -> None:
        pass
        
    def collect_timeframes(self):
        """
        Collects signals from the supported timeframes.
        """
        pass
        
    def validate_alignment(self, signals: List[TimeframeSignal]) -> tuple:
        """
        Validates whether the collected timeframe signals align with each other.

        Args:
            signals: List of TimeframeSignal objects.

        Returns:
            Tuple[str, int, int]: (AlignmentStatus, confirmed_count, total_count)
        """
        total_count = len(signals)
        if total_count == 0:
            return "REJECTED", 0, 0

        bull_count = 0
        bear_count = 0
        neutral_count = 0

        for s in signals:
            trend_val = str(s.trend).upper()
            if trend_val in ("BULL", "BULLISH", "STRONG_BULL"):
                bull_count += 1
            elif trend_val in ("BEAR", "BEARISH", "STRONG_BEAR"):
                bear_count += 1
            else:
                neutral_count += 1

        # 1. Absolute Bullish Confirmation: all timeframes must be Bullish
        if bull_count == total_count:
            return "CONFIRMED", bull_count, total_count

        # 2. Dominant Agreement: at least 3 timeframes agree (excluding neutrals)
        agree_count = max(bull_count, bear_count)
        if agree_count >= 3:
            return "PARTIAL", agree_count, total_count

        # 3. Otherwise Rejected
        return "REJECTED", agree_count, total_count
        
    def calculate_alignment_score(self, signals: List[TimeframeSignal], alignment_status: str) -> float:
        """
        Calculates a score based on the degree of alignment across timeframes.

        Args:
            signals: List of TimeframeSignal objects.
            alignment_status: The calculated alignment status (CONFIRMED/PARTIAL/REJECTED).

        Returns:
            float: Alignment score between 0.0 and 100.0.
        """
        if not signals:
            return 0.0

        bull_count = sum(1 for s in signals if str(s.trend).upper() in ("BULL", "BULLISH"))
        bear_count = sum(1 for s in signals if str(s.trend).upper() in ("BEAR", "BEARISH"))
        
        aligned_count = max(bull_count, bear_count)

        if aligned_count >= 5:
            return 100.0
        elif aligned_count == 4:
            return 80.0
        elif aligned_count == 3:
            return 60.0
        elif aligned_count == 2:
            return 40.0
        elif aligned_count == 1:
            return 20.0
        
        return 0.0
        
    def build_alignment_report(self):
        """
        Builds the final report detailing multi-timeframe confirmation.
        """
        pass
