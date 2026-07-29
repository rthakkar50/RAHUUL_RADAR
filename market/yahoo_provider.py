"""
Yahoo Finance data provider implementation for RAHUUL_RADAR.
Implements robust, production-ready market data fetching using the yfinance library.
"""
import time
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import threading
import requests

from market.data_provider import MarketDataProvider, OHLCV, MarketStatus
from utils.logger import get_logger

logger = get_logger(__name__)

class YahooFinanceProvider(MarketDataProvider):
    """
    Concrete implementation of MarketDataProvider for Yahoo Finance.
    Handles downloading, normalizing, and standardizing NSE market data with retry mechanics.
    """

    def __init__(self) -> None:
        """
        Initializes the Yahoo Finance provider architecture.
        """
        self._is_connected = False
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._cache_ttl = 900 # 15 minutes TTL for memory
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Disk Cache Initialization
        import os
        import pickle
        self._disk_cache_dir = os.path.expanduser("~/.cache/rahuul_radar")
        os.makedirs(self._disk_cache_dir, exist_ok=True)
        self._disk_cache_file = os.path.join(self._disk_cache_dir, "yahoo_cache.pkl")
        
        # Load from disk if exists
        try:
            if os.path.exists(self._disk_cache_file):
                # Only load if modified in the last 15 minutes
                if time.time() - os.path.getmtime(self._disk_cache_file) < self._cache_ttl:
                    with open(self._disk_cache_file, "rb") as f:
                        self._cache = pickle.load(f)
                        logger.info(f"Loaded {len(self._cache)} items from disk cache.")
                else:
                    logger.info("Disk cache expired. Starting fresh.")
        except Exception as e:
            logger.warning(f"Failed to load disk cache: {e}")
            self._cache = {}
            
        logger.info("Initialized YahooFinanceProvider (Live Mode).")
        
    def _save_disk_cache(self):
        """Saves current memory cache to disk asynchronously"""
        def save():
            try:
                with self._cache_lock:
                    cache_copy = self._cache.copy()
                with open(self._disk_cache_file, "wb") as f:
                    import pickle
                    pickle.dump(cache_copy, f)
            except Exception as e:
                logger.error(f"Failed to save disk cache: {e}")
        threading.Thread(target=save, daemon=True).start()

    def connect(self) -> bool:
        """
        Establishes a connection state for the Yahoo Finance API.
        
        Returns:
            bool: True if connection state is active.
        """
        logger.info("Connecting to Yahoo Finance API...")
        self._is_connected = True
        logger.info("Successfully connected to Yahoo Finance.")
        return True

    def disconnect(self) -> bool:
        """
        Closes the connection state to the Yahoo Finance API.
        
        Returns:
            bool: True if disconnected successfully.
        """
        logger.info("Disconnecting from Yahoo Finance API...")
        self._is_connected = False
        self._session.close()
        logger.info("Disconnected successfully.")
        return True

    def is_connected(self) -> bool:
        """
        Checks if the provider is currently connected.
        
        Returns:
            bool: Connection status.
        """
        return self._is_connected

    def _format_symbol(self, symbol: str) -> str:
        """
        Ensures the symbol is properly formatted for Yahoo Finance NSE mapping.
        """
        clean_symbol = symbol.upper().strip()
        if clean_symbol.startswith("$"):
            clean_symbol = clean_symbol[1:]
        if not clean_symbol.startswith("^") and not clean_symbol.endswith(".NS") and not clean_symbol.endswith(".BO"):
            clean_symbol = f"{clean_symbol}.NS"
        return clean_symbol

    def get_last_price(self, symbol: str) -> float:
        """
        Retrieves the last traded price (LTP) for a symbol using yfinance.
        
        Args:
            symbol: The stock symbol to query.
            
        Returns:
            float: The last traded price.
        """
        logger.debug(f"Fetching last price for {symbol} from Yahoo Finance.")
        if not self._is_connected:
            logger.warning("Provider disconnected. Returning 0.0")
            return 0.0
            
        formatted_symbol = self._format_symbol(symbol)
        
        # Check if we have recent OHLCV data in cache first
        cache_key = f"{formatted_symbol}_1d_3mo"
        with self._cache_lock:
            if cache_key in self._cache and (time.time() - self._cache[cache_key]['timestamp'] < self._cache_ttl):
                cached_data = self._cache[cache_key]['data']
                if cached_data:
                    return cached_data[-1].close
                else:
                    return 0.0
        
        for attempt in range(3):
            try:
                ticker = yf.Ticker(formatted_symbol, session=self._session)
                # Fast retrieval using fast_info if available, else history
                try:
                    price = ticker.fast_info['lastPrice']
                    return float(price)
                except Exception as e:
                    logger.debug(f"fast_info failed for {formatted_symbol}, falling back to history: {e}")
                    df = ticker.history(period="1d", interval="1d")
                    if df.empty:
                        raise ValueError(f"No data returned for {formatted_symbol}")
                    return float(df['Close'].iloc[-1])
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to fetch price for {formatted_symbol}: {e}")
                time.sleep(1)
                
        logger.error(f"Failed to fetch last price for {symbol} after 3 attempts.")
        return 0.0

    def pre_cache(self, symbols: List[str], interval: str = "1d", period: str = "3mo") -> None:
        """
        Pre-fetches data for multiple symbols in bulk using a single API call.
        """
        if not self._is_connected or not symbols:
            return
            
        # Filter symbols that are already in cache
        missing_symbols = []
        with self._cache_lock:
            for s in symbols:
                f_sym = self._format_symbol(s)
                cache_key = f"{f_sym}_{interval}_{period}"
                if cache_key in self._cache and (time.time() - self._cache[cache_key]['timestamp'] < self._cache_ttl):
                    continue
                missing_symbols.append(s)
                
        if not missing_symbols:
            logger.debug(f"All {len(symbols)} symbols already cached for {interval} {period}.")
            return
            
        logger.info(f"Bulk downloading {len(missing_symbols)} missing symbols for {interval} {period}")
        formatted_symbols = [self._format_symbol(s) for s in missing_symbols]
        sym_str = " ".join(formatted_symbols)
        
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = yf.download(sym_str, period=period, interval=interval, group_by="ticker", threads=True, progress=False, session=self._session)
            
            with self._cache_lock:
                for orig_sym, f_sym in zip(missing_symbols, formatted_symbols):
                    cache_key = f"{f_sym}_{interval}_{period}"
                    ohlcv_list = []
                    
                    if len(symbols) == 1:
                        sym_df = df
                    else:
                        if isinstance(df.columns, pd.MultiIndex):
                            if f_sym in df.columns.levels[0]:
                                sym_df = df[f_sym]
                            else:
                                sym_df = pd.DataFrame()
                        else:
                            # If it's not a MultiIndex, but we asked for multiple symbols, 
                            # it means only ONE symbol returned data.
                            if not df.empty and df.columns.name == f_sym: # yfinance sometimes sets columns.name
                                sym_df = df
                            else:
                                sym_df = pd.DataFrame()
                    
                    rows_downloaded = len(sym_df) if not sym_df.empty else 0
                    if sym_df.empty:
                        logger.warning(f"Symbol: {f_sym}, Rows downloaded: {rows_downloaded}, Reason skipped: yfinance returned empty dataframe.")
                    else:
                        logger.debug(f"Symbol: {f_sym}, Rows downloaded: {rows_downloaded}, Reason skipped: N/A")
                        
                    if not sym_df.empty:
                        sym_df = sym_df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'])
                        for index, row in sym_df.iterrows():
                            ohlcv_list.append(
                                OHLCV(
                                    timestamp=index.to_pydatetime() if hasattr(index, 'to_pydatetime') else index,
                                    open=float(row['Open']),
                                    high=float(row['High']),
                                    low=float(row['Low']),
                                    close=float(row['Close']),
                                    volume=int(row['Volume'])
                                )
                            )
                            
                    # Always cache, even if empty, to prevent fallback retries
                    self._cache[cache_key] = {
                        'timestamp': time.time(),
                        'data': ohlcv_list
                    }
                self._save_disk_cache()
        except Exception as e:
            logger.error(f"Bulk download failed for {interval} {period}: {e}")

    def get_ohlcv(self, symbol: str, interval: str = "1d", period: str = "3mo") -> List[OHLCV]:
        """
        Retrieves historical or real-time OHLCV data for a symbol.
        Supports specific intervals (e.g., '1d', '15m') and handles retries.
        
        Args:
            symbol: The stock symbol to query.
            interval: The timeframe (e.g., '1d', '15m'). Default '1d'.
            period: The lookback period (e.g., '3mo', '1mo'). Default '3mo'.
            
        Returns:
            List[OHLCV]: A standardized list of candlestick data.
        """
        logger.debug(f"Fetching OHLCV data for {symbol} ({interval}) from Yahoo Finance.")
        
        if not self._is_connected:
            logger.warning("Provider disconnected. Returning empty list.")
            return []
            
        formatted_symbol = self._format_symbol(symbol)
        cache_key = f"{formatted_symbol}_{interval}_{period}"
        
        with self._cache_lock:
            if cache_key in self._cache:
                if time.time() - self._cache[cache_key]['timestamp'] < self._cache_ttl:
                    logger.debug(f"Returning CACHED OHLCV data for {cache_key}")
                    return self._cache[cache_key]['data']
        
        for attempt in range(3):
            try:
                ticker = yf.Ticker(formatted_symbol, session=self._session)
                df = ticker.history(period=period, interval=interval)
                
                rows_downloaded = len(df) if not df.empty else 0
                if df.empty:
                    logger.warning(f"Symbol: {formatted_symbol}, Rows downloaded: {rows_downloaded}, Reason skipped: yfinance returned empty dataframe on attempt {attempt + 1}.")
                    time.sleep(1)
                    continue
                else:
                    logger.debug(f"Symbol: {formatted_symbol}, Rows downloaded: {rows_downloaded}, Reason skipped: N/A")
                
                df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
                    
                ohlcv_list = []
                # Ensure the dataframe index is a datetime
                for index, row in df.iterrows():
                    ohlcv_list.append(
                        OHLCV(
                            timestamp=index.to_pydatetime() if hasattr(index, 'to_pydatetime') else index,
                            open=float(row['Open']),
                            high=float(row['High']),
                            low=float(row['Low']),
                            close=float(row['Close']),
                            volume=int(row['Volume'])
                        )
                    )
                
                logger.debug(f"Successfully retrieved {len(ohlcv_list)} candles for {formatted_symbol}")
                
                with self._cache_lock:
                    self._cache[cache_key] = {
                        'timestamp': time.time(),
                        'data': ohlcv_list
                    }
                    
                return ohlcv_list
                
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Network error (Attempt {attempt + 1}) fetching OHLCV for {formatted_symbol}: {e}")
                time.sleep(2 * (attempt + 1))  # Exponential backoff for network errors
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to fetch OHLCV for {formatted_symbol}: {e}")
                time.sleep(1)
                
        logger.error(f"Failed to fetch OHLCV for {symbol} after 3 attempts. Invalid symbol or network error.")
        return []

    def get_volume(self, symbol: str) -> int:
        """
        Retrieves the current daily volume for a symbol.
        """
        logger.debug(f"Fetching volume for {symbol} from Yahoo Finance.")
        
        formatted_symbol = self._format_symbol(symbol)
        cache_key = f"{formatted_symbol}_1d_3mo"
        with self._cache_lock:
            if cache_key in self._cache and (time.time() - self._cache[cache_key]['timestamp'] < self._cache_ttl):
                cached_data = self._cache[cache_key]['data']
                if cached_data:
                    return cached_data[-1].volume
                else:
                    return 0
                    
        ohlcv = self.get_ohlcv(symbol, interval="1d", period="1d")
        if ohlcv:
            return ohlcv[-1].volume
        return 0

    def get_market_status(self) -> MarketStatus:
        """
        Retrieves the overall market status.
        Yahoo Finance doesn't offer a direct exchange status endpoint reliably without parsing web data,
        so this remains structurally functional but statically evaluated based on time if needed in the future.
        """
        logger.debug("Fetching market status from Yahoo Finance.")
        return MarketStatus(
            is_open=True,
            status_message="Yahoo Finance data is delayed by 15 mins. Status is assumed Open during market hours."
        )

    def get_option_chain(self, symbol: str, expiry: str = None) -> Dict[str, Any]:
        """Fetch Option Chain from Yahoo Finance (Not implemented)"""
        logger.warning("Option Chain not supported for Yahoo Finance in this implementation.")
        return {}

    def fetch_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Helper method to return DataFrame directly for DataManager compatibility."""
        formatted_symbol = self._format_symbol(symbol)
        try:
            ticker = yf.Ticker(formatted_symbol, session=self._session)
            df = ticker.history(period=period, interval=interval)
            return df if df is not None and not df.empty else pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()

    def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Alias for fetch_stock_data."""
        return self.fetch_stock_data(symbol, period, interval)
