"""
Volume calculation engine for RAHUUL_RADAR.
Analyzes relative volume (RVOL), price-volume agreement, and On-Balance Volume (OBV) trend.
"""
from dataclasses import dataclass, field
from typing import List
import pandas as pd
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class VolumeResult:
    """
    Data structure representing the outcome of the VolumeEngine calculation.
    """
    score: float
    reasons: List[str] = field(default_factory=list)


class VolumeEngine:
    """
    Engine responsible for evaluating volume confirmation.
    Computes RVOL, Price-Volume divergence, and OBV direction.
    """
    
    def __init__(self) -> None:
        """Initializes the VolumeEngine."""
        logger.debug("VolumeEngine instantiated.")

    def evaluate(self, df: pd.DataFrame, direction: str) -> VolumeResult:
        """
        Evaluates the volume profile and computes a score from 0 to 100.
        """
        score = 0.0
        reasons = []

        if df is None or len(df) < 20:
            logger.warning("Not enough data for VolumeEngine. Defaulting to 0.")
            return VolumeResult(score=0.0, reasons=["Insufficient data for volume analysis."])
        
        try:
            # 1. Relative Volume (RVOL) [Max 50 points]
            current_vol = float(df['Volume'].iloc[-1])
            avg_vol_20 = float(df['Volume'].rolling(window=20).mean().iloc[-1])
            rvol = current_vol / avg_vol_20 if avg_vol_20 > 0 else 0.0
            
            if rvol >= 2.0:
                score += 50.0
                reasons.append(f"Exceptional Volume Surge (RVOL={rvol:.2f})")
            elif rvol >= 1.5:
                score += 35.0
                reasons.append(f"Strong Relative Volume (RVOL={rvol:.2f})")
            elif rvol >= 1.0:
                score += 20.0
                reasons.append(f"Average Volume (RVOL={rvol:.2f})")
            else:
                score += 0.0
                reasons.append(f"Low Volume (RVOL={rvol:.2f})")

            # 2. Price-Volume Agreement [Max 30 points]
            current_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            
            if direction == "BUY" and current_close > prev_close:
                score += 30.0
                reasons.append("Price-Volume Agreement: Bullish Close")
            elif direction == "SELL" and current_close < prev_close:
                score += 30.0
                reasons.append("Price-Volume Agreement: Bearish Close")
            else:
                reasons.append("Price-Volume Divergence detected")

            # 3. OBV Trend (5-period slope) [Max 20 points]
            # Calculate standard OBV
            obv = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
            
            # 5-period slope logic
            if len(obv) >= 5:
                recent_obv = obv.iloc[-5:]
                # Simple linear regression slope on the last 5 points
                x = np.arange(5)
                y = recent_obv.values
                slope = np.polyfit(x, y, 1)[0]
                
                if direction == "BUY" and slope > 0:
                    score += 20.0
                    reasons.append("OBV Trend supports BUY direction")
                elif direction == "SELL" and slope < 0:
                    score += 20.0
                    reasons.append("OBV Trend supports SELL direction")
                else:
                    reasons.append("OBV Trend contradicts trade direction")
            
            # Clamp final score
            score = max(0.0, min(100.0, score))
            
            return VolumeResult(score=score, reasons=reasons)
            
        except Exception as e:
            logger.exception(f"VolumeEngine evaluation failed: {e}")
            return VolumeResult(score=0.0, reasons=[f"Volume calculation error: {e}"])
