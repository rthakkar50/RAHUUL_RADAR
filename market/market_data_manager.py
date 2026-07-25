import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketDataManager:
    """
    Unified Market Data Manager.
    
    Responsibilities:
    - Historical Data: Routed to Yahoo Finance.
    - Live Pricing/Quotes: Routed to Paytm Money.
    - Option Chain / Future Expansion: Routed to Dhan.
    """
    
    def __init__(self, yahoo_provider=None, paytm_provider=None, dhan_provider=None):
        self.yahoo = yahoo_provider
        self.paytm = paytm_provider
        self.dhan = dhan_provider
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rest_fallback_count = 0

    def get_history(self, symbol: str, interval: str = "1d", period: str = "1mo") -> Any:
        """
        Fetch historical OHLCV data.
        Routed to: Yahoo Finance
        """
        self.logger.debug(f"Fetching historical data for {symbol} (Interval: {interval}, Period: {period})")
        if self.yahoo:
            return self.yahoo.get_ohlcv(symbol, interval, period)
        raise NotImplementedError("Yahoo Provider is not initialized.")

    def get_live_price(self, symbol: str) -> float:
        """
        Fetch the Last Traded Price (LTP).
        Routed to: Paytm Money Cache -> REST Fallback
        """
        self.logger.debug(f"Fetching live price for {symbol}")
        if self.paytm:
            if hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
                sec_id = symbol.replace('.NS', '')
                price = self.paytm.ws_cache.get_cached_ltp(sec_id)
                if price > 0:
                    return price
            
            self.rest_fallback_count += 1
            return self.paytm.get_last_price(symbol)
        raise NotImplementedError("Paytm Provider is not initialized.")

    def get_live_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch full live quote (OHLC, Volume, Depth).
        Routed to: Paytm Money Cache -> REST Fallback
        """
        self.logger.debug(f"Fetching live quote for {symbol}")
        if self.paytm:
            ltp = 0.0
            vol = 0
            if hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
                sec_id = symbol.replace('.NS', '')
                ltp = self.paytm.ws_cache.get_cached_ltp(sec_id)
                vol = self.paytm.ws_cache.get_cached_vol(sec_id)
                
            if ltp <= 0:
                self.rest_fallback_count += 1
                ltp = self.paytm.get_last_price(symbol)
            if vol <= 0:
                vol = self.paytm.get_volume(symbol)
                
            return {"ltp": ltp, "volume": vol}
        raise NotImplementedError("Paytm Provider is not initialized.")

    def get_option_chain(self, symbol: str, expiry: Optional[str] = None) -> Any:
        """
        Fetch Option Chain data.
        Routed to: Dhan (Future Expansion)
        """
        self.logger.debug(f"Fetching option chain for {symbol}")
        if self.dhan:
            if hasattr(self.dhan, 'get_option_chain'):
                return self.dhan.get_option_chain(symbol, expiry)
            else:
                self.logger.warning("Dhan provider does not support get_option_chain yet.")
                return {}
        raise NotImplementedError("Dhan Provider is not initialized for option chains.")

    def subscribe(self, symbols: List[str]) -> bool:
        """
        Subscribe to WebSocket streaming for live updates.
        Routed to: Paytm Money
        """
        self.logger.debug(f"Subscribing to websocket for {len(symbols)} symbols")
        if self.paytm and hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
            sec_ids = [s.replace('.NS', '') for s in symbols]
            self.paytm.ws_cache.subscribe(sec_ids)
            return True
        return False

    def unsubscribe(self, symbols: List[str]) -> bool:
        """
        Unsubscribe from WebSocket streaming.
        Routed to: Paytm Money
        """
        self.logger.debug(f"Unsubscribing from websocket for {len(symbols)} symbols")
        if self.paytm and hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
            sec_ids = [s.replace('.NS', '') for s in symbols]
            self.paytm.ws_cache.unsubscribe(sec_ids)
            return True
        return False

    def get_cached_price(self, symbol: str) -> float:
        """
        Retrieve the latest price from the active cache (WebSocket/REST pre-cache).
        Routed to: Paytm Money Cache -> Yahoo Cache
        """
        if self.paytm:
            if hasattr(self.paytm, 'ws_cache') and self.paytm.ws_cache:
                sec_id = symbol.replace('.NS', '')
                price = self.paytm.ws_cache.get_cached_ltp(sec_id)
                if price > 0:
                    return price
            
            # Fallback to provider's internal mechanism
            self.rest_fallback_count += 1
            return self.paytm.get_last_price(symbol)
            
        return 0.0

    def get_status(self, stale_threshold_ms: int = 45000) -> Dict[str, Any]:
        """
        System Health Dashboard Metrics.
        """
        ws = getattr(self.paytm, 'ws_cache', None)
        if not ws:
            return {"error": "WebSocket cache not initialized"}
            
        last_tick_age_ms = (time.time() - ws.last_msg_time) * 1000 if ws.last_msg_time else 0
        
        ws_status = "CONNECTED" if ws.is_connected() else "DISCONNECTED"
        if ws.is_connected() and last_tick_age_ms > stale_threshold_ms:
            ws_status = "STALE"
            
        total_hits = ws.cache_hits
        total_misses = ws.cache_misses
        total_reqs = total_hits + total_misses
        hit_rate = (total_hits / total_reqs * 100) if total_reqs > 0 else 0.0
        miss_rate = (total_misses / total_reqs * 100) if total_reqs > 0 else 0.0
        
        status = {
            "websocket_status": ws_status,
            "last_tick_age_ms": round(last_tick_age_ms, 2),
            "cached_symbols": len(ws.tick_cache),
            "reconnect_count": ws.reconnect_count,
            "rest_fallback_count": self.rest_fallback_count,
            "cache_hit_rate": round(hit_rate, 2),
            "cache_miss_rate": round(miss_rate, 2)
        }
        
        # Optional debug panel / console output
        print("\n" + "="*45)
        print("   SYSTEM HEALTH DASHBOARD (Market Data)")
        print("="*45)
        for k, v in status.items():
            print(f"{k.ljust(25)}: {v}")
        print("="*45 + "\n")
        
        return status
