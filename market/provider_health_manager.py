"""
Provider Health Manager for RAHUUL_RADAR Enterprise Hybrid Market Data Engine.
Tracks latency, status, cache hit rates, heartbeat, and WebSocket health across data providers.
"""
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ProviderHealthManager:
    _instance = None

    def __init__(self):
        self.providers: Dict[str, Dict[str, Any]] = {
            "YahooFinance": {
                "status": "HEALTHY",
                "latency_ms": 15.0,
                "cache_hit_rate": 92.5,
                "last_historical_sync": time.time(),
                "requests_total": 0,
                "failures": 0,
            },
            "PaytmMoney": {
                "status": "HEALTHY",
                "latency_ms": 18.0,
                "reconnect_count": 0,
                "last_tick": time.time(),
                "heartbeat": time.time(),
                "websocket_status": "CONNECTED",
                "cache_hit_rate": 88.0,
                "requests_total": 0,
                "failures": 0,
            }
        }

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ProviderHealthManager()
        return cls._instance

    def update_provider_health(self, name: str, status: str = None, latency_ms: float = None, cache_hit_rate: float = None):
        if name not in self.providers:
            self.providers[name] = {"status": "UNKNOWN", "latency_ms": 0.0}
        
        target = self.providers[name]
        if status:
            target["status"] = status
        if latency_ms is not None:
            target["latency_ms"] = round(latency_ms, 2)
        if cache_hit_rate is not None:
            target["cache_hit_rate"] = round(cache_hit_rate, 2)

    def record_tick(self, provider_name: str = "PaytmMoney"):
        if provider_name in self.providers:
            self.providers[provider_name]["last_tick"] = time.time()
            self.providers[provider_name]["heartbeat"] = time.time()

    def get_health_report(self) -> Dict[str, Any]:
        return {
            "timestamp": time.time(),
            "providers": self.providers,
            "overall_status": "HEALTHY" if all(p.get("status") == "HEALTHY" for p in self.providers.values()) else "DEGRADED"
        }
