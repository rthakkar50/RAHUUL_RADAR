import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
from market.data_provider import OHLCV
from core.relative_strength_engine import RelativeStrengthEngine
from utils.logger import get_logger

logger = get_logger(__name__)

class StateCache:
    """
    Maintains the state of symbols across 5-minute Intraday scans to prevent 
    volatile memory loss and binary double-rejections.
    """
    _instance = None
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    @classmethod
    def get_instance(cls) -> 'StateCache':
        if cls._instance is None:
            cls._instance = StateCache()
        return cls._instance
        
    def add_or_update(self, symbol: str, stage: str, score: float, data: Dict = None):
        if symbol not in self.cache:
            self.cache[symbol] = {
                "discovery_timestamp": datetime.now().isoformat(),
                "symbol": symbol,
            }
        
        self.cache[symbol]["stage"] = stage
        self.cache[symbol]["current_score"] = score
        self.cache[symbol]["last_updated"] = datetime.now().isoformat()
        if data:
            self.cache[symbol]["data"] = data
            
    def get_state(self, symbol: str) -> Dict[str, Any]:
        return self.cache.get(symbol)
        
    def remove(self, symbol: str):
        if symbol in self.cache:
            del self.cache[symbol]


class DiscoveryEngine:
    """
    STAGE-1: DISCOVERY ENGINE
    Purely identifies tradable opportunities by checking raw movement and liquidity.
    Does NOT calculate entries, stops, AI scores, or elite validations.
    """
    
    def __init__(self):
        self.rs_engine = RelativeStrengthEngine()
        self.state_cache = StateCache.get_instance()
        
    def _reject(self, symbol: str, reason: str) -> Dict:
        return {
            "symbol": symbol,
            "status": "DISCOVERY_REJECT",
            "reason": reason,
            "stage": "Discovery",
            "timestamp": datetime.now().isoformat()
        }
        
    def _pass(self, symbol: str, reason: str, score: float = 50.0) -> Dict:
        self.state_cache.add_or_update(symbol, "DISCOVERY", score)
        return {
            "symbol": symbol,
            "status": "DISCOVERY_PASS",
            "reason": reason,
            "stage": "Discovery",
            "timestamp": datetime.now().isoformat(),
            "score": score
        }

    def df_from_ohlcv(self, ohlcv_list: List[OHLCV]) -> pd.DataFrame:
        if not ohlcv_list:
            return pd.DataFrame()
        df = pd.DataFrame([
            {'Open': c.open, 'High': c.high, 'Low': c.low, 'Close': c.close, 'Volume': c.volume, 'Datetime': c.timestamp}
            for c in ohlcv_list
        ])
        return df

    def evaluate(self, symbol: str, ohlcv_intra: List[OHLCV], ohlcv_1d: List[OHLCV]) -> Dict:
        if len(ohlcv_intra) < 30:
            return self._reject(symbol, "Insufficient Intraday Data")
            
        df = self.df_from_ohlcv(ohlcv_intra)
        
        # 1. Trading Session Filter (Exclude first 15 mins)
        try:
            latest_time = pd.to_datetime(df.iloc[-1]['Datetime'])
            if latest_time.hour == 9 and latest_time.minute < 30:
                return self._reject(symbol, "Pre-Market / Early Open Volatility (Wait until 9:30 AM)")
        except:
            pass

        df['Vol_MA'] = df['Volume'].rolling(20).mean()
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (df['Typical_Price'] * df['Volume']).cumsum() / (df['Volume'].cumsum() + 1e-10)
        
        latest = df.iloc[-1]
        
        # 2. Liquidity (Min average volume)
        if latest['Vol_MA'] < 50000:
            return self._reject(symbol, "Low Liquidity (Vol < 50k)")
            
        # 3. Volume Expansion (Current > 1.2x Average)
        if latest['Volume'] < (1.2 * latest['Vol_MA']):
            return self._reject(symbol, "No Volume Expansion")
            
        # 4. Basic Trend (Is price moving away from VWAP?)
        price = latest['Close']
        vwap = latest['VWAP']
        ema9 = latest['EMA9']
        
        is_trending_up = price > vwap and price > ema9
        is_trending_down = price < vwap and price < ema9
        
        if not (is_trending_up or is_trending_down):
            return self._reject(symbol, "Chop / Sideways (Price entangled with VWAP)")
            
        # 5. Relative Strength
        rs_data = self.rs_engine.get_rs_data(symbol)
        rs_score = rs_data.get("score", 50)
        
        if is_trending_up and rs_score < 45:
            return self._reject(symbol, "Relative Weakness (Opposes Up-Trend)")
        if is_trending_down and rs_score > 55:
            return self._reject(symbol, "Relative Strength (Opposes Down-Trend)")
            
        # Score calculation for caching (basic momentum proxy)
        score = 50.0 + (min(latest['Volume'] / (latest['Vol_MA'] + 1e-10), 5.0) * 10.0)
        score = min(100.0, score)
        
        direction = "BULLISH" if is_trending_up else "BEARISH"
        return self._pass(symbol, f"Volume Expansion + {direction} Trend Alignment", score)
