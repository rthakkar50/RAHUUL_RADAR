"""
RAHUUL RADAR — F&O Engine: Option Chain Engine (Task 4)
======================================================
Fetches, constructs, and caches option chain data.
Supports Call/Put OI, Change in OI, Volume, LTP, Bid, Ask, OHLC, and TTL caching.
"""

import time
import math
import threading
from typing import Dict, List, Any, Optional
from core.fno_engine.fno_models import OptionChainItem
from core.fno_engine.contract_selector import ContractSelector


class OptionChainEngine:
    """
    High-speed Option Chain Builder with thread-safe caching.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self, ttl_seconds: float = 15.0):
        self.ttl_seconds = ttl_seconds
        self.selector = ContractSelector()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()

    def get_option_chain(
        self,
        underlying: str,
        spot_price: float,
        expiry: str,
        step: float = 50.0,
        range_strikes: int = 10
    ) -> List[OptionChainItem]:
        """
        Retrieves or generates option chain items for underlying.
        Returns cached list if within TTL.
        """
        cache_key = f"{underlying.upper()}:{expiry}:{spot_price}"
        with self._cache_lock:
            entry = self._cache.get(cache_key)
            if entry and (time.time() - entry["timestamp"] < self.ttl_seconds):
                return entry["chain"]

        strikes = self.selector.get_strike_chain_range(spot_price, step=step, num_strikes_above_below=range_strikes)
        atm_strike = self.selector.get_atm_strike(spot_price, step=step)

        chain = []
        for strike in strikes:
            dist = (strike - atm_strike) / max(step, 1.0)
            
            # Synthetic realistic OI & LTP modeling
            call_oi = int(max(50000 - dist * 3500 + (hash(f"{strike}CE") % 10000), 5000))
            put_oi = int(max(50000 + dist * 3500 + (hash(f"{strike}PE") % 10000), 5000))

            call_change_oi = int(call_oi * 0.08 * (-1 if dist > 0 else 1))
            put_change_oi = int(put_oi * 0.10 * (1 if dist >= 0 else -1))

            call_ltp = max(round(max(spot_price - strike, 0.0) + max(150.0 - abs(dist) * 18.0, 5.0), 2), 0.5)
            put_ltp = max(round(max(strike - spot_price, 0.0) + max(150.0 - abs(dist) * 18.0, 5.0), 2), 0.5)

            call_vol = int(call_oi * 0.25)
            put_vol = int(put_oi * 0.28)

            call_iv = round(max(14.5 + abs(dist) * 0.4, 10.0), 2)
            put_iv = round(max(15.2 + abs(dist) * 0.5, 10.0), 2)

            item = OptionChainItem(
                strike_price=strike,
                call_oi=call_oi,
                put_oi=put_oi,
                call_change_oi=call_change_oi,
                put_change_oi=put_change_oi,
                call_ltp=call_ltp,
                put_ltp=put_ltp,
                call_volume=call_vol,
                put_volume=put_vol,
                call_iv=call_iv,
                put_iv=put_iv,
                call_bid=round(call_ltp * 0.99, 2),
                call_ask=round(call_ltp * 1.01, 2),
                put_bid=round(put_ltp * 0.99, 2),
                put_ask=round(put_ltp * 1.01, 2),
                open_price=call_ltp,
                high_price=round(call_ltp * 1.05, 2),
                low_price=round(call_ltp * 0.95, 2),
                close_price=call_ltp
            )
            chain.append(item)

        with self._cache_lock:
            self._cache[cache_key] = {
                "chain": chain,
                "timestamp": time.time()
            }

        return chain

    def clear_cache(self):
        """Clears option chain cache."""
        with self._cache_lock:
            self._cache.clear()
