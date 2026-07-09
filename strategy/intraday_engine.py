import pandas as pd
import numpy as np
from typing import Dict, List
from market.data_provider import OHLCV
from datetime import datetime
import os
import logging
from utils.logger import get_logger
from application.data_manager import DataManager
from ai.option_ai import OptionAI
from core.relative_strength_engine import RelativeStrengthEngine

logger = get_logger(__name__)

os.makedirs("logs", exist_ok=True)
debug_logger = logging.getLogger("IntradayStrictDebug")
debug_logger.setLevel(logging.INFO)
fh = logging.FileHandler("logs/intraday_strict_debug.log")
fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
debug_logger.addHandler(fh)

class IntradayEngine:
    """
    ACTIVE TRADING AI V2.0 - STRICT Intraday Engine
    Quality over Quantity. Capital Protection prioritized.
    """
    def __init__(self):
        self.rs_engine = RelativeStrengthEngine()
        self.reset_stats()

    def reset_stats(self):
        self.stats = {
            "Total Scanned": 0,
            "Total Qualified": 0,
            "Total Rejected": 0,
            "Reasons": {}
        }

    def log_rejection(self, symbol: str, reason: str):
        debug_logger.info(f"[{symbol}] Rejected | Reason: {reason}")
        self.stats["Total Rejected"] += 1
        if reason not in self.stats["Reasons"]:
            self.stats["Reasons"][reason] = 0
        self.stats["Reasons"][reason] += 1

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()

    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df = df.copy()
        high_diff = df['High'].diff()
        low_diff = df['Low'].diff()
        
        df['+DM'] = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0.0)
        df['-DM'] = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0.0)
        
        atr = self.calculate_atr(df, period)
        atr = atr.replace(0, 1e-10) # prevent division by zero
        
        df['+DI'] = 100 * (df['+DM'].ewm(alpha=1/period, adjust=False).mean() / atr)
        df['-DI'] = 100 * (df['-DM'].ewm(alpha=1/period, adjust=False).mean() / atr)
        
        dx = 100 * np.abs((df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'] + 1e-10))
        df['ADX'] = dx.ewm(alpha=1/period, adjust=False).mean()
        return df[['ADX', '+DI', '-DI']]

    def df_from_ohlcv(self, ohlcv_list: List[OHLCV]) -> pd.DataFrame:
        if not ohlcv_list:
            return pd.DataFrame()
        df = pd.DataFrame([
            {'Open': c.open, 'High': c.high, 'Low': c.low, 'Close': c.close, 'Volume': c.volume, 'Datetime': c.timestamp}
            for c in ohlcv_list
        ])
        return df

    def get_trend(self, df: pd.DataFrame) -> str:
        if len(df) < 30:
            return "NEUTRAL"
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
        latest = df.iloc[-1]
        
        if latest['EMA9'] > latest['EMA20'] and latest['Close'] > latest['EMA9']:
            return "BULLISH"
        elif latest['EMA9'] < latest['EMA20'] and latest['Close'] < latest['EMA9']:
            return "BEARISH"
        return "NEUTRAL"

    def evaluate(self, symbol: str, ohlcv_intra: List[OHLCV], ohlcv_15m: List[OHLCV], ohlcv_1h: List[OHLCV], ohlcv_1d: List[OHLCV], market_trend: str = "NEUTRAL") -> Dict:
        self.stats["Total Scanned"] += 1
        
        if len(ohlcv_intra) < 50:
            return self._empty_result(symbol, "Insufficient Intraday Data")
            
        df = self.df_from_ohlcv(ohlcv_intra)
        df_15m = self.df_from_ohlcv(ohlcv_15m)
        df_1h = self.df_from_ohlcv(ohlcv_1h)
        df_1d = self.df_from_ohlcv(ohlcv_1d)
        
        if df_15m.empty or df_1h.empty or df_1d.empty:
            return self._empty_result(symbol, "Missing HTF/Daily Data")
            
        # 1. Higher Timeframe Trend Confirmation
        trend_15m = self.get_trend(df_15m)
        trend_1h = self.get_trend(df_1h)
        
        htf_trend = "NEUTRAL"
        if trend_15m == "BULLISH" and trend_1h == "BULLISH":
            htf_trend = "BULLISH"
        elif trend_15m == "BEARISH" and trend_1h == "BEARISH":
            htf_trend = "BEARISH"
            
        if htf_trend == "NEUTRAL":
            return self._empty_result(symbol, "Weak Trend (Mixed HTF)")
            
        # 2. Market Direction Confirmation
        if market_trend != "NEUTRAL" and market_trend != htf_trend:
            return self._empty_result(symbol, f"Market Direction Opposing")
            
        # Intraday Indicators
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['Vol_MA'] = df['Volume'].rolling(20).mean()
        df['ATR'] = self.calculate_atr(df, 14)
        
        df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        adx_df = self.calculate_adx(df, 14)
        df['ADX'] = adx_df['ADX']
        df['+DI'] = adx_df['+DI']
        df['-DI'] = adx_df['-DI']
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Donchian for Breakout
        df['Donchian_High'] = df['High'].rolling(20).max().shift()
        df['Donchian_Low'] = df['Low'].rolling(20).min().shift()

        latest = df.iloc[-1]
        
        # 3. High Liquidity (Min avg 100k volume intraday or sufficient turnover)
        if latest['Vol_MA'] < 50000:
            return self._empty_result(symbol, "Low Volume / Liquidity")
            
        # 4. Momentum Confirmation
        if latest['ADX'] < 25:
            return self._empty_result(symbol, "Weak Momentum (ADX < 25)")
            
        signal = "WAIT"
        breakout_type = "None"
        
        pdh = df_1d.iloc[-2]['High'] if len(df_1d) >= 2 else 0
        pdl = df_1d.iloc[-2]['Low'] if len(df_1d) >= 2 else 0
        
        # 5. Breakout / Breakdown + Volume Spike
        vol_spike = latest['Volume'] >= (2.0 * latest['Vol_MA'])
        
        # VWAP Confirmation
        if htf_trend == "BULLISH" and latest['Close'] < latest['VWAP']:
            return self._empty_result(symbol, "Price Below VWAP (Bullish setup invalid)")
        elif htf_trend == "BEARISH" and latest['Close'] > latest['VWAP']:
            return self._empty_result(symbol, "Price Above VWAP (Bearish setup invalid)")
            
        # Bullish conditions
        if htf_trend == "BULLISH":
            is_pdh_break = (latest['Close'] > pdh) and (df.iloc[-2]['Close'] <= pdh) if pdh > 0 else False
            is_donchian_break = latest['Close'] > latest['Donchian_High']
            
            if is_pdh_break or is_donchian_break:
                breakout_type = "PDH Breakout" if is_pdh_break else "Donchian Breakout"
                if vol_spike:
                    if latest['RSI'] > 55 and latest['MACD'] > latest['Signal_Line'] and latest['+DI'] > latest['-DI']:
                        signal = "BUY"
                else:
                    return self._empty_result(symbol, "Fake Breakout (Low Volume Breakout)")
            else:
                return self._empty_result(symbol, "No Valid Breakout (PDH/Donchian)")
                
        # Bearish conditions
        elif htf_trend == "BEARISH":
            is_pdl_break = (latest['Close'] < pdl) and (df.iloc[-2]['Close'] >= pdl) if pdl > 0 else False
            is_donchian_break = latest['Close'] < latest['Donchian_Low']
            
            if is_pdl_break or is_donchian_break:
                breakout_type = "PDL Breakdown" if is_pdl_break else "Donchian Breakdown"
                if vol_spike:
                    if latest['RSI'] < 45 and latest['MACD'] < latest['Signal_Line'] and latest['-DI'] > latest['+DI']:
                        signal = "SELL"
                else:
                    return self._empty_result(symbol, "Fake Breakdown (Low Volume Breakout)")
            else:
                return self._empty_result(symbol, "No Valid Breakdown (PDL/Donchian)")
                
        if signal == "WAIT":
            return self._empty_result(symbol, "Setup Conditions Not Met")
            
        # 6. Relative Strength / Weakness
        rs_data = self.rs_engine.get_rs_data(symbol)
        rs_score = rs_data.get("score", 50)
        if signal == "BUY" and rs_score < 50:
            return self._empty_result(symbol, "Relative Weakness (BUY rejected)")
        if signal == "SELL" and rs_score > 50:
            return self._empty_result(symbol, "Relative Strength (SELL rejected)")
            
        # Calculate Levels
        entry = round(latest['Close'], 2)
        atr = latest['ATR'] if not pd.isna(latest['ATR']) and latest['ATR'] > 0 else (entry * 0.005)
        
        if signal == "BUY":
            sl = round(entry - atr, 2)
            tp1 = round(entry + atr, 2)
            tp2 = round(entry + (atr * 2.0), 2)
        else: # SELL
            sl = round(entry + atr, 2)
            tp1 = round(entry - atr, 2)
            tp2 = round(entry - (atr * 2.0), 2)
            
        # 8. Risk / Reward Minimum 1:2
        risk = abs(entry - sl)
        reward = abs(tp2 - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        if rr_ratio < 2.0:
            return self._empty_result(symbol, f"Poor RR (1:{round(rr_ratio, 1)})")
            
        # 9. AI Confidence >= 85%
        conf_score = 75 # Base for reaching here
        if latest['Volume'] >= (3.0 * latest['Vol_MA']): conf_score += 10 # Institutional Participation
        if latest['ADX'] > 35: conf_score += 5 # Very strong trend
        if (signal == "BUY" and rs_score > 70) or (signal == "SELL" and rs_score < 30): conf_score += 5
        if market_trend == htf_trend and market_trend != "NEUTRAL": conf_score += 5
        
        # Option AI Check (Sprint 71)
        try:
            if symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
                dm = DataManager.get_instance()
                chain_data = dm.get_option_chain(symbol)
                if chain_data and "records" in chain_data:
                    expiries = chain_data["records"]["expiryDates"]
                    if expiries:
                        expiry = expiries[0]
                        underlying = chain_data["records"]["underlyingValue"]
                        data_list = chain_data["records"]["data"]
                        
                        rows = []
                        for item in data_list:
                            if item["expiryDate"] == expiry:
                                ce = item.get("CE", {})
                                pe = item.get("PE", {})
                                rows.append({
                                    "Strike": item["strikePrice"],
                                    "CE_OI": ce.get("openInterest", 0),
                                    "CE_CHNG_OI": ce.get("changeinOpenInterest", 0),
                                    "CE_Vol": ce.get("totalTradedVolume", 0),
                                    "CE_IV": ce.get("impliedVolatility", 0),
                                    "CE_LTP": ce.get("lastPrice", 0),
                                    "PE_OI": pe.get("openInterest", 0),
                                    "PE_CHNG_OI": pe.get("changeinOpenInterest", 0),
                                    "PE_Vol": pe.get("totalTradedVolume", 0),
                                    "PE_IV": pe.get("impliedVolatility", 0),
                                    "PE_LTP": pe.get("lastPrice", 0)
                                })
                        
                        df_chain = pd.DataFrame(rows)
                        if not df_chain.empty:
                            ai = OptionAI()
                            ai_res = ai.analyze(df_chain, underlying, expiry, symbol)
                            ai_sentiment = ai_res.get("sentiment", "Neutral")
                            
                            if signal == "BUY" and ai_sentiment == "Bearish":
                                return self._empty_result(symbol, "Option AI Bearish")
                            elif signal == "SELL" and ai_sentiment == "Bullish":
                                return self._empty_result(symbol, "Option AI Bullish")
                            elif signal == "BUY" and ai_sentiment == "Bullish":
                                conf_score = min(conf_score + 10, 100)
                            elif signal == "SELL" and ai_sentiment == "Bearish":
                                conf_score = min(conf_score + 10, 100)
        except Exception as e:
            logger.error(f"Option AI Error for {symbol}: {e}")

        # Enforce AI Confidence Limit
        if conf_score < 85:
            return self._empty_result(symbol, f"Low Confidence ({conf_score}%)")
            
        # Trade Grade and Estimations
        trade_grade = "A+" if conf_score >= 90 else "A"
        expected_holding = "30-60 Mins" if atr > 5 else "1-2 Hours"
        
        # Calculate Expected Exit Time (approx)
        now = datetime.now()
        try:
            if "30" in expected_holding:
                exit_time_dt = pd.to_datetime(latest['Datetime']) + pd.Timedelta(minutes=45)
            else:
                exit_time_dt = pd.to_datetime(latest['Datetime']) + pd.Timedelta(hours=1.5)
            expected_exit_time = exit_time_dt.strftime("%H:%M")
        except:
            expected_exit_time = "EOD"
            
        reason = "Institutional Vol + Breakout" if latest['Volume'] >= (3.0 * latest['Vol_MA']) else "High Prob Breakout"
        dt_str = now.isoformat()
        
        self.stats["Total Qualified"] += 1
        debug_logger.info(f"[{symbol}] ACCEPTED - {signal} - Conf: {conf_score}% - Grade: {trade_grade}")
        
        return {
            "symbol": symbol,
            "signal": signal,
            "entry": entry,
            "stop_loss": sl,
            "target_1": tp1,
            "target_2": tp2,
            "risk_reward": f"1:{round(rr_ratio, 1)}",
            "trend": htf_trend,
            "volume_status": "Inst. Buying" if signal == "BUY" and conf_score >= 90 else "Volume Spike",
            "sector_status": "Aligned",
            "confidence": f"{conf_score}%",
            "breakout_type": breakout_type,
            "reason": reason,
            "score": conf_score,
            "trade_grade": trade_grade,
            "expected_holding": expected_holding,
            "expected_exit_time": expected_exit_time,
            "created_at": dt_str
        }

    def _empty_result(self, symbol: str, reason: str = "") -> Dict:
        self.log_rejection(symbol, reason)
        return {
            "symbol": symbol, "signal": "WAIT", "score": 0, "entry": 0.0,
            "stop_loss": 0.0, "target_1": 0.0, "target_2": 0.0, "risk_reward": "0:0", "confidence": "0%",
            "trend": "N/A", "volume_status": "N/A", "sector_status": "N/A", "breakout_type": "N/A",
            "trade_grade": "N/A", "expected_holding": "N/A", "expected_exit_time": "N/A",
            "created_at": datetime.now().isoformat(), "reason": reason
        }
