"""
MASTER-23: Multi-Timeframe Confluence Engine (MTCE)
Verifies multi-timeframe alignment across Weekly, Daily, and 4H timeframes.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
from core.trend_engine import TrendEngine

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class MtfResult:
    weekly_trend: str = "Unknown"
    daily_trend: str = "Unknown"
    h4_trend: str = "Unknown"
    confluence_score: int = 0
    alignment_status: str = "No Alignment"
    decision: str = "WAIT"
    reasons: List[str] = field(default_factory=list)


class MtfEngine:
    def __init__(self):
        self.trend_engine = TrendEngine()
        
    def _evaluate_trend(self, df: pd.DataFrame) -> str:
        if df is None or df.empty or len(df) < 20:
            return "Unknown"
        result = self.trend_engine.calculate(df=df)
        return result.direction

    def evaluate(self, df_weekly: pd.DataFrame, df_daily: pd.DataFrame, df_4h: pd.DataFrame) -> MtfResult:
        try:
            w_trend = self._evaluate_trend(df_weekly)
            d_trend = self._evaluate_trend(df_daily)
            h4_trend = self._evaluate_trend(df_4h)
            
            score = 20
            alignment_status = "No Alignment"
            decision = "WAIT"
            reasons = []
            
            reasons.append(f"Weekly Trend: {w_trend}")
            reasons.append(f"Daily Trend: {d_trend}")
            reasons.append(f"4H Trend: {h4_trend}")
            
            is_w_bull = "BULL" in w_trend.upper()
            is_d_bull = "BULL" in d_trend.upper()
            is_4h_bull = "BULL" in h4_trend.upper()
            
            is_w_bear = "BEAR" in w_trend.upper()
            is_d_bear = "BEAR" in d_trend.upper()
            is_4h_bear = "BEAR" in h4_trend.upper()
            
            if is_w_bull and is_d_bull and is_4h_bull:
                score = 100
                alignment_status = "Perfect Alignment"
                decision = "Strong Buy Environment"
                reasons.append("Strong Bullish Confluence across all timeframes.")
            elif is_w_bear and is_d_bear and is_4h_bear:
                score = 100
                alignment_status = "Perfect Alignment"
                decision = "Strong Sell Environment"
                reasons.append("Strong Bearish Confluence across all timeframes.")
            elif is_w_bull and is_d_bear:
                score = 30
                alignment_status = "Major Conflict"
                decision = "Conflict"
                reasons.append("Major Conflict: Weekly is Bullish but Daily is Bearish. Reduce Confidence.")
            elif is_w_bear and is_d_bull:
                score = 30
                alignment_status = "Major Conflict"
                decision = "Conflict"
                reasons.append("Major Conflict: Weekly is Bearish but Daily is Bullish. Reduce Confidence.")
            elif is_d_bull and is_4h_bear:
                score = 50
                alignment_status = "Partial Alignment"
                decision = "Wait for Confirmation"
                reasons.append("Wait: Daily is Bullish but 4H entry timeframe is Bearish. No immediate entry.")
            elif is_d_bear and is_4h_bull:
                score = 50
                alignment_status = "Partial Alignment"
                decision = "Wait for Confirmation"
                reasons.append("Wait: Daily is Bearish but 4H entry timeframe is Bullish. No immediate entry.")
            elif w_trend == "Sideways":
                score = 40
                alignment_status = "No Alignment"
                decision = "Wait for Confirmation"
                reasons.append("Weekly Trend is Sideways. Reduce Position Size and increase filter strictness.")
            else:
                score = 55
                alignment_status = "Partial Alignment"
                decision = "Wait for Confirmation"
                reasons.append("Partial alignment. Awaiting stronger confluence.")
                
            return MtfResult(
                weekly_trend=w_trend,
                daily_trend=d_trend,
                h4_trend=h4_trend,
                confluence_score=score,
                alignment_status=alignment_status,
                decision=decision,
                reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"Error calculating MTCE: {e}")
            return MtfResult(reasons=[f"Calculation Error: {str(e)}"])
