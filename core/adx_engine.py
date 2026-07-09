"""
MASTER-21: ADX Trend Strength Engine
Confirmation engine designed to measure the strength of an existing trend.
Does not generate standalone BUY/SELL signals.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class AdxResult:
    adx: float = 0.0
    plus_di: float = 0.0
    minus_di: float = 0.0
    trend_strength: str = "Unknown"
    direction: str = "Sideways"
    score: int = 0
    reasons: List[str] = field(default_factory=list)
    isValidForBuy: bool = False
    isValidForSell: bool = False


class AdxEngine:
    def __init__(self, period: int = 14):
        self.period = period
        
    def _rma(self, x: pd.Series, n: int) -> pd.Series:
        """Wilder's Smoothing (Running Moving Average)"""
        return x.ewm(alpha=1/n, adjust=False).mean()

    def _calculate_adx(self, df: pd.DataFrame) -> tuple:
        """
        Calculates ADX, +DI, and -DI.
        Returns the latest (adx, +di, -di).
        """
        if len(df) < self.period * 2:
            return 0.0, 0.0, 0.0
            
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
        
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        tr_rma = self._rma(tr, self.period)
        plus_dm_rma = self._rma(pd.Series(plus_dm), self.period)
        minus_dm_rma = self._rma(pd.Series(minus_dm), self.period)
        
        # Avoid division by zero
        tr_rma = np.where(tr_rma == 0, 1e-10, tr_rma)
        
        plus_di = 100 * (plus_dm_rma / tr_rma)
        minus_di = 100 * (minus_dm_rma / tr_rma)
        
        denom = plus_di + minus_di
        denom = np.where(denom == 0, 1e-10, denom)
        
        dx = 100 * (abs(plus_di - minus_di) / denom)
        dx = pd.Series(dx).fillna(0)
        
        adx = self._rma(dx, self.period)
        
        return round(adx.iloc[-1], 2), round(plus_di.iloc[-1], 2), round(minus_di.iloc[-1], 2)

    def evaluate(self, df: pd.DataFrame) -> AdxResult:
        if df is None or df.empty:
            return AdxResult(reasons=["Insufficient Data for ADX"])
            
        try:
            # TASK-3: Use Cached Indicators if present
            if 'ADX_14' in df.columns:
                adx = float(df['ADX_14'].iloc[-1])
                p_di = float(df['PLUS_DI_14'].iloc[-1])
                m_di = float(df['MINUS_DI_14'].iloc[-1])
            else:
                adx, p_di, m_di = self._calculate_adx(df)
            
            score = 0
            trend_strength = "Unknown"
            reasons = []
            
            # 1. Trend Strength Classification & Scoring
            if adx < 20:
                trend_strength = "Weak Trend"
                score = int(adx * (35.0 / 20.0))  # Max 35
                reasons.append(f"ADX < 20 ({adx}): Weak Trend. Low Conviction. Penalty applied.")
            elif adx < 25:
                trend_strength = "Trend Starting"
                score = 35 + int((adx - 20) * (20.0 / 5.0)) # 35 to 55
                reasons.append(f"ADX 20-25 ({adx}): Trend Starting. Neutral.")
            elif adx < 35:
                trend_strength = "Healthy Trend"
                score = 55 + int((adx - 25) * (30.0 / 10.0)) # 55 to 85
                reasons.append(f"ADX 25-35 ({adx}): Healthy Trend. Positive Score.")
            elif adx < 50:
                trend_strength = "Strong Trend"
                score = 85 + int((adx - 35) * (15.0 / 15.0)) # 85 to 100 (Wait, max is 95?)
                # Adjusted to hit 95 at ADX 45, meaning (adx-35)*10/10... 
                # Let's use a simpler mapping matching user example:
                # ADX 35 = 85, ADX 45 = 95 -> Slope is 1
                score = 85 + int((adx - 35) * 1.0)
                reasons.append(f"ADX 35-50 ({adx}): Strong Trend. High Score.")
            else:
                trend_strength = "Very Strong Trend"
                score = min(100, 100) # Max 100
                reasons.append(f"ADX > 50 ({adx}): Very Strong Trend. Maximum Confirmation.")
                
            # 2. Direction Analysis
            if p_di > m_di:
                direction = "Bullish"
            elif m_di > p_di:
                direction = "Bearish"
            else:
                direction = "Sideways"
                
            if adx < 20:
                direction = "Sideways"
                
            # 3. Validation Logic
            is_valid_buy = (p_di > m_di) and (adx > 22)
            is_valid_sell = (m_di > p_di) and (adx > 22)
            
            if is_valid_buy:
                reasons.append(f"BUY Validated (+DI > -DI and ADX > 22).")
            elif is_valid_sell:
                reasons.append(f"SELL Validated (-DI > +DI and ADX > 22).")
            else:
                reasons.append(f"Validation Pending: Not meeting strict entry rules.")
                
            return AdxResult(
                adx=adx,
                plus_di=p_di,
                minus_di=m_di,
                trend_strength=trend_strength,
                direction=direction,
                score=score,
                reasons=reasons,
                isValidForBuy=is_valid_buy,
                isValidForSell=is_valid_sell
            )
            
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return AdxResult(reasons=[f"Calculation Error: {str(e)}"])
