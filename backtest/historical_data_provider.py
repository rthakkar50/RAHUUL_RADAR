import yfinance as yf
from typing import List
from market.data_provider import MarketDataProvider, OHLCV, MarketStatus
from utils.logger import get_logger

logger = get_logger(__name__)

class HistoricalDataProvider(MarketDataProvider):
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
