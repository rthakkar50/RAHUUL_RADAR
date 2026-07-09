"""
Momentum calculation engine for RAHUUL_RADAR.
Evaluates the speed and directional strength of price action using RSI and ADX/DMI.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MomentumResult:
    """
    Data structure representing the outcome of the MomentumEngine calculation.
    """
    score: int
    direction: str
    rsi: float
    adx: float
    plus_di: float
    minus_di: float
    momentum_strength: float = 0.0
    reasons: List[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class MomentumEngine:
    """
    Engine responsible for executing pure mathematical logic to determine momentum strength.
    Uses precise point-based allocations based on RSI positioning and ADX/DMI alignment.
    Computes RSI, ADX, and DI dynamically from raw pandas DataFrames.
    """
    
    def __init__(self) -> None:
        """Initializes the MomentumEngine."""
        logger.debug("MomentumEngine instantiated securely.")

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculates Wilder's Relative Strength Index (RSI)."""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        
        # Wilder's Smoothing
        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14):
        """Calculates Average Directional Index (ADX) and Directional Indicators (+DI, -DI)."""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        up = high - high.shift(1)
        down = low.shift(1) - low
        
        plus_dm = np.where((up > down) & (up > 0), up, 0.0)
        minus_dm = np.where((down > up) & (down > 0), down, 0.0)
        
        plus_dm = pd.Series(plus_dm, index=df.index)
        minus_dm = pd.Series(minus_dm, index=df.index)
        
        # Wilder's Smoothing
        tr_smooth = tr.ewm(alpha=1/period, adjust=False).mean()
        plus_dm_smooth = plus_dm.ewm(alpha=1/period, adjust=False).mean()
        minus_dm_smooth = minus_dm.ewm(alpha=1/period, adjust=False).mean()
        
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()
        
        return adx, plus_di, minus_di
        
    def _calculate_macd(self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculates MACD and Signal Line."""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, signal_line
        
    def calculate(
        self, 
        df: Optional[pd.DataFrame] = None,
        rsi: float = 0.0, 
        rsi_rising: bool = False, 
        adx: float = 0.0, 
        plus_di: float = 0.0, 
        minus_di: float = 0.0,
        **kwargs
    ) -> MomentumResult:
        """
        Calculates the aggregate momentum score and categorical directional bias.
        Prioritizes dynamic calculation from `df` if provided.
        Falls back to explicit parameters to maintain interface backward compatibility.
        """
        score: int = 0
        reasons: List[str] = []
        momentum_strength: float = 0.0
        macd_val: float = 0.0
        macd_signal: float = 0.0

        if df is not None and not df.empty and len(df) >= 30:
            # TASK-3: Use Cached Indicators if present
            if 'RSI_14' in df.columns:
                rsi_series = df['RSI_14']
                rsi = float(rsi_series.iloc[-1])
            else:
                rsi_series = self._calculate_rsi(df['Close'], period=14)
                rsi = float(rsi_series.iloc[-1])
            
            # 2. RSI slope positive over last 5 candles (Linear Regression)
            if len(rsi_series) >= 5:
                y = rsi_series.tail(5).values
                x = np.arange(len(y))
                slope, _ = np.polyfit(x, y, 1)
                rsi_rising = float(slope) > 0.0
                
            # 3. Calculate ADX, +DI, -DI
            if 'ADX_14' in df.columns:
                adx = float(df['ADX_14'].iloc[-1])
                plus_di = float(df['PLUS_DI_14'].iloc[-1])
                minus_di = float(df['MINUS_DI_14'].iloc[-1])
            else:
                adx_series, plus_di_series, minus_di_series = self._calculate_adx(df, period=14)
                adx = float(adx_series.iloc[-1])
                plus_di = float(plus_di_series.iloc[-1])
                minus_di = float(minus_di_series.iloc[-1])
            
            # Momentum strength proxy (ADX represents trend/momentum strength magnitude)
            momentum_strength = round(adx, 2)
            
            # 4. Calculate MACD
            if 'MACD' in df.columns:
                macd_val = float(df['MACD'].iloc[-1])
                macd_signal = float(df['MACD_Signal'].iloc[-1])
            else:
                macd_series, signal_series = self._calculate_macd(df['Close'])
                macd_val = float(macd_series.iloc[-1])
                macd_signal = float(signal_series.iloc[-1])

        # --- Rule Implementations ---

        # Rule 1: RSI > 55 (+5)
        if rsi > 55.0:
            score += 5
            reasons.append("RSI above 55")
            
        # Rule 2: RSI slope positive over last 5 candles (+5)
        if rsi_rising:
            score += 5
            reasons.append("RSI rising")
            
        # Rule 3: ADX > 25 (+5)
        if adx > 25.0:
            score += 5
            reasons.append("ADX above 25")
            
        # Rule 4: +DI > -DI (+5)
        if plus_di > minus_di:
            score += 5
            reasons.append("+DI above -DI")
            
        # Rule 5: MACD > Signal & MACD > 0 (+5)
        if macd_val > macd_signal and macd_val > 0:
            score += 5
            reasons.append("MACD Bullish (Above Signal & Zero)")
            
        # Determine categorical direction based on absolute score rules
        if score >= 16:
            direction = "STRONG_BULL"
        elif score >= 11:
            direction = "BULL"
        elif score >= 6:
            direction = "NEUTRAL"
        elif score >= 3:
            direction = "BEAR"
        else:
            direction = "STRONG_BEAR"
            
        details = {
            "Momentum": "🟢 Increasing" if direction in ("STRONG_BULL", "BULL") else "🟡 Neutral" if direction == "NEUTRAL" else "🔴 Decreasing",
            "RSI": f"🟢 {rsi:.1f} (Bullish)" if rsi >= 55 else f"🟡 {rsi:.1f} (Neutral)" if rsi > 45 else f"🔴 {rsi:.1f} (Bearish)",
            "MACD": "🟢 Bullish" if direction in ("STRONG_BULL", "BULL") else "🔴 Bearish" # Approximate based on direction since ADX/MACD combined
        }
            
        logger.debug(f"Momentum Calculation Complete | Score: {score}/20 | Direction: {direction} | RSI: {rsi:.2f}")
        
        return MomentumResult(
            score=score,
            direction=direction,
            rsi=rsi,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            momentum_strength=momentum_strength,
            reasons=reasons,
            details=details
        )
