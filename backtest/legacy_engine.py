import os
import csv
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
import yfinance as yf

from utils.logger import get_logger
from market.data_provider import MarketDataProvider, OHLCV, MarketStatus
from scanner.scanner_engine import ScannerEngine
from data.stocks import Stock
from core.models import ScanResult

# Import SwingScannerService and IntradayScannerService to inherit exactly its engines and Master Pipeline
from application.swing_scanner_service import SwingScannerService, safe_float, safe_int
from application.intraday_scanner_service import IntradayScannerService

logger = get_logger(__name__)

class BacktestDataProvider(MarketDataProvider):
    """
    Simulates real-time market data progression by dispensing historical
    OHLCV data one day at a time. Caches NIFTY and Sectors as well.
    """
    def __init__(self, start_date: str, end_date: str, interval: str = "1d"):
        self.interval = interval
        self.start_date = start_date
        self.end_date = end_date
        self.cache = {}
        self.current_date_index = 0
        self.main_symbol = None
        self._connected = True

    def set_main_symbol(self, symbol: str):
        self.main_symbol = symbol
        self._fetch_symbol(symbol)
        self.current_date_index = 0

    def _fetch_symbol(self, sym: str):
        if sym not in self.cache:
            ticker = yf.Ticker(sym)
            df = ticker.history(start=self.start_date, end=self.end_date, interval=self.interval)
            if not df.empty and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            self.cache[sym] = df

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def get_last_price(self, symbol: str) -> float:
        if self.main_symbol and self.main_symbol in self.cache:
            df = self.cache[self.main_symbol]
            if self.current_date_index < len(df):
                return float(df['Close'].iloc[self.current_date_index])
        return 0.0

    def get_ohlcv(self, symbol: str, interval: str = "1d", period: str = "3mo") -> List[OHLCV]:
        if symbol not in self.cache:
            self._fetch_symbol(symbol)
            
        df = self.cache[symbol]
        if df.empty:
            return []
            
        if self.main_symbol not in self.cache or self.cache[self.main_symbol].empty:
            return []
            
        main_df = self.cache[self.main_symbol]
        if self.current_date_index >= len(main_df):
            return []
            
        current_date = main_df.index[self.current_date_index]
        df_slice = df[df.index <= current_date]
        
        ohlcv_list = []
        for index, row in df_slice.iterrows():
            ohlcv_list.append(
                OHLCV(
                    timestamp=index,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
            )
        return ohlcv_list

    def get_volume(self, symbol: str) -> int:
        if self.main_symbol and self.main_symbol in self.cache:
            df = self.cache[self.main_symbol]
            if self.current_date_index < len(df):
                return int(df['Volume'].iloc[self.current_date_index])
        return 0

    def get_market_status(self) -> MarketStatus:
        return MarketStatus(is_open=False, status_message="BACKTEST MODE")

class BacktestEngine:
    """
    Executes the Unified Ranking Engine over historical data.
    """
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def run_backtest(self, symbol_list: List[str], start_date: str, end_date: str, timeframe: str = "1d", hold_days: int = 10, mode: str = "SWING"):
        start_time = time.time()
        
        print("\n======================================================================")
        print(f"Backtest Synchronization Started")
        print(f"Symbols: {len(symbol_list)}")
        print(f"Period:  {start_date} to {end_date}")
        print("======================================================================")
        print("Initializing Unified Ranking Engine...")
        
        from strategy.ranking_engine import RankingEngine
        ranking_engine = RankingEngine()
        
        # We need a dedicated BacktestDataProvider capable of caching multiple symbols (e.g. Sectors, Nifty)
        data_provider = BacktestDataProvider(start_date, end_date, timeframe)
        data_provider._fetch_symbol("^NSEI")
        for sym in ["BANKNIFTY.NS", "NIFTYIT.NS", "NIFTYAUTO.NS", "NIFTYFMCG.NS", "NIFTYMETAL.NS", "NIFTYPHARMA.NS"]:
            data_provider._fetch_symbol(sym)
        
        all_signals = []
        
        for idx, symbol in enumerate(symbol_list):
            try:
                data_provider.set_main_symbol(symbol)
                main_df = data_provider.cache.get(symbol)
                if main_df is None or main_df.empty:
                    continue
            except Exception as e:
                logger.error(f"Failed to initialize backtest data for {symbol}: {e}")
                continue
                
            min_lookback = 50
            trading_days = len(main_df)
            
            if trading_days <= min_lookback:
                logger.error(f"Insufficient data for {symbol}.")
                continue
                
            for i in range(min_lookback, trading_days):
                data_provider.current_date_index = i
                current_date = main_df.index[i]
                
                # Fetch rolling slices up to current date (simulating live feed)
                df_slice_1d = data_provider.get_ohlcv(symbol, "1d")
                df_slice_intra = data_provider.get_ohlcv(symbol, timeframe)
                
                if not df_slice_1d or not df_slice_intra:
                    continue
                    
                res = ranking_engine.evaluate(symbol, df_slice_intra, df_slice_1d)
                
                if res["status"] == "RANKED":
                    final_decision = res["direction"]
                    score = res["score"]
                    
                    if score >= 70.0:  # Good+ Grade gets executed in Backtest
                        # Basic entry logic simulation since we bypassed PrecisionEntryEngine
                        price = float(df_slice_intra[-1].close)
                        entry = price
                        sl = price * 0.98
                        t1 = price * 1.02
                        t2 = price * 1.05
                        
                        all_signals.append({
                            "Date": current_date,
                            "Symbol": symbol,
                            "Signal": "BUY" if final_decision == "BULLISH" else "SELL",
                            "Entry Price": entry,
                            "Stop Loss": sl,
                            "Target 1": t1,
                            "Target 2": t2,
                            "Trend Score": res["engine_breakdown"].get("Trend", {}).get("Score Contribution", 0),
                            "Momentum Score": res["engine_breakdown"].get("Momentum", {}).get("Score Contribution", 0),
                            "Structure Score": res["engine_breakdown"].get("VWAP", {}).get("Score Contribution", 0),
                            "Raw Score": res["raw_score"],
                            "Adjusted Score": score,
                            "Confidence": res["confidence"]
                        })
                    
            # Print Progress
            if not hasattr(self, '_bt_start_time'):
                self._bt_start_time = time.time()
                
            progress = int(((idx + 1) / len(symbol_list)) * 100)
            elapsed = time.time() - self._bt_start_time
            speed = (idx + 1) / elapsed if elapsed > 0 else 0
            eta = int((len(symbol_list) - (idx + 1)) / speed) if speed > 0 else 0
            
            sys.stdout.write(f"\rProgress: {progress}% | ETA: {eta}s | {idx+1}/{len(symbol_list)}")
            sys.stdout.flush()
            
        sys.stdout.write("\nCompleted Pipeline Execution\n")
        exec_time = time.time() - start_time
        print(f"Pipeline executed in {exec_time:.2f} seconds.")
        
        return all_signals
