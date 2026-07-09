import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
from market.data_provider import OHLCV
from utils.logger import get_logger

# Import Stage-1 Cache
from strategy.discovery_engine import StateCache

# Import Core Validation Engines
from core.adx_engine import AdxEngine
from core.avwap_engine import AvwapEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.sector_rotation_engine import SectorRotationEngine

logger = get_logger(__name__)

class ValidationEngine:
    """
    STAGE-2: VALIDATION ENGINE
    Accepts ONLY Discovery-passed candidates.
    Evaluates hard technical metrics (ADX, AVWAP, Momentum, Structure, Sector).
    """
    
    def __init__(self):
        self.state_cache = StateCache.get_instance()
        self.adx_engine = AdxEngine()
        self.avwap_engine = AvwapEngine()
        self.momentum_engine = MomentumEngine()
        self.structure_engine = StructureEngine()
        self.sector_engine = SectorRotationEngine()
        
    def _wait(self, symbol: str, reason: str) -> Dict:
        self.state_cache.add_or_update(symbol, "VALIDATION_WAIT", 0.0, {"reason": reason})
        return {
            "symbol": symbol,
            "status": "VALIDATION_WAIT",
            "reason": reason,
            "stage": "Validation",
            "timestamp": datetime.now().isoformat()
        }
        
    def _reject(self, symbol: str, reason: str) -> Dict:
        self.state_cache.add_or_update(symbol, "VALIDATION_REJECT", 0.0, {"reason": reason})
        return {
            "symbol": symbol,
            "status": "VALIDATION_REJECT",
            "reason": reason,
            "stage": "Validation",
            "timestamp": datetime.now().isoformat()
        }
        
    def _pass(self, symbol: str, reason: str, score: float = 80.0) -> Dict:
        self.state_cache.add_or_update(symbol, "VALIDATION_PASS", score, {"reason": reason})
        return {
            "symbol": symbol,
            "status": "VALIDATION_PASS",
            "reason": reason,
            "stage": "Validation",
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

    def evaluate(self, symbol: str, ohlcv_intra: List[OHLCV], ohlcv_1d: List[OHLCV], direction: str = "BULLISH") -> Dict:
        """
        Evaluate the symbol through Stage-2.
        Direction is inferred from Stage-1.
        """
        # Ensure it passed Stage-1
        state = self.state_cache.get_state(symbol)
        if not state or state.get("stage") not in ["DISCOVERY", "VALIDATION_WAIT"]:
            pass 
                
        if len(ohlcv_intra) < 50:
            return self._wait(symbol, "Insufficient Intraday Data for Validation")
            
        df = self.df_from_ohlcv(ohlcv_intra)
        
        # 1. ADX Filter (Must be expanding / strong)
        adx_res = self.adx_engine.evaluate(df)
        if adx_res.adx < 20.0:
            return self._wait(symbol, f"ADX building ({adx_res.adx:.1f} < 20) - Waiting for expansion")
            
        if direction == "BULLISH" and adx_res.direction == "BEARISH":
            return self._reject(symbol, "ADX Direction Mismatch (Expected Bullish, Got Bearish)")
        if direction == "BEARISH" and adx_res.direction == "BULLISH":
            return self._reject(symbol, "ADX Direction Mismatch (Expected Bearish, Got Bullish)")

        # 2. Anchored VWAP
        avwap_res = self.avwap_engine.evaluate(df)
        if direction == "BULLISH" and avwap_res.relation == "BELOW":
            return self._reject(symbol, "Price below Anchored VWAP (Bearish trap)")
        if direction == "BEARISH" and avwap_res.relation == "ABOVE":
            return self._reject(symbol, "Price above Anchored VWAP (Bullish trap)")
            
        # 3. Momentum Confirmation (Using HTF daily data)
        df_1d = self.df_from_ohlcv(ohlcv_1d)
        
        try:
            # FIX: Only pass the df argument as per core method signature
            mom_res = self.momentum_engine.calculate(df=df_1d)
            if mom_res.score < 6: # NEUTRAL threshold is 6
                return self._wait(symbol, f"HTF Momentum weak (Score: {mom_res.score})")
        except Exception as e:
            return self._wait(symbol, "HTF Momentum Data Unavailable (Wait)")

        # 4. Market Structure
        try:
            struct_res = self.structure_engine.calculate(df=df_1d)
            if direction == "BULLISH" and struct_res.direction == "BEARISH":
                return self._reject(symbol, "HTF Structure is Bearish")
            if direction == "BEARISH" and struct_res.direction == "BULLISH":
                return self._reject(symbol, "HTF Structure is Bullish")
        except Exception as e:
            return self._wait(symbol, "HTF Structure Data Unavailable (Wait)")

        # 5. Sector Strength
        sector_name = self.sector_engine.get_stock_sector(symbol)
        if sector_name:
            sectors = self.sector_engine.get_sector_data()
            if sectors and sector_name in sectors:
                sec_score = sectors[sector_name].get("score", 50)
                if direction == "BULLISH" and sec_score < 40:
                    return self._wait(symbol, f"Weak Sector ({sector_name} Score: {sec_score})")
                if direction == "BEARISH" and sec_score > 60:
                    return self._wait(symbol, f"Strong Sector ({sector_name} Score: {sec_score})")

        return self._pass(symbol, f"Passed All 5 Validation Engines (ADX: {adx_res.adx:.1f})")
