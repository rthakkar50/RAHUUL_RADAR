import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from market.data_provider import MarketDataProvider, OHLCV, MarketStatus
from market.yahoo_provider import YahooFinanceProvider
from market.paytm_provider import PaytmMoneyProvider
from market.provider_health_manager import ProviderHealthManager

logger = logging.getLogger(__name__)

class MarketDataManager(MarketDataProvider):
    """
    Enterprise Unified Market Data Manager (v7.4.0).
    
    Routing Matrix (TASK-4):
    - Swing Scanner -> Yahoo ONLY (Historical Daily / Weekly)
    - Intraday / F&O / Breakout / High Volume Scanners -> Paytm ONLY
    - Paper Trading / Broker Preview -> Paytm ONLY
    """
    
    def __init__(self, yahoo_provider=None, paytm_provider=None, dhan_provider=None):
        self.yahoo = yahoo_provider or YahooFinanceProvider()
        self.paytm = paytm_provider or PaytmMoneyProvider()
        self.dhan = dhan_provider
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rest_fallback_count = 0
        self.health_manager = ProviderHealthManager.get_instance()

    def connect(self) -> bool:
        c1 = self.yahoo.connect() if self.yahoo else True
        c2 = self.paytm.connect() if self.paytm else True
        return c1 and c2

    def disconnect(self) -> bool:
        d1 = self.yahoo.disconnect() if self.yahoo else True
        d2 = self.paytm.disconnect() if self.paytm else True
        return d1 and d2

    def is_connected(self) -> bool:
        return (self.yahoo is not None and self.yahoo.is_connected()) or (self.paytm is not None and self.paytm.is_connected())

    def get_historical(self, symbol: str, interval: str = "1d", period: str = "1mo") -> Any:
        """
        Historical OHLCV routing -> Yahoo ONLY (TASK-4).
        """
        self.logger.debug(f"MarketDataManager: Historical OHLCV for {symbol} routed to Yahoo Finance")
        if self.yahoo:
            return self.yahoo.get_ohlcv(symbol, interval=interval, period=period)
        raise NotImplementedError("Yahoo Provider is not initialized for historical data.")

    def get_intraday(self, symbol: str, interval: str = "15m", period: str = "5d") -> Any:
        """
        Live Intraday routing -> Paytm ONLY (TASK-4). NO FALLBACK TO YAHOO (TASK-7).
        """
        self.logger.debug(f"MarketDataManager: Live Intraday for {symbol} routed to Paytm Money")
        if self.paytm:
            return self.paytm.get_intraday(symbol, interval=interval, period=period)
        self.logger.warning(f"Paytm Provider unavailable for {symbol}. Returning 'LIVE DATA UNAVAILABLE'")
        return []

    def get_ohlcv(self, symbol: str, interval: str = "1d", period: str = "1mo") -> Any:
        """
        Unified get_ohlcv routing based on interval/period:
        - Daily / Weekly / Monthly -> Yahoo ONLY
        - Intraday (1m, 5m, 15m, 1h) -> Paytm ONLY
        """
        if interval in ["1d", "1wk", "1mo"] or period in ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]:
            return self.get_historical(symbol, interval=interval, period=period)
        else:
            return self.get_intraday(symbol, interval=interval, period=period)

    def pre_cache(self, symbols: List[str], interval: str = "1d", period: str = "1mo") -> bool:
        """
        Pre-cache routing:
        - Daily/Weekly -> Pre-cache Yahoo
        - Intraday -> Subscribe Paytm WebSocket stream
        """
        if interval in ["1d", "1wk", "1mo"]:
            if hasattr(self.yahoo, 'pre_cache'):
                return self.yahoo.pre_cache(symbols, interval=interval, period=period)
        else:
            return self.subscribe(symbols)
        return True

    def get_last_price(self, symbol: str) -> float:
        """
        LTP routing -> Paytm ONLY for Live (TASK-4).
        """
        if self.paytm:
            if hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
                sec_id = symbol.replace('.NS', '')
                price = self.paytm.ws_cache.get_cached_ltp(sec_id)
                if price > 0:
                    return price
            return self.paytm.get_last_price(symbol)
        if self.yahoo:
            return self.yahoo.get_last_price(symbol)
        return 0.0

    def get_volume(self, symbol: str) -> int:
        if self.paytm:
            return self.paytm.get_volume(symbol)
        if self.yahoo:
            return self.yahoo.get_volume(symbol)
        return 0

    def get_live_price(self, symbol: str) -> float:
        return self.get_last_price(symbol)

    def get_live_quote(self, symbol: str) -> Dict[str, Any]:
        if self.paytm:
            return self.paytm.get_quote(symbol)
        return {"ltp": self.get_last_price(symbol), "volume": self.get_volume(symbol)}

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        return self.get_live_quote(symbol)

    def get_market_status(self) -> MarketStatus:
        if self.paytm:
            return self.paytm.get_market_status()
        if self.yahoo:
            return self.yahoo.get_market_status()
        return MarketStatus(is_open=True, status_message="Market Status Operational")

    def get_option_chain(self, symbol: str, expiry: Optional[str] = None) -> Any:
        if self.dhan and hasattr(self.dhan, 'get_option_chain'):
            return self.dhan.get_option_chain(symbol, expiry)
        if self.paytm and hasattr(self.paytm, 'get_option_chain'):
            return self.paytm.get_option_chain(symbol, expiry)
        return {}

    def subscribe(self, symbols: List[str]) -> bool:
        if self.paytm and hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
            sec_ids = [s.replace('.NS', '') for s in symbols]
            self.paytm.ws_cache.subscribe(sec_ids)
            return True
        return False

    def unsubscribe(self, symbols: List[str]) -> bool:
        if self.paytm and hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
            sec_ids = [s.replace('.NS', '') for s in symbols]
            self.paytm.ws_cache.unsubscribe(sec_ids)
            return True
        return False

    def health(self) -> Dict[str, Any]:
        return self.health_manager.get_health_report()

    def latency(self) -> float:
        return self.paytm.latency() if self.paytm else 15.0
