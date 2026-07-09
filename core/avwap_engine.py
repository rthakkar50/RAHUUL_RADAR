"""
MASTER-22: Anchored VWAP (AVWAP) Institutional Engine
Confirmation engine designed to identify institutional price zones.
Does not generate standalone BUY/SELL signals.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AvwapResult:
    avwap_value: float = 0.0
    distance_pct: float = 0.0
    position: str = "Unknown"  # Premium, Fair Value, Discount
    institutional_bias: str = "Neutral" # Bullish, Bearish, Neutral
    score: int = 0
    anchor_point_type: str = "None"
    reasons: List[str] = field(default_factory=list)


class AvwapEngine:
    def __init__(self):
        pass
        
    def _find_anchor_index(self, df: pd.DataFrame) -> tuple:
        """
        Automatically detects the best anchor point.
        Prioritizes:
        1. Major Volume Spike (last 6 months)
        2. 52-Week High / Low (whichever is more recent)
        Returns (index_int, anchor_type_string)
        """
        n = len(df)
        if n < 20:
            return 0, "Default (Start of Data)"
            
        # 1. Look for Major Volume Spike in last 130 periods (~6 months)
        lookback_vol = min(130, n)
        recent_df = df.iloc[-lookback_vol:]
        
        avg_vol = recent_df['Volume'].mean()
        max_vol_idx = recent_df['Volume'].idxmax()
        max_vol = recent_df.loc[max_vol_idx, 'Volume']
        
        if max_vol > avg_vol * 3.0:
            idx = df.index.get_loc(max_vol_idx)
            return idx, f"Volume Spike ({max_vol_idx.date() if hasattr(max_vol_idx, 'date') else max_vol_idx})"
            
        # 2. Fallback to 52-Week High or Low
        lookback_52w = min(252, n)
        df_52w = df.iloc[-lookback_52w:]
        
        high_idx = df_52w['High'].idxmax()
        low_idx = df_52w['Low'].idxmin()
        
        # Get integer locations
        high_iloc = df.index.get_loc(high_idx)
        low_iloc = df.index.get_loc(low_idx)
        
        # Choose the more recent one
        if high_iloc > low_iloc:
            return high_iloc, f"52W High ({high_idx.date() if hasattr(high_idx, 'date') else high_idx})"
        else:
            return low_iloc, f"52W Low ({low_idx.date() if hasattr(low_idx, 'date') else low_idx})"

    def _calculate_avwap(self, df: pd.DataFrame, anchor_idx: int) -> pd.Series:
        """
        Calculates AVWAP starting from anchor_idx.
        """
        df_anchored = df.iloc[anchor_idx:].copy()
        
        typical_price = (df_anchored['High'] + df_anchored['Low'] + df_anchored['Close']) / 3.0
        volume = df_anchored['Volume']
        
        cum_vol_price = (typical_price * volume).cumsum()
        cum_vol = volume.cumsum()
        
        # Avoid division by zero
        cum_vol = np.where(cum_vol == 0, 1e-10, cum_vol)
        
        avwap = cum_vol_price / cum_vol
        return avwap

    def evaluate(self, df: pd.DataFrame) -> AvwapResult:
        if df is None or df.empty or len(df) < 5:
            return AvwapResult(reasons=["Insufficient Data for AVWAP"])
            
        try:
            anchor_idx, anchor_type = self._find_anchor_index(df)
            avwap_series = self._calculate_avwap(df, anchor_idx)
            
            current_avwap = avwap_series.iloc[-1]
            current_price = df['Close'].iloc[-1]
            
            # Calculate distance %
            distance_pct = ((current_price - current_avwap) / current_avwap) * 100.0
            
            position = "Fair Value"
            bias = "Neutral"
            score = 50
            reasons = []
            
            reasons.append(f"Anchor Point: {anchor_type}")
            
            # Distance Classification
            if distance_pct > 2.0:
                position = "Premium"
                bias = "Bullish"
                score = 75
                reasons.append(f"Price is at Premium (>2% above AVWAP). Institutional Bias: Bullish.")
            elif distance_pct < -2.0:
                position = "Discount"
                bias = "Bearish"
                score = 20
                reasons.append(f"Price is at Discount (<2% below AVWAP). Institutional Bias: Bearish.")
            else:
                position = "Fair Value"
                bias = "Neutral"
                score = 50
                reasons.append(f"Price is near Fair Value (within ±2% of AVWAP).")
                
            # Volume Confirmation (Institutional Strength/Weakness)
            # Compare recent 3-day volume average against 20-day volume average
            if len(df) >= 20:
                vol_3d = df['Volume'].iloc[-3:].mean()
                vol_20d = df['Volume'].iloc[-20:].mean()
                
                if position == "Premium" and vol_3d > vol_20d * 1.2:
                    score = 95
                    reasons.append("Institutional Strength: Price above AVWAP + Increasing Volume.")
                elif position == "Discount" and vol_3d > vol_20d * 1.2:
                    score = 10
                    reasons.append("Institutional Weakness: Price below AVWAP + Heavy Selling.")
                    
            # Fake Breakout / Retest Logic
            # Check if price recently crossed AVWAP and reversed
            if len(avwap_series) >= 5:
                # Look at last 5 days
                recent_closes = df['Close'].iloc[-5:]
                recent_avwaps = avwap_series.iloc[-5:]
                
                # Breakout logic
                if recent_closes.iloc[-2] > recent_avwaps.iloc[-2] and recent_closes.iloc[-1] < recent_avwaps.iloc[-1]:
                    reasons.append("Flag: Possible Fake Breakout (Crossed above AVWAP, returned below).")
                    score -= 15
                # Breakdown logic
                elif recent_closes.iloc[-2] < recent_avwaps.iloc[-2] and recent_closes.iloc[-1] > recent_avwaps.iloc[-1]:
                    reasons.append("Flag: Possible Bear Trap / Fake Breakdown (Crossed below AVWAP, returned above).")
                    score += 15
                    
                # Retest holds
                if position == "Premium" and recent_closes.min() >= recent_avwaps.max() * 0.99 and distance_pct < 5.0:
                     reasons.append("Positive Confirmation: Retest of AVWAP holding.")
                     score += 10
                     
            # Clamp score 0-100
            score = max(0, min(100, score))
            
            return AvwapResult(
                avwap_value=round(current_avwap, 2),
                distance_pct=round(distance_pct, 2),
                position=position,
                institutional_bias=bias,
                score=score,
                anchor_point_type=anchor_type,
                reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"Error calculating AVWAP: {e}")
            return AvwapResult(reasons=[f"Calculation Error: {str(e)}"])
