import json
import logging
import threading
import time
from typing import Callable, Dict, List, Any
import websocket

logger = logging.getLogger(__name__)

class PaytmLiveBroadcast:
    """
    Live Broadcast WebSocket Provider for Paytm Money.
    Handles auto-reconnect, subscription management, and tick caching.
    """
    
    WSS_URL = "wss://developer-ws.paytmmoney.com/broadcast/user/v1/data"
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = PaytmLiveBroadcast()
            return cls._instance

    def __init__(self):
        self.public_access_token = ""
        self.ws = None
        self.ws_thread = None
        self._connected = False
        self._should_reconnect = True
        
        self.tick_cache: Dict[str, float] = {}
        self.vol_cache: Dict[str, int] = {}
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.subscribed_instruments: set = set()
        
        # Heartbeat and connection management
        self.last_msg_time = 0.0
        self.monitor_thread = None
        
        # SPRINT-3.5 Monitoring Metrics
        self.reconnect_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    def set_token(self, public_access_token: str):
        self.public_access_token = public_access_token
        
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        if callback not in self.callbacks:
            self.callbacks.append(callback)
            
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def connect(self):
        if self._connected:
            return
            
        if not self.public_access_token:
            logger.error("Cannot connect PaytmLiveBroadcast: No public_access_token provided.")
            return
            
        self._should_reconnect = True
        
        def run_ws():
            backoff = 1
            consecutive_auth_failures = 0
            MAX_AUTH_FAILURES = 5
            while self._should_reconnect:
                try:
                    logger.info("Connecting to Paytm Money Live Broadcast WebSocket...")
                    
                    self.ws = websocket.WebSocketApp(
                        f"{self.WSS_URL}?x_jwt_token={self.public_access_token}",
                        on_open=self._on_open,
                        on_message=self._on_message,
                        on_error=self._on_error,
                        on_close=self._on_close,
                        on_pong=self._on_pong
                    )
                    
                    self.last_msg_time = time.time()
                    self.ws.run_forever(ping_interval=30, ping_timeout=10)
                    
                except Exception as e:
                    logger.error(f"WebSocket execution error: {e}")
                    
                if self._should_reconnect:
                    self.reconnect_count += 1
                    
                    # Detect repeated auth failures (401) - stop retrying if token is invalid
                    if not self._connected and backoff >= 16:
                        consecutive_auth_failures += 1
                        if consecutive_auth_failures >= MAX_AUTH_FAILURES:
                            logger.warning(f"WebSocket: {MAX_AUTH_FAILURES} consecutive auth failures. Stopping reconnect. Please refresh Paytm token.")
                            self._should_reconnect = False
                            break
                    else:
                        consecutive_auth_failures = 0
                    
                    logger.warning(f"WebSocket disconnected. Reconnecting in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 60)  # Exponential backoff capped at 60s
                    
        self.ws_thread = threading.Thread(target=run_ws, daemon=True)
        self.ws_thread.start()
        
        self._start_heartbeat_monitor()

    def _start_heartbeat_monitor(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
            
        def monitor():
            while self._should_reconnect:
                if self._connected:
                    if time.time() - self.last_msg_time > 45:
                        logger.error("Heartbeat timeout. No messages or pongs received in 45s. Forcing reconnect...")
                        if self.ws:
                            self.ws.close()
                time.sleep(5)
                
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

    def disconnect(self):
        self._should_reconnect = False
        if self.ws:
            self.ws.close()
        self._connected = False
        
    def is_connected(self):
        return self._connected

    def _on_open(self, ws):
        logger.info("Paytm Money Live Broadcast connected successfully.")
        self._connected = True
        self.last_msg_time = time.time()
        
        # Resubscribe to existing instruments if any
        if self.subscribed_instruments:
            self._send_subscription(list(self.subscribed_instruments), "SUBSCRIBE")

    def _on_pong(self, ws, message):
        self.last_msg_time = time.time()

    def _on_message(self, ws, message):
        self.last_msg_time = time.time()
        try:
            if isinstance(message, bytes):
                message = message.decode('utf-8')
                
            data = json.loads(message)
            
            items = data.get('data', [])
            for item in items:
                sec_id = item.get('security_id')
                ltp = item.get('last_price', item.get('lastPrice', item.get('ltp')))
                vol = item.get('volume', item.get('traded_volume'))
                
                if sec_id:
                    if ltp is not None:
                        self.tick_cache[str(sec_id)] = float(ltp)
                    if vol is not None:
                        self.vol_cache[str(sec_id)] = int(vol)
                        
            for cb in self.callbacks:
                try:
                    cb(data)
                except Exception as e:
                    logger.error(f"Error in WebSocket callback: {e}")
                    
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
        self._connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        logger.warning(f"WebSocket closed: code={close_status_code}, msg={close_msg}")
        self._connected = False

    def subscribe(self, security_ids: List[str]):
        """Subscribe to a list of security IDs"""
        new_ids = [str(sid) for sid in security_ids if str(sid) not in self.subscribed_instruments]
        if not new_ids:
            return
            
        for sid in new_ids:
            self.subscribed_instruments.add(sid)
            
        if self._connected:
            self._send_subscription(new_ids, "SUBSCRIBE")

    def unsubscribe(self, security_ids: List[str]):
        """Unsubscribe from a list of security IDs"""
        remove_ids = [str(sid) for sid in security_ids if str(sid) in self.subscribed_instruments]
        if not remove_ids:
            return
            
        for sid in remove_ids:
            self.subscribed_instruments.discard(sid)
            
        if self._connected:
            self._send_subscription(remove_ids, "UNSUBSCRIBE")

    def _send_subscription(self, security_ids: List[str], action: str):
        """Send subscription payload. Action = 'SUBSCRIBE' or 'UNSUBSCRIBE'"""
        if not self.ws or not self._connected:
            return
            
        prefs = [f"NSE:{sid}:EQUITY" for sid in security_ids]
        
        payload = {
            "action": action,
            "mode": "LTP",
            "preferences": prefs
        }
        
        try:
            self.ws.send(json.dumps(payload))
        except Exception as e:
            logger.error(f"Failed to send {action} command: {e}")

    def get_cached_ltp(self, security_id: str) -> float:
        """Get the latest cached LTP for a security ID"""
        val = self.tick_cache.get(str(security_id), 0.0)
        if val > 0:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        return val

    def get_cached_vol(self, security_id: str) -> int:
        """Get the latest cached volume for a security ID"""
        return self.vol_cache.get(str(security_id), 0)
