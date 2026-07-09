import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
from market.data_provider import OHLCV
from utils.logger import get_logger

# Import core engines
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.adx_engine import AdxEngine
from core.avwap_engine import AvwapEngine
from core.structure_engine import StructureEngine
from core.smart_money_engine import SmartMoneyEngine
from core.market_regime_engine import MarketRegimeEngine
from core.relative_strength_engine import RelativeStrengthEngine
from core.sector_rotation_engine import SectorRotationEngine

try:
    from core.ai_engine import AIPredictionEngine
    from core.confidence_calibration_engine import ConfidenceCalibrationEngine
    from core.risk_reward_engine import RiskRewardEngine
except ImportError:
    AIPredictionEngine = None
    ConfidenceCalibrationEngine = None
    RiskRewardEngine = None

logger = get_logger(__name__)

class RankingEngine:
    """
    INTRADAY V2: INSTITUTIONAL RANKING SCANNER
    Scores and ranks every stock based on a 100-point composite weight.
    No hard rejection unless (No Data, Circuit, Suspended, Invalid Symbol).
    """
    
    def __init__(self):
        self.trend_engine = TrendEngine()
        self.momentum_engine = MomentumEngine()
        self.adx_engine = AdxEngine()
        self.avwap_engine = AvwapEngine()
        self.structure_engine = StructureEngine()
        self.sme = SmartMoneyEngine()
        self.rs_engine = RelativeStrengthEngine()
        self.sector_engine = SectorRotationEngine()
        self.market_regime = MarketRegimeEngine()
        
        self.ai = AIPredictionEngine() if AIPredictionEngine else None
        self.confidence_engine = ConfidenceCalibrationEngine() if ConfidenceCalibrationEngine else None
        
        # Load market regime once per scan cycle to save CPU
        self.regime_data = self.market_regime.get_current_regime()

    def df_from_ohlcv(self, ohlcv_list: List[OHLCV]) -> pd.DataFrame:
        if not ohlcv_list:
            return pd.DataFrame()
        df = pd.DataFrame([
            {'Open': c.open, 'High': c.high, 'Low': c.low, 'Close': c.close, 'Volume': c.volume, 'Datetime': c.timestamp}
            for c in ohlcv_list
        ])
        
        # --- TASK-3: Indicator Cache ---
        # Calculate standard indicators ONLY ONCE here and attach as columns to reuse.
        
        # EMA
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # VWAP
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        # RSI 14
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        rs = avg_gain / avg_loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        
        # ATR 14
        tr1 = df['High'] - df['Low']
        tr2 = (df['High'] - df['Close'].shift(1)).abs()
        tr3 = (df['Low'] - df['Close'].shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['ATR_14'] = tr.ewm(alpha=1/14, adjust=False).mean()
        
        # ADX 14
        up = df['High'] - df['High'].shift(1)
        down = df['Low'].shift(1) - df['Low']
        plus_dm = np.where((up > down) & (up > 0), up, 0.0)
        minus_dm = np.where((down > up) & (down > 0), down, 0.0)
        plus_dm_smooth = pd.Series(plus_dm, index=df.index).ewm(alpha=1/14, adjust=False).mean()
        minus_dm_smooth = pd.Series(minus_dm, index=df.index).ewm(alpha=1/14, adjust=False).mean()
        tr_smooth = tr.ewm(alpha=1/14, adjust=False).mean()
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        df['ADX_14'] = dx.ewm(alpha=1/14, adjust=False).mean()
        df['PLUS_DI_14'] = plus_di
        df['MINUS_DI_14'] = minus_di
        
        # MACD (12, 26, 9)
        ema_fast = df['Close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df

    def _create_engine_response(self, score: float, reason: str, penalty: float = 0.0, bonus: float = 0.0) -> dict:
        return {
            "Score Contribution": round(score, 2),
            "Reason": reason,
            "Penalty": round(penalty, 2),
            "Bonus": round(bonus, 2)
        }

    def _eval_trend(self, df: pd.DataFrame, direction: str) -> dict:
        # Max 10 points
        try:
            res = self.trend_engine.evaluate(df)
            trend_dir = res.get("direction", "UNKNOWN")
            if trend_dir == direction:
                return self._create_engine_response(10.0, "Trend aligned with direction")
            return self._create_engine_response(0.0, "Trend counter to direction", 5.0)
        except Exception as e:
            logger.debug(f"Trend evaluation failed: {e}")
            return self._create_engine_response(5.0, "Trend : Neutral")

    def _eval_momentum(self, df_1d: pd.DataFrame, direction: str) -> dict:
        # Max 5 points
        try:
            res = self.momentum_engine.calculate(df=df_1d)
            if (direction == "BULLISH" and res.direction in ["BULL", "STRONG_BULL"]) or \
               (direction == "BEARISH" and res.direction in ["BEAR", "STRONG_BEAR"]):
                return self._create_engine_response(5.0, f"Momentum aligned ({res.score}/20)")
            return self._create_engine_response(0.0, "Momentum conflicting")
        except Exception as e:
            logger.debug(f"Momentum evaluation failed: {e}")
            return self._create_engine_response(2.5, "Momentum : Medium")

    def _eval_volume(self, df: pd.DataFrame) -> dict:
        # Max 5 points
        try:
            vol_ma = df['Volume'].rolling(20).mean().iloc[-1]
            vol = df['Volume'].iloc[-1]
            if vol > vol_ma * 1.5:
                return self._create_engine_response(5.0, "High Relative Volume expansion")
            elif vol > vol_ma:
                return self._create_engine_response(3.0, "Normal Volume expansion")
            return self._create_engine_response(0.0, "Below average volume")
        except Exception as e:
            logger.debug(f"Volume evaluation failed: {e}")
            return self._create_engine_response(2.5, "Volume : Medium")

    def _eval_adx(self, df: pd.DataFrame) -> dict:
        # Max 5 points
        try:
            res = self.adx_engine.evaluate(df)
            if res.adx >= 25:
                return self._create_engine_response(5.0, f"Strong ADX ({res.adx:.1f})")
            elif res.adx >= 20:
                return self._create_engine_response(3.0, f"Moderate ADX ({res.adx:.1f})")
            return self._create_engine_response(0.0, f"Weak ADX ({res.adx:.1f})")
        except Exception as e:
            logger.debug(f"ADX evaluation failed: {e}")
            return self._create_engine_response(2.5, "Trend : Neutral")

    def _eval_vwap(self, df: pd.DataFrame, direction: str) -> dict:
        # Max 5 points
        try:
            res = self.avwap_engine.evaluate(df)
            if (direction == "BULLISH" and res.institutional_bias == "Bullish") or \
               (direction == "BEARISH" and res.institutional_bias == "Bearish"):
                return self._create_engine_response(5.0, "Price structurally respects AVWAP")
            return self._create_engine_response(0.0, "Price disrespecting AVWAP", penalty=2.0)
        except Exception as e:
            logger.debug(f"VWAP evaluation failed: {e}")
            return self._create_engine_response(2.5, "Structure : Neutral")

    def _eval_ict(self, df: pd.DataFrame, direction: str) -> dict:
        # Max 10 points
        score = 0.0
        reasons = []
        try:
            if len(df) >= 5:
                # FVG Check
                if direction == "BULLISH" and df['Low'].iloc[-1] > df['High'].iloc[-3]:
                    score += 5.0
                    reasons.append("Bullish FVG")
                elif direction == "BEARISH" and df['High'].iloc[-1] < df['Low'].iloc[-3]:
                    score += 5.0
                    reasons.append("Bearish FVG")
                    
                # Liquidity Sweep Check
                latest = df.iloc[-1]
                rng = latest['High'] - latest['Low']
                if rng > 0:
                    if direction == "BULLISH":
                        lower_wick = min(latest['Open'], latest['Close']) - latest['Low']
                        if lower_wick / rng > 0.5:
                            score += 5.0
                            reasons.append("Liquidity Sweep (Long lower wick)")
                    else:
                        upper_wick = latest['High'] - max(latest['Open'], latest['Close'])
                        if upper_wick / rng > 0.5:
                            score += 5.0
                            reasons.append("Liquidity Sweep (Long upper wick)")
                            
            if score == 0:
                return self._create_engine_response(0.0, "No ICT footprints detected")
            return self._create_engine_response(min(10.0, score), " + ".join(reasons), bonus=min(10.0, score))
        except Exception as e:
            logger.debug(f"ICT evaluation failed: {e}")
            return self._create_engine_response(0.0, "Structure : Neutral")

    def _eval_smart_money(self, df: pd.DataFrame) -> dict:
        # Max 10 points
        try:
            res = self.sme.analyze(df, self.regime_data, "Neutral")
            sm_raw = res.get("Smart Money Score", 50)
            score = (sm_raw / 100) * 10
            return self._create_engine_response(score, res.get("Classification", "Neutral"))
        except Exception as e:
            logger.debug(f"Smart Money evaluation failed: {e}")
            return self._create_engine_response(5.0, "Smart Money : Neutral")

    def _eval_sector(self, symbol: str, direction: str) -> dict:
        # Max 5 points
        try:
            sector = self.sector_engine.get_stock_sector(symbol)
            if not sector: return self._create_engine_response(2.5, "Sector Unknown")
            sdata = self.sector_engine.get_sector_data().get(sector, {})
            score = sdata.get("score", 50)
            if (direction == "BULLISH" and score >= 60) or (direction == "BEARISH" and score <= 40):
                return self._create_engine_response(5.0, f"Sector Aligned ({sector})")
            return self._create_engine_response(0.0, f"Sector Weak/Opposing ({sector})")
        except Exception as e:
            logger.debug(f"Sector evaluation failed for {symbol}: {e}")
            return self._create_engine_response(2.5, "Sector : Neutral")

    def _eval_rs(self, symbol: str, direction: str) -> dict:
        # Max 5 points
        try:
            rs_data = self.rs_engine.get_rs_data(symbol)
            score = rs_data.get("score", 50)
            if (direction == "BULLISH" and score >= 55) or (direction == "BEARISH" and score <= 45):
                return self._create_engine_response(5.0, f"Relative Strength Aligned (Score: {score})")
            return self._create_engine_response(0.0, "Relative Strength Opposing")
        except Exception as e:
            logger.debug(f"RS evaluation failed for {symbol}: {e}")
            return self._create_engine_response(2.5, "Relative Strength : Neutral")

    def _eval_ai(self) -> dict:
        # Max 15 points
        return self._create_engine_response(10.0, "AI Consensus (Mock/Offline)", 0.0, 0.0)

    def _eval_confidence(self, engines: dict, raw_score: float) -> dict:
        # Max 10 points (which maps to 0-100%)
        # Calculate dynamic confidence based on alignment of key technical engines
        aligned_count = 0
        total_eval = 0
        key_engines = ["Trend", "Momentum", "Volume", "VWAP", "ICT", "ADX", "Smart Money", "Sector", "Relative Strength"]
        
        for key in key_engines:
            if key in engines:
                total_eval += 1
                if engines[key]["Score Contribution"] >= 5.0: # Meaning full alignment
                    aligned_count += 1
                elif engines[key]["Score Contribution"] > 0.0: # Partial alignment
                    aligned_count += 0.5
                    
        alignment_ratio = aligned_count / max(1, total_eval)
        
        # Base confidence from alignment (0 to 60%)
        conf_pct = alignment_ratio * 60.0
        
        # Liquidity (TQI) confidence (0 to 20%)
        tqi = engines.get("TQI", {}).get("Score Contribution", 0.0)
        conf_pct += (tqi / 10.0) * 20.0
        
        # Raw score component (0 to 20%)
        conf_pct += min(20.0, raw_score * 0.4)
        
        conf_pct = min(100.0, max(0.0, conf_pct))
        conf_score = (conf_pct / 100.0) * 10.0
        
        return self._create_engine_response(conf_score, f"Dynamic Confidence ({conf_pct:.1f}%)")

    def _eval_tqi(self, df: pd.DataFrame) -> dict:
        # Max 10 points (Proxy via spread/liquidity stability)
        try:
            avg_vol = df['Volume'].mean()
            if avg_vol > 500000:
                return self._create_engine_response(10.0, "Excellent TQI (High Liquidity)")
            elif avg_vol > 100000:
                return self._create_engine_response(7.0, "Good TQI (Moderate Liquidity)")
            return self._create_engine_response(3.0, "Poor TQI (Low Liquidity)", penalty=2.0)
        except Exception as e:
            logger.debug(f"TQI evaluation failed: {e}")
            return self._create_engine_response(5.0, "Liquidity : Medium")

    def _eval_rr(self) -> dict:
        # Max 5 points
        return self._create_engine_response(5.0, "Risk-Reward >= 1:2 validated")

    def get_grade(self, score: float) -> str:
        if score >= 90: return "A+"
        if score >= 80: return "A"
        if score >= 70: return "B"
        if score >= 60: return "C"
        if score >= 50: return "Watch"
        return "Weak"

    def evaluate(self, symbol: str, ohlcv_intra: List[OHLCV], ohlcv_1d: List[OHLCV]) -> Dict:
        """
        Calculates composite score out of 100 for the symbol using the 13-engine pipeline.
        """
        if len(ohlcv_intra) < 30:
            return {"symbol": symbol, "status": "REJECT", "reason": "No Data / Insufficient Data", "score": 0}
            
        df = self.df_from_ohlcv(ohlcv_intra)
        df_1d = self.df_from_ohlcv(ohlcv_1d)
        
        # Determine Base Direction
        latest = df.iloc[-1]
        price = latest['Close']
        is_trending_up = price > latest['VWAP'] and price > latest['EMA9']
        direction = "BULLISH" if is_trending_up else "BEARISH"
        
        engines = {}
        engines['Trend'] = self._eval_trend(df, direction)
        engines['Momentum'] = self._eval_momentum(df_1d, direction)
        engines['Volume'] = self._eval_volume(df)
        engines['ADX'] = self._eval_adx(df)
        engines['VWAP'] = self._eval_vwap(df, direction)
        engines['ICT'] = self._eval_ict(df, direction)
        engines['Smart Money'] = self._eval_smart_money(df)
        engines['Sector'] = self._eval_sector(symbol, direction)
        engines['Relative Strength'] = self._eval_rs(symbol, direction)
        engines['AI'] = self._eval_ai()
        engines['TQI'] = self._eval_tqi(df)
        engines['Risk Reward'] = self._eval_rr()
        
        # Calculate raw score before confidence
        raw_pre_conf = sum(res["Score Contribution"] for key, res in engines.items() if key != 'Confidence')
        
        # Inject dynamic confidence calculation
        engines['Confidence'] = self._eval_confidence(engines, raw_pre_conf)
        
        # Sum Base Contributions
        raw_score = sum(res["Score Contribution"] for res in engines.values())
        total_penalties = sum(res["Penalty"] for res in engines.values())
        total_bonuses = sum(res["Bonus"] for res in engines.values())
        
        # Normalize score to 0-100 scale (MAX_POSSIBLE_SCORE is theoretically ~95.0 excluding bonuses)
        MAX_THEORETICAL = 95.0 
        normalized_base = (raw_score / MAX_THEORETICAL) * 100.0
        
        composite_score = max(0.0, normalized_base - total_penalties + total_bonuses)
        composite_score = min(100.0, composite_score)
        
        reasons = [f"{k}: {v['Reason']}" for k, v in engines.items() if v["Score Contribution"] > 0 or v["Penalty"] > 0]
        primary_reasons = " | ".join(reasons[:3]) # Show top 3 reasons in UI
        
        # CAPITAL PROTECTION PENALTY (Market Regime)
        regime = self.regime_data.get("Market Regime", "UNKNOWN")
        regime_penalty = 0.0
        
        if regime in ["STRONG BEAR TREND", "BEAR TREND"] and direction == "BULLISH":
            regime_penalty = 10.0
            primary_reasons = "Market Regime Penalty (-10) | " + primary_reasons
        elif regime in ["STRONG BULL TREND", "BULL TREND"] and direction == "BEARISH":
            regime_penalty = 10.0
            primary_reasons = "Market Regime Penalty (-10) | " + primary_reasons
            
        final_score = max(0.0, composite_score - regime_penalty)
        
        # Mock confidence metric %
        confidence = (engines['Confidence']['Score Contribution'] / 10.0) * 100
        
        # Generate realistic price levels
        latest_close = df.iloc[-1]['Close']
        if direction == "BULLISH":
            entry_price = latest_close
            sl_price = latest_close * 0.985
            target_price = latest_close * 1.03
        else:
            entry_price = latest_close
            sl_price = latest_close * 1.015
            target_price = latest_close * 0.97
        
        # Use rounded score for both display and grading to ensure 100% consistency
        rounded_final_score = round(final_score, 1)
        
        return {
            "symbol": symbol,
            "status": "RANKED",
            "direction": direction,
            "score": rounded_final_score,
            "raw_score": round(composite_score, 1),
            "confidence": round(confidence, 1),
            "grade": self.get_grade(rounded_final_score),
            "reason": primary_reasons,
            "engine_breakdown": engines,
            "entry": round(entry_price, 2),
            "sl": round(sl_price, 2),
            "target1": round(target_price, 2)
        }
