"""
MASTER-24: Market Structure Engine (MSE)
Analyzes pure price action context, structural validity, BOS, CHoCH, and Zones.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StructureResult:
    """
    Data structure representing the outcome of the StructureEngine calculation.
    Backward compatibility maintained with 'score' and 'direction'.
    """
    score: int
    direction: str
    current_structure: str = "Neutral"
    last_bos: str = "None"
    last_choch: str = "None"
    supply_zone: str = "None"
    demand_zone: str = "None"
    reasons: List[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class StructureEngine:
    def __init__(self) -> None:
        logger.debug("StructureEngine (MSE) instantiated securely.")

    def _detect_swings(self, df: pd.DataFrame, window: int = 5) -> tuple[pd.Series, pd.Series]:
        """
        Dynamically detects historical swing highs and lows using a centered rolling window.
        Returns Pandas Series with datetime index.
        """
        is_swing_high = df['High'] == df['High'].rolling(window=window, center=True).max()
        is_swing_low = df['Low'] == df['Low'].rolling(window=window, center=True).min()
        
        swing_highs = df['High'][is_swing_high].dropna()
        swing_lows = df['Low'][is_swing_low].dropna()
        
        return swing_highs, swing_lows
        
    def _find_zones(self, swings: pd.Series, tolerance_pct: float = 0.01) -> str:
        """
        Detects if multiple swings happened around the same price level, indicating a zone.
        """
        if len(swings) < 2:
            return "None"
            
        prices = swings.values
        for i in range(len(prices) - 1, 0, -1):
            p1 = prices[i]
            for j in range(i - 1, max(-1, i - 5), -1):
                p2 = prices[j]
                if abs(p1 - p2) / max(p1, p2) <= tolerance_pct:
                    return f"Active near {round((p1+p2)/2, 2)}"
        return "None"

    def calculate(
        self,
        df: Optional[pd.DataFrame] = None,
        swing_highs: List[float] = None,
        swing_lows: List[float] = None,
        previous_structure: str = "NEUTRAL",
        **kwargs
    ) -> StructureResult:
        
        score: int = 25  # Base Weak Structure
        reasons: List[str] = []
        direction: str = "NEUTRAL"
        current_structure: str = "Neutral"
        last_bos: str = "None"
        last_choch: str = "None"
        
        if df is None or df.empty or len(df) < 15:
            return StructureResult(
                score=0, direction="NEUTRAL", current_structure="Neutral",
                reasons=["Insufficient data for StructureEngine"]
            )
            
        s_highs_series, s_lows_series = self._detect_swings(df, window=5)
        
        if len(s_highs_series) < 2 or len(s_lows_series) < 2:
            return StructureResult(
                score=25, direction="NEUTRAL", current_structure="Neutral",
                reasons=["Not enough swings detected to form structure."]
            )
            
        # Get the last two highs and lows
        h1, h2 = s_highs_series.iloc[-2], s_highs_series.iloc[-1]
        l1, l2 = s_lows_series.iloc[-2], s_lows_series.iloc[-1]
        
        hh = h2 > h1
        hl = l2 > l1
        lh = h2 < h1
        ll = l2 < l1
        
        # 1. Evaluate Structure Sequence
        if hh and hl:
            current_structure = "Bullish Structure"
            direction = "BULLISH"
            score += 25
            reasons.append("Bullish Structure (HH + HL) detected.")
        elif lh and ll:
            current_structure = "Bearish Structure"
            direction = "BEARISH"
            score += 25
            reasons.append("Bearish Structure (LH + LL) detected.")
        elif hh and ll:
            current_structure = "Expanding Structure"
            reasons.append("Expanding/Volatile Structure (HH + LL).")
        elif lh and hl:
            current_structure = "Contracting Structure"
            reasons.append("Contracting Structure (LH + HL) - Consolidation.")
            
        # 2. Evaluate BOS (Break of Structure) & CHoCH (Change of Character)
        current_close = df['Close'].iloc[-1]
        current_high = df['High'].iloc[-1]
        current_low = df['Low'].iloc[-1]
        recent_vol = df['Volume'].iloc[-3:].mean()
        avg_vol = df['Volume'].mean()
        
        vol_confirmed = recent_vol > avg_vol * 1.1
        
        bullish_break = current_close > h2
        bearish_break = current_close < l2
        
        # Bullish BOS = breaking higher high in a bullish trend
        # Bullish CHoCH = breaking lower high in a bearish trend
        if bullish_break:
            if direction == "BULLISH" or lh:
                if lh:
                    last_choch = "Bullish CHoCH"
                    reasons.append(f"Bullish CHoCH: Price closed above last Lower High ({h2:.2f}).")
                    score += 15
                else:
                    last_bos = "Bullish BOS"
                    reasons.append(f"Bullish BOS: Price broke above last Higher High ({h2:.2f}).")
                    score += 20
                if vol_confirmed:
                    reasons.append("Breakout confirmed by Volume Surge.")
                    score += 10
            
        elif bearish_break:
            if direction == "BEARISH" or hl:
                if hl:
                    last_choch = "Bearish CHoCH"
                    reasons.append(f"Bearish CHoCH: Price closed below last Higher Low ({l2:.2f}).")
                    score -= 10
                else:
                    last_bos = "Bearish BOS"
                    reasons.append(f"Bearish BOS: Price broke below last Lower Low ({l2:.2f}).")
                    score -= 10
                if vol_confirmed:
                    reasons.append("Breakdown confirmed by heavy selling volume.")
        
        # 3. Detect Fake Breakouts (Traps)
        fake_breakout_high = (current_high > h2) and (current_close <= h2)
        fake_breakout_low = (current_low < l2) and (current_close >= l2)
        
        if fake_breakout_high:
            reasons.append("Bull Trap: Upside Fake Breakout detected.")
            score -= 15
        elif fake_breakout_low:
            reasons.append("Bear Trap: Downside Fake Breakdown detected.")
            score += 15
            
        # 4. Supply and Demand Zones
        supply_zone = self._find_zones(s_highs_series)
        demand_zone = self._find_zones(s_lows_series)
        
        if supply_zone != "None":
            reasons.append(f"Supply Zone {supply_zone}.")
        if demand_zone != "None":
            reasons.append(f"Demand Zone {demand_zone}.")
            
        # Normalize score 0-100
        score = max(0, min(100, score))
        
        if score >= 90:
            reasons.append("Structure Quality: Perfect Structure.")
        elif score >= 70:
            reasons.append("Structure Quality: Strong Structure.")
        elif score >= 50:
            reasons.append("Structure Quality: Healthy Structure.")
        else:
            reasons.append("Structure Quality: Weak Structure.")

        # Expose raw structural markers for Risk Reward Engine
        details = {
            "swing_high": float(h2) if h2 is not None else 0.0,
            "swing_low": float(l2) if l2 is not None else 0.0,
            "supply_zone": supply_zone,
            "demand_zone": demand_zone
        }

        return StructureResult(
            score=score,
            direction=direction,
            current_structure=current_structure,
            last_bos=last_bos,
            last_choch=last_choch,
            supply_zone=supply_zone,
            demand_zone=demand_zone,
            reasons=reasons,
            details=details
        )
