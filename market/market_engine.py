"""
Market Engine module for RAHUUL_RADAR.
Analyzes aggregate market data to determine overall market state, bias, and volatility.
"""
from dataclasses import dataclass
from typing import List

from utils.logger import get_logger
from market.data_provider import OHLCV

logger = get_logger(__name__)


@dataclass
class MarketState:
    """
    Data structure representing the calculated state of the overall market.
    """
    trend: str
    strength: float
    volatility: float
    market_bias: str
    confidence: float


class MarketEngine:
    """
    Engine responsible for calculating and interpreting macroeconomic and market-wide 
    technical indicators (EMA, VWAP, ATR, ADX) to define the baseline market regime.
    """

    def __init__(self) -> None:
        """Initializes the MarketEngine."""
        logger.info("MarketEngine initialized securely.")

    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculates the Exponential Moving Average (EMA)."""
        if not prices or len(prices) < period:
            return []
            
        ema = []
        multiplier = 2.0 / (period + 1.0)
        
        # Initial SMA for the first 'period'
        initial_sma = sum(prices[:period]) / period
        
        # Pad the beginning with 0.0 to match the length
        for _ in range(period - 1):
            ema.append(0.0)
            
        ema.append(initial_sma)
        
        for price in prices[period:]:
            current_ema = (price - ema[-1]) * multiplier + ema[-1]
            ema.append(current_ema)
            
        return ema

    def _calculate_vwap(self, data: List[OHLCV]) -> float:
        """Calculates the Volume Weighted Average Price (VWAP) for the given dataset."""
        if not data:
            return 0.0
        
        cumulative_pv = 0.0
        cumulative_vol = 0.0
        
        for candle in data:
            typical_price = (candle.high + candle.low + candle.close) / 3.0
            cumulative_pv += typical_price * candle.volume
            cumulative_vol += candle.volume
            
        if cumulative_vol == 0:
            return data[-1].close
            
        return cumulative_pv / cumulative_vol

    def _calculate_atr(self, data: List[OHLCV], period: int = 14) -> float:
        """Calculates the Average True Range (ATR) as a volatility measure."""
        if len(data) <= period:
            return 0.0
            
        true_ranges = []
        for i in range(1, len(data)):
            high = data[i].high
            low = data[i].low
            prev_close = data[i-1].close
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_ranges.append(max(tr1, tr2, tr3))
            
        # Simplified Moving Average of TR
        atr = sum(true_ranges[-period:]) / period
        return atr

    def _calculate_adx(self, data: List[OHLCV], period: int = 14) -> float:
        """
        Calculates a functional approximation of the Average Directional Index (ADX)
        to measure trend strength.
        """
        if len(data) <= period:
            return 0.0
            
        plus_dm_list = []
        minus_dm_list = []
        tr_list = []
        
        for i in range(1, len(data)):
            up_move = data[i].high - data[i-1].high
            down_move = data[i-1].low - data[i].low
            
            if up_move > down_move and up_move > 0:
                plus_dm_list.append(up_move)
            else:
                plus_dm_list.append(0.0)
                
            if down_move > up_move and down_move > 0:
                minus_dm_list.append(down_move)
            else:
                minus_dm_list.append(0.0)
                
            tr = max(
                data[i].high - data[i].low,
                abs(data[i].high - data[i-1].close),
                abs(data[i].low - data[i-1].close)
            )
            tr_list.append(tr)
            
        # Simplified Wilder's smoothing logic for immediate reading
        smoothed_plus_dm = sum(plus_dm_list[-period:])
        smoothed_minus_dm = sum(minus_dm_list[-period:])
        smoothed_tr = sum(tr_list[-period:])
        
        if smoothed_tr == 0:
            return 0.0
            
        plus_di = 100 * (smoothed_plus_dm / smoothed_tr)
        minus_di = 100 * (smoothed_minus_dm / smoothed_tr)
        
        dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-8))
        return dx

    def evaluate(self, market_data: List[OHLCV], df=None) -> MarketState:
        """
        Evaluates the market OHLCV data to generate a cohesive MarketState.
        
        Args:
            market_data: List of OHLCV data for the benchmark index (e.g., NIFTY).
            df: Optional precomputed pandas DataFrame for performance optimization.
            
        Returns:
            MarketState: The evaluated condition of the overall market.
        """
        logger.debug(f"Evaluating market state over {len(market_data)} periods.")
        
        # Failsafe for insufficient data
        if not market_data or len(market_data) < 50:
            logger.warning("Insufficient data for reliable market evaluation. Defaulting to NEUTRAL.")
            return MarketState(
                trend="NEUTRAL",
                strength=0.0,
                volatility=0.0,
                market_bias="NEUTRAL",
                confidence=0.0
            )
            
        closes = [c.close for c in market_data]
        current_close = closes[-1]
        
        if df is not None and not df.empty and 'EMA20' in df.columns:
            # Bypass pure Python loop bottlenecks by extracting cached vector values
            ema20 = df['EMA20'].iloc[-1]
            ema50 = df['EMA50'].iloc[-1]
            vwap = df['VWAP'].iloc[-1] if 'VWAP' in df.columns else self._calculate_vwap(market_data)
            atr = df['ATR'].iloc[-1] if 'ATR' in df.columns else self._calculate_atr(market_data, 14)
            adx = df['ADX'].iloc[-1] if 'ADX' in df.columns else self._calculate_adx(market_data, 14)
        else:
            # Fallback to legacy calculations
            ema20_list = self._calculate_ema(closes, 20)
            ema50_list = self._calculate_ema(closes, 50)
            
            ema20 = ema20_list[-1] if ema20_list else current_close
            ema50 = ema50_list[-1] if ema50_list else current_close
            
            vwap = self._calculate_vwap(market_data)
            atr = self._calculate_atr(market_data, 14)
            adx = self._calculate_adx(market_data, 14)
        
        # 1. Determine Core Trend
        if current_close > ema20 and ema20 > ema50:
            trend = "BULLISH"
        elif current_close < ema20 and ema20 < ema50:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"
            
        # 2. Determine Market Bias (incorporating VWAP intraday anchor)
        if current_close > vwap and trend == "BULLISH":
            bias = "STRONG_BULL"
        elif current_close < vwap and trend == "BEARISH":
            bias = "STRONG_BEAR"
        else:
            bias = "NEUTRAL"
            
        # 3. Calculate Confidence Score (0-100)
        confidence = 0.0
        if trend != "SIDEWAYS":
            confidence += 40.0
        if (bias == "STRONG_BULL" and trend == "BULLISH") or (bias == "STRONG_BEAR" and trend == "BEARISH"):
            confidence += 30.0
            
        # ADX > 20 indicates strong directional conviction
        if adx > 20.0:
            confidence += 30.0
        elif adx > 15.0:
            confidence += 15.0
            
        logger.info(f"Market Evaluation Complete: Trend={trend}, Bias={bias}, ADX={adx:.2f}")
            
        return MarketState(
            trend=trend,
            strength=round(adx, 2),
            volatility=round(atr, 2),
            market_bias=bias,
            confidence=round(confidence, 2)
        )
