import os
import time
import logging
import threading
from PySide6.QtCore import QObject, Signal

from providers.yahoo_provider import YahooProvider
from providers.nse_provider import NSEProvider
from providers.cache_manager import CacheManager
from utils.paths import get_logs_dir

log_dir = get_logs_dir()
log_file = log_dir / "data_manager.log"

logger = logging.getLogger("DataManager")
logger.setLevel(logging.INFO)
if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

class DataEvents(QObject):
    stock_data_updated = Signal(str, object)
    option_chain_updated = Signal(str, object)
    market_breadth_updated = Signal(object)

class DataManager:
    """
    Centralized Unified Data Manager.
    All modules must request data from here.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if DataManager._instance is not None:
            raise Exception("This class is a singleton!")
            
        logger.info("Initializing Unified Data Manager...")
        self.yahoo = YahooProvider()
        self.nse = NSEProvider()
        self.cache = CacheManager()
        self.events = DataEvents()
        
        self.active_symbols = set()
        self.active_indices = set()
        
        self._start_background_threads()
        
    def _start_background_threads(self):
        # Stock Data Auto Refresh (30s)
        def refresh_stocks():
            while True:
                time.sleep(30)
                for sym in list(self.active_symbols):
                    self.get_stock_data(sym)
                    
        # Option Chain Auto Refresh (30s)
        def refresh_options():
            while True:
                time.sleep(30)
                for idx in list(self.active_indices):
                    self.get_option_chain(idx)
                    
        threading.Thread(target=refresh_stocks, daemon=True).start()
        threading.Thread(target=refresh_options, daemon=True).start()

    # --- PUBLIC API ---

    def get_stock_data(self, symbol, period="1mo", interval="1d"):
        self.active_symbols.add(symbol)
        
        start_time = time.time()
        logger.info(f"DataManager: Fetching Stock Data for {symbol} (Yahoo)")
        
        data = self.yahoo.fetch_stock_data(symbol, period, interval)
        resp_time = time.time() - start_time
        
        cache_key = f"stock_{symbol}_{period}_{interval}"
        if data is not None and not data.empty:
            logger.info(f"DataManager: Yahoo SUCCESS | {symbol} | {resp_time:.2f}s")
            self.cache.set(cache_key, data)
            self.events.stock_data_updated.emit(symbol, data)
            return data
            
        logger.error(f"DataManager: Yahoo FAILED | {symbol} | Returning Cached Data.")
        return self.cache.get(cache_key)

    def get_intraday_data(self, symbol, timeframe="5m"):
        return self.get_stock_data(symbol, period="5d", interval=timeframe)

    def get_historical_data(self, symbol, period="1mo", interval="1d"):
        return self.get_stock_data(symbol, period, interval)

    def get_option_chain(self, index="NIFTY"):
        self.active_indices.add(index)
        
        start_time = time.time()
        logger.info(f"DataManager: Fetching Option Chain for {index} (NSE)")
        
        data = self.nse.fetch_option_chain(index)
        resp_time = time.time() - start_time
        
        cache_key = f"oc_{index}"
        if data is not None:
            logger.info(f"DataManager: NSE SUCCESS | {index} | {resp_time:.2f}s")
            self.cache.set(cache_key, data)
            self.events.option_chain_updated.emit(index, data)
            return data
            
        logger.error(f"DataManager: NSE FAILED | {index} | Returning Cached Data.")
        return self.cache.get(cache_key)
        
    def get_market_status(self):
        # Stub for market status
        return {"status": "Open"}

    def get_market_breadth(self):
        # Stub for breadth
        return {"advances": 0, "declines": 0}
