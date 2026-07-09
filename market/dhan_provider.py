"""
Dhan API data provider implementation for RAHUUL_RADAR.
Uses DhanHQ for blazing-fast real-time data, with Yahoo Finance as a fallback for historical OHLCV if needed.
"""
import os
import csv
import urllib.request
from datetime import datetime, timedelta
import pandas as pd
from typing import List

from market.data_provider import MarketDataProvider, OHLCV, MarketStatus
from market.yahoo_provider import YahooFinanceProvider
from utils.logger import get_logger

logger = get_logger(__name__)

class DhanProvider(MarketDataProvider):
    """
    Concrete implementation of MarketDataProvider for Dhan API.
    Provides fast real-time data and historical data using dhanhq.
    """

    def __init__(self, client_id: str, access_token: str) -> None:
        self.client_id = client_id
        self.access_token = access_token
        self._is_connected = False
        self.dhan = None
        self.yahoo_fallback = YahooFinanceProvider()
        
        # Caches
        self.symbol_to_security_id = {}
        self._cache_ltp = {}
        self._cache_ttl = 30 # seconds
        
        logger.info("Initialized DhanProvider.")

    def connect(self) -> bool:
        """
        Establishes connection to Dhan API using DhanContext.
        """
        try:
            from dhanhq import dhanhq, DhanContext
            # New dhanhq API: requires DhanContext object
            context = DhanContext(self.client_id, self.access_token)
            self.dhan = dhanhq(context)
            
            # Verify connection by getting fund limits
            funds = self.dhan.get_fund_limits()
            if isinstance(funds, dict) and funds.get('status') == 'success':
                self._is_connected = True
                logger.info("[SUCCESS] Successfully connected to Dhan API.")
                self._load_instruments()
                self.yahoo_fallback.connect()
                return True
            else:
                logger.warning(f"Dhan connected but fund check returned: {funds}")
                # Still mark connected — API responded
                self._is_connected = True
                self._load_instruments()
                self.yahoo_fallback.connect()
                return True
        except Exception as e:
            logger.error(f"Error connecting to Dhan: {e}")
            self.yahoo_fallback.connect()
            return False


    def disconnect(self) -> bool:
        self._is_connected = False
        self.yahoo_fallback.disconnect()
        return True

    def is_connected(self) -> bool:
        return self._is_connected

    def _load_instruments(self):
        """
        Downloads and parses the Dhan API scrip master CSV.
        Maps NSE symbols (e.g. RELIANCE) to security_id.
        """
        try:
            url = "https://images.dhan.co/api-data/api-scrip-master.csv"
            import tempfile
            temp_path = os.path.join(tempfile.gettempdir(), "api-scrip-master.csv")
            
            if not os.path.exists(temp_path) or (datetime.now().timestamp() - os.path.getmtime(temp_path) > 86400):
                logger.info("Downloading Dhan instrument master CSV...")
                urllib.request.urlretrieve(url, temp_path)
            
            # Read CSV and build map
            df = pd.read_csv(temp_path, low_memory=False)
            
            # Filter for NSE EQUITY
            nse_df = df[(df['SEM_EXM_EXCH_ID'] == 'NSE') & ((df['SEM_SERIES'] == 'EQ') | (df['SEM_SERIES'] == 'IN'))] if 'SEM_EXM_EXCH_ID' in df.columns else df
            
            for index, row in nse_df.iterrows():
                if 'SEM_TRADING_SYMBOL' in row and 'SEM_SMST_SECURITY_ID' in row:
                    sym = str(row['SEM_TRADING_SYMBOL']).strip()
                    sec_id = str(row['SEM_SMST_SECURITY_ID']).strip()
                    self.symbol_to_security_id[sym] = sec_id
                
            # Explicit mappings for indices
            # Dhan lists NIFTY 50 and NIFTY BANK under IDX
            idx_df = df[df['SEM_EXM_EXCH_ID'] == 'IDX'] if 'SEM_EXM_EXCH_ID' in df.columns else df
            for index, row in idx_df.iterrows():
                if 'SEM_TRADING_SYMBOL' in row and 'SEM_SMST_SECURITY_ID' in row:
                    sym = str(row['SEM_TRADING_SYMBOL']).strip()
                    sec_id = str(row['SEM_SMST_SECURITY_ID']).strip()
                    self.symbol_to_security_id[sym] = sec_id

            # Mapping for RAHUUL_RADAR symbols
            if 'NIFTY 50' in self.symbol_to_security_id:
                self.symbol_to_security_id['^NSEI'] = self.symbol_to_security_id['NIFTY 50']
            elif 'NIFTY-50' in self.symbol_to_security_id:
                 self.symbol_to_security_id['^NSEI'] = self.symbol_to_security_id['NIFTY-50']
                 
            if 'NIFTY BANK' in self.symbol_to_security_id:
                self.symbol_to_security_id['^NSEBANK'] = self.symbol_to_security_id['NIFTY BANK']
            elif 'BANKNIFTY' in self.symbol_to_security_id:
                self.symbol_to_security_id['^NSEBANK'] = self.symbol_to_security_id['BANKNIFTY']

            logger.info(f"Loaded {len(self.symbol_to_security_id)} Dhan instruments.")
        except Exception as e:
            logger.error(f"Failed to load Dhan instruments: {e}")

    def _get_clean_symbol(self, symbol: str) -> str:
        s = symbol.upper().replace('.NS', '').replace('.BO', '')
        return s

    def get_last_price(self, symbol: str) -> float:
        if not self._is_connected:
            return self.yahoo_fallback.get_last_price(symbol)
            
        clean_sym = self._get_clean_symbol(symbol)
        sec_id = self.symbol_to_security_id.get(clean_sym)
        
        exchange = "NSE_EQ"
        if clean_sym in ["^NSEI", "^NSEBANK"] or not sec_id:
             exchange = "IDX_I"

        if not sec_id:
            # Maybe the user appended -EQ or something, try mapping fallback
            sec_id = self.symbol_to_security_id.get(f"{clean_sym}-EQ")
            if not sec_id:
                return self.yahoo_fallback.get_last_price(symbol)
            
        try:
            now = datetime.now()
            if symbol in self._cache_ltp:
                cached_time, price = self._cache_ltp[symbol]
                if (now - cached_time).total_seconds() < 5:
                    return price
            
            # Fetch LTP from Dhan Market Quote API. 
            # Note: For free dhanhq we can use market quote or rely on fallback if it fails.
            # Some segments like IDX_I might require different endpoints in v2.
            # We wrap this in try-catch so it safely falls back to Yahoo.
            # Using standard dict format for market_quote in dhanhq: 
            # dhan.market_quote({'exchange_segment': 'NSE_EQ', 'security_id': sec_id})
            
            try:
                 res = self.dhan.market_quote({sec_id: exchange})
                 if hasattr(res, 'get') and res.get('status') == 'success':
                     data = res.get('data', {})
                     if data:
                         first_key = list(data.keys())[0]
                         ltp = data[first_key].get('last_price', 0.0)
                         if ltp > 0:
                             self._cache_ltp[symbol] = (now, float(ltp))
                             return float(ltp)
            except Exception as e:
                 logger.debug(f"Dhan market_quote parsing failed for {sec_id}: {e}")
                 
        except Exception as e:
            logger.error(f"Dhan API LTP error for {symbol}: {e}")
            
        return self.yahoo_fallback.get_last_price(symbol)

    def get_ohlcv(self, symbol: str, interval: str = "1d", period: str = "3mo") -> List[OHLCV]:
        """
        Fallback to yahoo if requested by get_ohlcv.
        But for strictly Dhan, get_historical_data should be used.
        """
        return self.yahoo_fallback.get_ohlcv(symbol, interval, period)
        
    def pre_cache(self, symbols: List[str], interval: str = "1d", period: str = "3mo") -> None:
        """Delegates pre-caching to the Yahoo fallback provider."""
        if hasattr(self.yahoo_fallback, 'pre_cache'):
            self.yahoo_fallback.pre_cache(symbols, interval, period)
        
    def get_historical_data(self, symbol: str, interval: str = "1", days: int = 2) -> List[OHLCV]:
        if not self._is_connected:
            raise Exception("Dhan API not connected")
            
        clean_sym = self._get_clean_symbol(symbol)
        sec_id = self.symbol_to_security_id.get(clean_sym)
        if not sec_id:
            raise Exception(f"Security ID not found for {clean_sym}")
            
        exchange = "NSE_EQ"
        if clean_sym in ["^NSEI", "^NSEBANK"]:
            exchange = "IDX_I"
            
        try:
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Map interval correctly (dhanhq typically supports 1, 5, 15, 25, 60)
            int_map = {"1": 1, "5": 5, "15": 15, "30": 15, "60": 60}
            dhan_interval = int_map.get(interval, 1)
            
            res = self.dhan.intraday_minute_data(
                security_id=sec_id,
                exchange_segment=exchange,
                instrument_type='EQUITY' if exchange == 'NSE_EQ' else 'INDEX',
                from_date=from_date,
                to_date=to_date,
                interval=dhan_interval
            )
            
            if res and hasattr(res, 'get') and res.get('status') == 'success':
                data = res.get('data', {})
                if not data or not data.get('start_Time'):
                    return []
                    
                ohlcv_list = []
                # Dhan returns lists of columns
                starts = data.get('start_Time', [])
                opens = data.get('open', [])
                highs = data.get('high', [])
                lows = data.get('low', [])
                closes = data.get('close', [])
                volumes = data.get('volume', [])
                
                for i in range(len(starts)):
                    # Convert Dhan timestamp to ISO format string
                    # Dhan timestamp might be integer or string (epoch or custom format)
                    # Let's rely on standard datetime conversion if possible, or just raw string if it's already string
                    try:
                        ts = int(starts[i])
                        dt = datetime.fromtimestamp(ts).isoformat()
                    except (ValueError, TypeError):
                        dt = str(starts[i])
                        
                    ohlcv_list.append(OHLCV(
                        open=float(opens[i]),
                        high=float(highs[i]),
                        low=float(lows[i]),
                        close=float(closes[i]),
                        volume=int(volumes[i]) if volumes else 0,
                        timestamp=dt
                    ))
                return ohlcv_list
            else:
                logger.error(f"Dhan API historical data error for {symbol}: {res}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching historical data from Dhan for {symbol}: {e}")
            return []

    def get_volume(self, symbol: str) -> int:
        return self.yahoo_fallback.get_volume(symbol)

    def get_market_status(self) -> MarketStatus:
        return self.yahoo_fallback.get_market_status()
