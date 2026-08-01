"""
RAHUUL RADAR — AI Engine V2: Feature Store
==========================================
High-speed in-memory feature cache for zero-redundancy inference.
Prevents repeated DataFrame manipulation or indicator recalculation.
"""

import time
import threading
from typing import Dict, Any, Optional


class FeatureStore:
    """
    Thread-safe Feature Store with TTL eviction.
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

    def __init__(self, ttl_seconds: float = 60.0):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}
        self._store_lock = threading.Lock()

    def _make_key(self, symbol: str, timeframe: str = "15m") -> str:
        return f"{symbol.upper()}:{timeframe.lower()}"

    def store_features(self, symbol: str, features: Dict[str, float], timeframe: str = "15m") -> None:
        """Stores feature map for symbol and timeframe."""
        key = self._make_key(symbol, timeframe)
        with self._store_lock:
            self._store[key] = {
                "features": features,
                "timestamp": time.time()
            }

    def get_features(self, symbol: str, timeframe: str = "15m") -> Optional[Dict[str, float]]:
        """Retrieves cached feature map if within TTL."""
        key = self._make_key(symbol, timeframe)
        with self._store_lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if time.time() - entry["timestamp"] > self.ttl_seconds:
                del self._store[key]
                return None
            return entry["features"]

    def clear(self) -> None:
        """Clears all cached features."""
        with self._store_lock:
            self._store.clear()
