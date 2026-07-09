"""
Trend calculation engine for RAHUUL_RADAR.
Analyzes moving averages, VWAP, and price action to determine the primary market trend direction and score.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import numpy as np

from market.data_provider import OHLCV
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TrendResult:
    """
    Data structure representing the outcome of the TrendEngine calculation.
    """
    score: int
    direction: str
    reasons: List[str] = field(default_factory=list)
    trend_strength: float = 0.0
    ema20: float = 0.0
    ema50: float = 0.0
    vwap: float = 0.0
    details: dict = field(default_factory=dict)


class TrendEngine:
    """
    Engine responsible for executing pure mathematical logic to determine trend strength.
    Computes moving averages and VWAP dynamically from raw pandas DataFrames.
    """
    
    def _calculate_supertrend(self, df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
        """Calculates Supertrend using Numpy for performance."""
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        tr2[0] = 0
        tr3[0] = 0
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        atr = pd.Series(tr).ewm(alpha=1/period, adjust=False).mean().values
        
        hl2 = (high + low) / 2
        basic_ub = hl2 + (multiplier * atr)
        basic_lb = hl2 - (multiplier * atr)
        
        final_ub = np.zeros(len(df))
        final_lb = np.zeros(len(df))
        supertrend_is_up = np.ones(len(df), dtype=bool)
        
        final_ub[0] = basic_ub[0]
        final_lb[0] = basic_lb[0]
        
        for i in range(1, len(df)):
            if basic_ub[i] < final_ub[i-1] or close[i-1] > final_ub[i-1]:
                final_ub[i] = basic_ub[i]
            else:
                final_ub[i] = final_ub[i-1]
                
            if basic_lb[i] > final_lb[i-1] or close[i-1] < final_lb[i-1]:
                final_lb[i] = basic_lb[i]
            else:
                final_lb[i] = final_lb[i-1]
                
            if supertrend_is_up[i-1] and close[i] <= final_lb[i]:
                supertrend_is_up[i] = False
            elif not supertrend_is_up[i-1] and close[i] >= final_ub[i]:
                supertrend_is_up[i] = True
            else:
                supertrend_is_up[i] = supertrend_is_up[i-1]
                
        return supertrend_is_up

    def calculate(
        self,
        df: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> TrendResult:
        """
        Calculates the trend score and directional bias dynamically from a DataFrame.
        Prioritizes dynamic calculation from `df` if provided.
        Falls back to explicit parameters to maintain interface backward compatibility.
        """
        score: int = 0
        reasons: List[str] = []
        trend_strength: float = 0.0
        
        close = kwargs.get('close', 0.0)
        ema20 = kwargs.get('ema20', 0.0)
        ema50 = kwargs.get('ema50', 0.0)
        vwap = kwargs.get('vwap', 0.0)
        ema20_slope = kwargs.get('ema20_slope', 0.0)
        higher_tf_alignment = kwargs.get('higher_tf_alignment', False)
        st_bullish = False

        # If real OHLCV DataFrame is provided, calculate everything dynamically.
        if df is not None and not df.empty and len(df) >= 50:
            close_series = df['Close']
            close = float(close_series.iloc[-1])
            
            # TASK-3: Use Cached Indicators if present
            if 'EMA20' in df.columns:
                ema20_series = df['EMA20']
                ema50_series = df['EMA50']
            else:
                ema20_series = close_series.ewm(span=20, adjust=False).mean()
                ema50_series = close_series.ewm(span=50, adjust=False).mean()
                
            ema20 = float(ema20_series.iloc[-1])
            ema50 = float(ema50_series.iloc[-1])
            
            if 'VWAP' in df.columns:
                vwap_series = df['VWAP']
            else:
                typical_price = (df['High'] + df['Low'] + df['Close']) / 3.0
                vwap_series = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
            vwap = float(vwap_series.iloc[-1])
            
            # Calculate EMA20 slope over the last 5 candles using numpy polyfit
            if len(ema20_series) >= 5:
                y = ema20_series.tail(5).values
                x = np.arange(len(y))
                slope, _ = np.polyfit(x, y, 1)
                ema20_slope = float(slope)
                
            # Proxy higher timeframe alignment via EMA50 slope
            if len(ema50_series) >= 5:
                y_50 = ema50_series.tail(5).values
                x = np.arange(len(y_50))
                slope_50, _ = np.polyfit(x, y_50, 1)
                higher_tf_alignment = float(slope_50) > 0.0
                
            # Calculate raw trend strength as percentage deviation from EMA50
            if ema50 > 0:
                trend_strength = round(((close - ema50) / ema50) * 100, 2)
                
            # Calculate Supertrend
            st_series = self._calculate_supertrend(df)
            st_bullish = bool(st_series[-1])

        # --- Rule Implementations ---
        
        # 1. EMA20 > EMA50 = +8
        if ema20 > ema50:
            score += 8
            reasons.append("EMA20 above EMA50")
            
        # 2. Latest Close > EMA20 = +5
        if close > ema20:
            score += 5
            reasons.append("Price above EMA20")
            
        # 3. Latest Close > VWAP = +4
        if close > vwap:
            score += 4
            reasons.append("Price above VWAP")
            
        # 4. EMA20 slope positive over last 5 candles = +4
        if ema20_slope > 0.0:
            score += 4
            reasons.append("EMA20 rising")
            
        # 5. Higher Timeframe trend confirmation = +4
        if higher_tf_alignment:
            score += 4
            reasons.append("Higher timeframe confirmed")
            
        # 6. Supertrend Bullish = +5
        if st_bullish:
            score += 5
            reasons.append("Supertrend Bullish (Trend Confirmation)")
            
        # Determine categorical direction based on absolute score rules
        if score >= 26:
            direction = "STRONG_BULL"
        elif score >= 21:
            direction = "BULL"
        elif score >= 14:
            direction = "NEUTRAL"
        elif score >= 7:
            direction = "BEAR"
        else:
            direction = "STRONG_BEAR"
            
        details = {
            "Trend": "🟢 Strong Bullish" if direction in ("STRONG_BULL", "BULL") else "🟡 Neutral" if direction == "NEUTRAL" else "🔴 Bearish",
            "EMA20": "🟢 Above" if close > ema20 else "🔴 Below",
            "EMA50": "🟢 Above" if close > ema50 else "🔴 Below",
            "VWAP":  "🟢 Above VWAP" if close > vwap else "🔴 Below VWAP"
        }
            
        logger.debug(f"Trend Calculation Complete | Score: {score}/25 | Direction: {direction}")
            
        return TrendResult(
            score=score,
            direction=direction,
            reasons=reasons,
            trend_strength=trend_strength,
            ema20=ema20 if 'ema20' in locals() else kwargs.get('ema20', 0.0),
            ema50=ema50 if 'ema50' in locals() else kwargs.get('ema50', 0.0),
            vwap=vwap if 'vwap' in locals() else kwargs.get('vwap', 0.0),
            details=details
        )
