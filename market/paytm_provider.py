import os
import json
import time
import logging
from datetime import datetime, timedelta, timezone
import requests
from typing import List, Dict, Any, Tuple, Optional
from market.data_provider import MarketDataProvider, OHLCV, MarketStatus
from market.yahoo_provider import YahooFinanceProvider
from market.paytm_websocket import PaytmLiveBroadcast

IST_TZ = timezone(timedelta(hours=5, minutes=30))

class PaytmMoneyProvider(MarketDataProvider):
    """
    Paytm Money Data Provider Implementation.
    Phase 2: Working implementation with OAuth auth and Market Data API.
    """
    
    BASE_URL_ACCOUNTS = "https://developer.paytmmoney.com/accounts"
    BASE_URL_DATA = "https://developer.paytmmoney.com/data"
    DEFAULT_HTTP_TIMEOUT = 5.0
    OPTION_CHAIN_CACHE_TTL = 60.0
    # Official Paytm Money / NSE 1980-01-01T00:00:00Z epoch offset (pyPMClient epochConverterUtil)
    PAYTM_EPOCH_OFFSET = 315532800
    
    def __init__(self, timeout: float = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._connected = False
        self.timeout = float(os.environ.get("PAYTM_HTTP_TIMEOUT", str(self.DEFAULT_HTTP_TIMEOUT))) if timeout is None else float(timeout)
        
        self.api_key = os.environ.get("PAYTM_API_KEY", None)
        self.api_secret = os.environ.get("PAYTM_API_SECRET", None)
        self.request_token = os.environ.get("PAYTM_REQUEST_TOKEN", None)
        self.access_token = os.environ.get("PAYTM_ACCESS_TOKEN", None)
        self.public_access_token = os.environ.get("PAYTM_PUBLIC_ACCESS_TOKEN", None)
        self.read_access_token = os.environ.get("PAYTM_READ_ACCESS_TOKEN", None)
        self.token_expiry = 0.0
        
        self.fallback = YahooFinanceProvider()
        self.ws_cache = PaytmLiveBroadcast.get_instance()
        self._rest_cache: Dict[str, Dict[str, Any]] = {}
        self._last_quote_meta: Dict[str, Dict[str, Any]] = {}
        self.last_ohlcv_status: Dict[str, Dict[str, Any]] = {}
        self._option_chain_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self.stats = {
            "success": 0,
            "fallback_count": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        self._load_credentials_from_config()

        if not self.api_key or self.api_key == "YOUR_PAYTM_API_KEY":
            self.logger.warning("PaytmMoneyProvider: Paytm API key not set. Using Yahoo Finance fallback for live market data.")
            self._use_fallback_only = True
        else:
            self._use_fallback_only = False

    def _load_credentials_from_config(self):
        try:
            config_path = os.path.join(os.getcwd(), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    if isinstance(config_data, dict):
                        paytm_block = config_data.get("paytm")
                        if not isinstance(paytm_block, dict):
                            paytm_block = {}
                        if not self.api_key:
                            self.api_key = paytm_block.get("api_key") or config_data.get("paytm_api_key") or ""
                        if not self.api_secret:
                            self.api_secret = (
                                paytm_block.get("api_secret_key")
                                or paytm_block.get("api_secret")
                                or config_data.get("paytm_api_secret")
                                or ""
                            )
                        if not self.request_token:
                            # Sometimes it might be in the config or we just rely on OAuth callback to set it dynamically
                            self.request_token = paytm_block.get("request_token") or config_data.get("paytm_request_token") or ""

                        if not self.access_token:
                            self.access_token = paytm_block.get("access_token") or config_data.get("paytm_access_token") or ""
                        if not self.public_access_token:
                            self.public_access_token = paytm_block.get("public_access_token") or config_data.get("paytm_public_access_token") or ""
                        if not self.read_access_token:
                            self.read_access_token = paytm_block.get("read_access_token") or config_data.get("paytm_read_access_token") or ""
                        raw_expiry = paytm_block.get("token_expiry") if "token_expiry" in paytm_block else config_data.get("paytm_token_expiry", 0.0)
                        if not getattr(self, "token_expiry", 0.0):
                            self.token_expiry = float(raw_expiry or 0.0)
                        if "http_timeout" in paytm_block and self.timeout == self.DEFAULT_HTTP_TIMEOUT:
                            try:
                                self.timeout = float(paytm_block.get("http_timeout", self.DEFAULT_HTTP_TIMEOUT))
                            except (ValueError, TypeError):
                                pass
            if self.api_key:
                from market.paytm_auth_manager import PaytmAuthManager
                auth_mgr = PaytmAuthManager.get_instance()
                if not self.request_token and auth_mgr.request_token:
                    self.request_token = auth_mgr.request_token
                if not self.access_token and auth_mgr.access_token:
                    self.access_token = auth_mgr.access_token
                if not self.public_access_token and auth_mgr.public_access_token:
                    self.public_access_token = auth_mgr.public_access_token
                if not self.read_access_token and auth_mgr.read_access_token:
                    self.read_access_token = auth_mgr.read_access_token
                if not getattr(self, "token_expiry", 0.0) and getattr(auth_mgr, "token_expiry", 0.0):
                    self.token_expiry = float(auth_mgr.token_expiry or 0.0)
        except Exception as e:
            self.logger.warning(f"Failed to load Paytm credentials from config.json: {e}")

    def connect(self) -> bool:
        self.logger.info("Attempting to connect to Paytm Money API...")
        from market.paytm_auth_manager import PaytmAuthManager
        auth_mgr = PaytmAuthManager.get_instance()
        if not auth_mgr.api_key and self.api_key:
            auth_mgr.api_key = self.api_key
        if not auth_mgr.api_secret and self.api_secret:
            auth_mgr.api_secret = self.api_secret
        if not auth_mgr.request_token and self.request_token:
            auth_mgr.request_token = self.request_token
        if not auth_mgr.access_token and self.access_token:
            auth_mgr.access_token = self.access_token
        if not auth_mgr.read_access_token and self.read_access_token:
            auth_mgr.read_access_token = self.read_access_token
        if not auth_mgr.public_access_token and self.public_access_token:
            auth_mgr.public_access_token = self.public_access_token
        if not getattr(auth_mgr, "token_expiry", 0.0) and getattr(self, "token_expiry", 0.0):
            auth_mgr.token_expiry = self.token_expiry
        
        if auth_mgr.is_authenticated():
            self.access_token = auth_mgr.access_token or self.access_token
            self.read_access_token = auth_mgr.read_access_token or self.read_access_token
            self.public_access_token = auth_mgr.public_access_token or self.public_access_token
            self.token_expiry = getattr(auth_mgr, "token_expiry", 0.0) or getattr(self, "token_expiry", 0.0)
            self.logger.info("Paytm Login Success: Using stored authenticated Paytm tokens.")
            self._connected = True
            try:
                self.fallback.connect()
            except Exception as e:
                self.logger.warning(f"Fallback connect failed: {e}")
            if self.public_access_token:
                self.ws_cache.set_token(self.public_access_token)
                self.ws_cache.connect()
            return True
            
        success, msg = auth_mgr.refresh_token()
        if success:
            self.access_token = auth_mgr.access_token or self.access_token
            self.read_access_token = auth_mgr.read_access_token or self.read_access_token
            self.public_access_token = auth_mgr.public_access_token or self.public_access_token
            self.token_expiry = getattr(auth_mgr, "token_expiry", 0.0) or getattr(self, "token_expiry", 0.0)
            self.logger.info("Paytm Login Success: Token Refreshed via PaytmAuthManager.")
            self._connected = True
            try:
                self.fallback.connect()
            except Exception as e:
                self.logger.warning(f"Fallback connect failed: {e}")
            if self.public_access_token:
                self.ws_cache.set_token(self.public_access_token)
                self.ws_cache.connect()
            return True
            
        return False

    def _refresh_token(self):
        """Helper to handle expired token - marks session disconnected and requires clean re-authentication"""
        self.logger.error("Paytm Money API token expired. Session terminated.")
        self._connected = False
        from broker.utils.exceptions import TokenExpiredError
        raise TokenExpiredError("Paytm session token expired. Clean re-authentication required.")

    def disconnect(self) -> bool:
        self.logger.info("Disconnecting from Paytm Money API...")
        self.access_token = None
        self.public_access_token = None
        self.read_access_token = None
        self._connected = False
        if self.ws_cache:
            self.ws_cache.disconnect()
        self.logger.info("Disconnected successfully.")
        return True

    def is_connected(self) -> bool:
        return self._connected

    _symbol_to_security_id: Dict[str, str] = {}
    _instruments_loaded: bool = False
    _INDEX_SECURITY_IDS: Dict[str, str] = {
        "NIFTY": "13",
        "^NSEI": "13",
        "NIFTY 50": "13",
        "NIFTY-50": "13",
        "NIFTY50": "13",
        "BANKNIFTY": "25",
        "^NSEBANK": "25",
        "NIFTY BANK": "25",
        "NIFTY-BANK": "25",
        "FINNIFTY": "27",
        "MIDCPNIFTY": "442",
    }

    def _load_instruments(self):
        if PaytmMoneyProvider._instruments_loaded and PaytmMoneyProvider._symbol_to_security_id:
            self.symbol_to_security_id = PaytmMoneyProvider._symbol_to_security_id
            return
        try:
            from market.dhan_provider import DhanProvider
            self.symbol_to_security_id = PaytmMoneyProvider._symbol_to_security_id
            DhanProvider._load_instruments(self)
            if PaytmMoneyProvider._symbol_to_security_id:
                PaytmMoneyProvider._instruments_loaded = True
        except Exception as e:
            self.logger.warning(f"Failed to load instrument mapping for PaytmMoneyProvider: {e}")

    def _get_security_id(self, symbol: str) -> str:
        """Helper method to resolve trading symbol to security ID"""
        clean_sym = str(symbol or "").strip().upper().replace('.NS', '').replace('.BO', '')
        if not clean_sym:
            return ""
        if clean_sym.isdigit():
            return clean_sym
        if clean_sym in self._INDEX_SECURITY_IDS:
            return self._INDEX_SECURITY_IDS[clean_sym]
        if not PaytmMoneyProvider._instruments_loaded or not PaytmMoneyProvider._symbol_to_security_id:
            self._load_instruments()
        sec_id = PaytmMoneyProvider._symbol_to_security_id.get(clean_sym) or PaytmMoneyProvider._symbol_to_security_id.get(f"{clean_sym}-EQ")
        return str(sec_id).strip() if sec_id else clean_sym

    @classmethod
    def convert_paytm_epoch(cls, raw_epoch: Any) -> Optional[int]:
        """
        Converts Paytm Money's 1980-01-01 UTC offset epoch (pyPMClient epochConverterUtil)
        into a standard 1970-01-01 Unix epoch timestamp in seconds.
        """
        if raw_epoch is None or raw_epoch == "":
            return None
        try:
            val = float(raw_epoch)
        except (ValueError, TypeError):
            return None
        if val <= 0:
            return None
        if val >= 1_000_000_000_000:
            val = val / 1000.0
        ival = int(val)
        # Paytm live quote timestamps are seconds since 1980-01-01T00:00:00Z (+315532800s offset)
        if 1_000_000_000 <= ival < 1_600_000_000:
            return ival + cls.PAYTM_EPOCH_OFFSET
        return ival

    @classmethod
    def _parse_candle_timestamp(cls, raw_ts: Any) -> Optional[datetime]:
        """Parse Paytm candle timestamp (epoch or ISO/date string) into naive IST datetime."""
        if raw_ts is None:
            return None
        if isinstance(raw_ts, datetime):
            if raw_ts.tzinfo is not None:
                return raw_ts.astimezone(IST_TZ).replace(tzinfo=None)
            return raw_ts
        if isinstance(raw_ts, (int, float)) or (isinstance(raw_ts, str) and raw_ts.strip().isdigit()):
            unix_ts = cls.convert_paytm_epoch(raw_ts)
            if not unix_ts:
                return None
            return datetime.fromtimestamp(unix_ts, tz=IST_TZ).replace(tzinfo=None)
        if isinstance(raw_ts, str):
            s = raw_ts.strip()
            if not s:
                return None
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                if dt.tzinfo is not None:
                    return dt.astimezone(IST_TZ).replace(tzinfo=None)
                return dt
            except ValueError:
                pass
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y"):
                try:
                    return datetime.strptime(s, fmt)
                except ValueError:
                    continue
        return None

    def _has_unexpired_jwt(self, jwt_token: Optional[str]) -> bool:
        if not jwt_token or not str(jwt_token).strip():
            return False
        exp = float(getattr(self, "token_expiry", 0.0) or 0.0)
        if exp > 0 and time.time() >= exp:
            return False
        return True

    def get_last_price(self, symbol: str) -> float:
        self.logger.debug(f"Requesting LTP for {symbol} via Paytm Money...")
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, '_use_fallback_only', False) or not self._has_unexpired_jwt(jwt_token):
            return self.fallback.get_last_price(symbol) if self.fallback else 0.0
            
        security_id = self._get_security_id(symbol)
        
        if self.ws_cache and self.ws_cache.is_connected():
            cached_ltp = self.ws_cache.get_cached_ltp(security_id)
            if cached_ltp > 0:
                return cached_ltp
                
        if security_id in self._rest_cache:
            return self._rest_cache[security_id].get('price', 0.0)
                
        if security_id in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "13", "25", "27", "442"]:
            pref_string = f"NSE:{security_id}:INDEX"
        else:
            pref_string = f"NSE:{security_id}:EQUITY"
        url = f"{self.BASE_URL_DATA}/v1/price/live"
        
        params = {
            "mode": "LTP",
            "pref": pref_string
        }
        
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, '_use_fallback_only', False) or not self._has_unexpired_jwt(jwt_token):
            return self.fallback.get_last_price(symbol) if self.fallback else 0.0

        headers = {
            "x-jwt-token": str(jwt_token).strip()
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            
            # Handle token expiry
            if response.status_code == 401:
                self.logger.warning("Token expired. Attempting refresh...")
                self._refresh_token()
                jwt_token = self.read_access_token if self.read_access_token else self.access_token
                headers["x-jwt-token"] = jwt_token if jwt_token else ""
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                
            response.raise_for_status()
            data = response.json()
            
            items = data.get('data', [])
            if not items:
                self.logger.warning(f"No LTP data found for {symbol} in response: {data}")
                return 0.0
                
            first_item = items[0]
            raw_ltt = first_item.get("last_trade_time") or first_item.get("last_update_time")
            converted_ltt = self.convert_paytm_epoch(raw_ltt)
            self._last_quote_meta[symbol] = {
                "raw_last_trade_time": raw_ltt,
                "last_trade_time": converted_ltt,
                "last_trade_datetime": datetime.fromtimestamp(converted_ltt, tz=IST_TZ).isoformat() if converted_ltt else None,
            }
            # Extract LTP from the payload
            ltp = first_item.get('last_price', first_item.get('lastPrice', first_item.get('ltp', 0.0)))
            return float(ltp)
            
        except Exception as e:
            self.logger.error(f"Failed to fetch LTP for {symbol}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
            return 0.0

    def test_connection(self) -> str:
        """Tests API directly and returns the exact error string if it fails"""
        url = f"{self.BASE_URL_DATA}/v1/price/live"
        params = {"mode": "LTP", "pref": "NSE:RELIANCE:EQUITY"}
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        headers = {"x-jwt-token": jwt_token if jwt_token else ""}
        
        response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        if response.status_code != 200:
            return f"HTTP {response.status_code}: {response.text}"
            
        data = response.json()
        if not data.get('data'):
            return f"Empty data. Response: {data}"
            
        return "SUCCESS"

    @staticmethod
    def _resolve_date_range(period: str, interval: str = "1d") -> Tuple[str, str, int]:
        """Resolve period string into (fromDate YYYY-MM-DD, toDate YYYY-MM-DD, lookback_days)."""
        period_map = {
            "1d": 2,
            "2d": 4,
            "5d": 7,
            "1wk": 7,
            "1mo": 30,
            "3mo": 85,
            "6mo": 89,
            "1y": 89,
            "2y": 89,
            "5y": 89,
        }
        days = min(89, period_map.get(str(period or "3mo").strip().lower(), 85))

        # SPRINT-185 STEP 44: Cap minute intervals to 5 calendar days to satisfy Paytm's 7-day limit
        norm_inv = str(interval or "1d").strip().lower()
        if norm_inv in ["1m", "5m", "15m", "30m", "60m", "1h", "minute"]:
            days = min(days, 5)

        now_ist = datetime.now(IST_TZ)
        past_dt = now_ist - timedelta(days=days)
        # Official Paytm API requires toDate <= fromDate (fromDate = newer/end date, toDate = older/start date)
        return now_ist.strftime("%Y-%m-%d"), past_dt.strftime("%Y-%m-%d"), days

    @staticmethod
    def _map_historical_interval(interval: str) -> Optional[Tuple[str, int]]:
        """
        Map caller interval to (Paytm API interval, aggregation_factor).
        Official Paytm price-charts/sym supports MINUTE and DAY intervals.
        """
        norm = str(interval or "1d").strip().lower()
        mapping = {
            "1m": ("MINUTE", 1),
            "5m": ("MINUTE", 5),
            "15m": ("MINUTE", 15),
            "30m": ("MINUTE", 30),
            "60m": ("MINUTE", 60),
            "1h": ("MINUTE", 60),
            "1d": ("DAY", 1),
            "1wk": ("DAY", 5),
            "1mo": ("DAY", 21),
        }
        return mapping.get(norm)

    @staticmethod
    def _aggregate_candles(candles: List[OHLCV], factor: int) -> List[OHLCV]:
        if factor <= 1:
            return candles
        if len(candles) < factor:
            return []
        aggregated: List[OHLCV] = []
        for idx in range(0, len(candles) - factor + 1, factor):
            chunk = candles[idx:idx + factor]
            aggregated.append(
                OHLCV(
                    timestamp=chunk[-1].timestamp,
                    open=chunk[0].open,
                    high=max(c.high for c in chunk),
                    low=min(c.low for c in chunk),
                    close=chunk[-1].close,
                    volume=int(sum(c.volume for c in chunk)),
                )
            )
        return aggregated

    def _fetch_paytm_historical_ohlcv(self, symbol: str, interval: str, period: str) -> Tuple[List[OHLCV], Dict[str, Any]]:
        """
        Calls the official Paytm Money Historical Price Chart endpoint:
        POST https://developer.paytmmoney.com/data/v1/price-charts/sym
        Validates response status, candle structure, OHLCV bounds, chronological order, and recency.
        """
        meta: Dict[str, Any] = {
            "endpoint": f"{self.BASE_URL_DATA}/v1/price-charts/sym",
            "method": "POST",
            "symbol": symbol,
            "interval": interval,
            "period": period,
        }
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, "_use_fallback_only", False):
            meta["error"] = "provider_not_connected"
            return [], meta
        if not self._has_unexpired_jwt(jwt_token):
            meta["error"] = "jwt_missing_or_expired"
            return [], meta

        interval_spec = self._map_historical_interval(interval)
        if not interval_spec:
            meta["error"] = f"unsupported_interval:{interval}"
            return [], meta
        paytm_interval, agg_factor = interval_spec

        clean_sym = str(symbol or "").strip().upper().replace(".NS", "").replace(".BO", "")
        security_id = self._get_security_id(symbol)
        is_index = clean_sym in self._INDEX_SECURITY_IDS or security_id in ["13", "25", "27", "442"]
        # Official Paytm historical contract requires instType "ES" (Equity Spot) and trading symbol
        inst_type = "INDEX" if is_index else "ES"
        from_date, to_date, lookback_days = self._resolve_date_range(period, interval=interval)

        payload = {
            "cont": "false",
            "exchange": "NSE",
            "fromDate": from_date,
            "instType": inst_type,
            "interval": paytm_interval,
            "symbol": clean_sym,
            "toDate": to_date,
        }
        meta["request_payload"] = payload
        headers = {
            "x-jwt-token": str(jwt_token).strip(),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "openapi-client-src": "sdk",
        }

        try:
            response = requests.post(meta["endpoint"], json=payload, headers=headers, timeout=self.timeout)
            meta["http_status"] = response.status_code
            if response.status_code != 200:
                meta["error"] = f"HTTP_{response.status_code}"
                return [], meta
            body = response.json()
        except Exception as e:
            meta["error"] = f"request_error:{type(e).__name__}"
            return [], meta

        raw_candles = body.get("data") if isinstance(body, dict) else None
        if not isinstance(raw_candles, list) or not raw_candles:
            meta["error"] = "empty_or_malformed_data"
            return [], meta

        parsed: List[OHLCV] = []
        for item in raw_candles:
            try:
                if isinstance(item, (list, tuple)) and len(item) >= 5:
                    ts = self._parse_candle_timestamp(item[0])
                    o, h, l, c = float(item[1]), float(item[2]), float(item[3]), float(item[4])
                    v = int(float(item[5])) if len(item) >= 6 and item[5] is not None else 0
                elif isinstance(item, dict):
                    raw_t = item.get("timestamp") or item.get("time") or item.get("date") or item.get("start_time")
                    ts = self._parse_candle_timestamp(raw_t)
                    o = float(item.get("open", 0.0))
                    h = float(item.get("high", 0.0))
                    l = float(item.get("low", 0.0))
                    c = float(item.get("close", 0.0))
                    v = int(float(item.get("volume", item.get("volume_traded", 0)) or 0))
                else:
                    continue

                if ts is None or o <= 0 or h <= 0 or l <= 0 or c <= 0 or v < 0:
                    continue
                if h < max(o, c, l) or l > min(o, c, h):
                    continue
                parsed.append(OHLCV(timestamp=ts, open=o, high=h, low=l, close=c, volume=v))
            except (ValueError, TypeError):
                continue

        if not parsed:
            meta["error"] = "no_valid_candles_after_validation"
            return [], meta

        parsed.sort(key=lambda bar: bar.timestamp)
        if agg_factor > 1:
            parsed = self._aggregate_candles(parsed, agg_factor)
            if not parsed:
                meta["error"] = f"insufficient_candles_for_aggregation:{agg_factor}"
                return [], meta

        # Verify newest candle is within the requested historical window and not stale (>7 days old)
        now_naive_ist = datetime.now(IST_TZ).replace(tzinfo=None)
        start_naive = datetime.strptime(to_date, "%Y-%m-%d")
        newest_ts = parsed[-1].timestamp
        if newest_ts < start_naive or (now_naive_ist - newest_ts).days > max(7, lookback_days):
            meta["error"] = f"stale_candles:newest={newest_ts.isoformat()}"
            return [], meta

        meta["candle_count"] = len(parsed)
        meta["newest_candle_timestamp"] = newest_ts.isoformat()
        return parsed, meta

    def get_ohlcv(self, symbol: str, interval: str = "1d", period: str = "3mo") -> List[OHLCV]:
        candles, meta = self._fetch_paytm_historical_ohlcv(symbol, interval=interval, period=period)
        if candles:
            self.stats["success"] = int(self.stats.get("success", 0)) + 1
            self.last_ohlcv_status[symbol] = {
                "provider": "PaytmMoney",
                "fallback_used": False,
                "http_status": meta.get("http_status", 200),
                "candle_count": len(candles),
                "newest_candle_timestamp": meta.get("newest_candle_timestamp"),
            }
            return candles

        # Explicit and truthful Yahoo Finance fallback
        self.stats["fallback_count"] = int(self.stats.get("fallback_count", 0)) + 1
        reason = meta.get("error", "paytm_historical_unavailable")
        self.logger.info(
            f"Paytm historical OHLCV unavailable for {symbol} ({interval}, {period}) [{reason}]. Using Yahoo Finance fallback."
        )
        fb_candles = self.fallback.get_ohlcv(symbol, interval=interval, period=period) if self.fallback else []
        newest_fb_ts = fb_candles[-1].timestamp.isoformat() if fb_candles else None
        self.last_ohlcv_status[symbol] = {
            "provider": "YahooFinance (Fallback)",
            "fallback_used": True,
            "paytm_error": reason,
            "http_status": meta.get("http_status"),
            "candle_count": len(fb_candles),
            "newest_candle_timestamp": newest_fb_ts,
        }
        return fb_candles
        
    def pre_cache(self, symbols: List[str], interval: str, period: str):
        if hasattr(self.fallback, 'pre_cache'):
            self.fallback.pre_cache(symbols, interval, period)
            
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, '_use_fallback_only', False) or not jwt_token:
            return
            
        security_ids = [self._get_security_id(s) for s in symbols]
        
        if self.ws_cache and self.ws_cache.is_connected():
            self.ws_cache.subscribe(security_ids)
            
        # Bulk fetch from REST to populate our internal cache
        try:
            self.logger.info(f"Bulk fetching live quotes for {len(security_ids)} symbols from Paytm API")
            url = f"{self.BASE_URL_DATA}/v1/price/live"
            jwt_token = self.read_access_token if self.read_access_token else self.access_token
            headers = {"x-jwt-token": jwt_token if jwt_token else ""}
            
            chunk_size = 40
            for i in range(0, len(security_ids), chunk_size):
                chunk = security_ids[i:i+chunk_size]
                prefs = []
                for sec_id in chunk:
                    self._rest_cache[sec_id] = {'price': 0.0, 'volume': 0}
                    if sec_id in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "13", "25", "27", "442"]:
                        prefs.append(f"NSE:{sec_id}:INDEX")
                    else:
                        prefs.append(f"NSE:{sec_id}:EQUITY")
                        
                params = {"mode": "QUOTE", "pref": ",".join(prefs)}
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                
                if response.status_code == 401:
                    self._refresh_token()
                    jwt_token = self.read_access_token if self.read_access_token else self.access_token
                    headers["x-jwt-token"] = jwt_token if jwt_token else ""
                    response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                    
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('data', []):
                        sec = str(item.get('security_id', ''))
                        if sec:
                            ltp = item.get('last_price', item.get('lastPrice', item.get('ltp', 0.0)))
                            vol = item.get('volume_traded', item.get('volume', item.get('traded_volume', 0.0)))
                            self._rest_cache[sec] = {'price': float(ltp), 'volume': int(vol or 0)}
        except Exception as e:
            self.logger.warning(f"Failed to bulk fetch from Paytm API: {e}")

    def get_volume(self, symbol: str) -> int:
        self.logger.debug(f"Requesting Volume for {symbol} via Paytm Money...")
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, '_use_fallback_only', False) or not jwt_token:
            return self.fallback.get_volume(symbol) if self.fallback else 0
            
        security_id = self._get_security_id(symbol)
        
        if self.ws_cache and self.ws_cache.is_connected():
            cached_vol = self.ws_cache.get_cached_vol(security_id)
            if cached_vol > 0:
                return cached_vol
                
        if security_id in self._rest_cache:
            return self._rest_cache[security_id].get('volume', 0)
        
        if security_id in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "13", "25", "27", "442"]:
            pref_string = f"NSE:{security_id}:INDEX"
        else:
            pref_string = f"NSE:{security_id}:EQUITY"
        url = f"{self.BASE_URL_DATA}/v1/price/live"
        params = {
            "mode": "QUOTE",
            "pref": pref_string
        }
        
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, '_use_fallback_only', False) or not jwt_token or not str(jwt_token).strip():
            return self.fallback.get_volume(symbol) if self.fallback else 0

        headers = {"x-jwt-token": str(jwt_token).strip()}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            if response.status_code == 401:
                self._refresh_token()
                jwt_token = self.read_access_token if self.read_access_token else self.access_token
                headers["x-jwt-token"] = jwt_token if jwt_token else ""
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                
            response.raise_for_status()
            data = response.json()
            items = data.get('data', [])
            if not items: return 0
            
            first_item = items[0]
            vol = first_item.get(
                "volume_traded",
                first_item.get(
                    "volume",
                    first_item.get("traded_volume", 0)
                )
            )
            return int(vol or 0)
        except Exception as e:
            self.logger.error(f"Failed to fetch volume for {symbol}: {e}")
            return self.fallback.get_volume(symbol) if self.fallback else 0

    def get_market_status(self) -> MarketStatus:
        self.logger.debug("Delegating Market Status to Yahoo fallback.")
        return self.fallback.get_market_status()
        
    def get_option_chain(self, symbol: str, expiry: str = None) -> Dict[str, Any]:
        """Fetch Option Chain from Paytm Money Open API"""
        self.logger.debug(f"Requesting Option Chain for {symbol} (Expiry: {expiry})")
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        if not self.is_connected() or getattr(self, '_use_fallback_only', False) or not jwt_token:
            return {}
            
        cache_key = f"{symbol}_{expiry}"
        if cache_key in self._option_chain_cache:
            timestamp, cached_data = self._option_chain_cache[cache_key]
            if time.time() - timestamp < self.OPTION_CHAIN_CACHE_TTL:
                self.logger.debug(f"Returning valid cached option chain for {symbol} (Expiry: {expiry})")
                return cached_data
                
        clean_symbol = symbol.replace('.NS', '')
        url = f"{self.BASE_URL_DATA}/fno/v1/option-chain"
        
        params = {"symbol": clean_symbol}
        if expiry:
            params["expiry"] = expiry
            
        jwt_token = self.read_access_token if self.read_access_token else self.access_token
        headers = {"x-jwt-token": jwt_token if jwt_token else ""}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            if response.status_code == 401:
                self._refresh_token()
                jwt_token = self.read_access_token if self.read_access_token else self.access_token
                headers["x-jwt-token"] = jwt_token if jwt_token else ""
                response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                
            response.raise_for_status()
            data = response.json()
            self._option_chain_cache[cache_key] = (time.time(), data)
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch Option Chain for {symbol}: {e}")
            return {}


    # ═══════════════════════════════════════════════════════════════════════════════
    # F&O DATA METHODS - Added for RAHUUL_RADAR F&O Integration
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_fno_summary(self, symbol: str):
        """Calculate F&O summary metrics from option chain."""
        self.logger.debug(f"Fetching F&O summary for {symbol}")

        try:
            chain_data = self.get_option_chain(symbol)

            if not chain_data or 'data' not in chain_data:
                return self._default_fno_summary()

            data = chain_data['data']
            call_options = data.get('call_options', [])
            put_options = data.get('put_options', [])
            underlying_price = data.get('underlying_price', 0)

            total_call_oi = sum(opt.get('oi', 0) for opt in call_options)
            total_put_oi = sum(opt.get('oi', 0) for opt in put_options)
            total_oi = total_call_oi + total_put_oi

            call_oi_change = sum(opt.get('oi_change', 0) for opt in call_options)
            put_oi_change = sum(opt.get('oi_change', 0) for opt in put_options)

            prev_call_oi = total_call_oi - call_oi_change
            prev_put_oi = total_put_oi - put_oi_change
            prev_total = prev_call_oi + prev_put_oi

            oi_change_pct = ((total_oi - prev_total) / prev_total * 100) if prev_total > 0 else 0

            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0

            # Max Pain
            strikes = {}
            for opt in call_options + put_options:
                strike = opt.get('strike_price', 0)
                oi = opt.get('oi', 0)
                if strike > 0:
                    strikes[strike] = strikes.get(strike, 0) + oi

            max_pain = max(strikes.items(), key=lambda x: x[1])[0] if strikes else 0

            result = {
                'total_call_oi': total_call_oi,
                'total_put_oi': total_put_oi,
                'pcr': round(pcr, 2),
                'max_pain': max_pain,
                'oi_change_pct': round(oi_change_pct, 2),
                'total_oi': total_oi,
                'underlying_price': underlying_price,
                'call_oi_change': call_oi_change,
                'put_oi_change': put_oi_change
            }

            self.logger.debug(f"F&O Summary for {symbol}: PCR={result['pcr']}, OIΔ={result['oi_change_pct']}%")
            return result

        except Exception as e:
            self.logger.error(f"Failed to get F&O summary for {symbol}: {e}")
            return self._default_fno_summary()

    def _default_fno_summary(self):
        """Return default F&O values when data unavailable"""
        return {
            'total_call_oi': 0,
            'total_put_oi': 0,
            'pcr': 1.0,
            'max_pain': 0,
            'oi_change_pct': 0,
            'total_oi': 0,
            'underlying_price': 0,
            'call_oi_change': 0,
            'put_oi_change': 0
        }

    def get_historical(self, symbol: str, interval: str = "1d", period: str = "1mo") -> Any:
        """Fetch historical OHLCV via Paytm price-charts/sym with explicit Yahoo fallback."""
        return self.get_ohlcv(symbol, interval=interval, period=period)

    def get_intraday(self, symbol: str, interval: str = "15m", period: str = "5d") -> Any:
        """Fetch intraday OHLCV via Paytm price-charts/sym with explicit Yahoo fallback."""
        return self.get_ohlcv(symbol, interval=interval, period=period)

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        ltp = self.get_last_price(symbol)
        vol = self.get_volume(symbol)
        q_meta = self._last_quote_meta.get(symbol, {})
        ltt = q_meta.get("last_trade_time")
        now_ts = int(time.time())
        is_stale = True if (ltt is None or (now_ts - int(ltt)) > 900) else False
        return {
            "symbol": symbol,
            "last_price": ltp,
            "volume": vol,
            "provider": "PaytmMoney" if ltt is not None else "YahooFinance (Fallback)",
            "fallback_used": ltt is None,
            "raw_last_trade_time": q_meta.get("raw_last_trade_time"),
            "last_trade_time": ltt,
            "last_trade_datetime": q_meta.get("last_trade_datetime"),
            "is_stale": is_stale,
        }

    def health(self) -> Dict[str, Any]:
        from market.provider_health_manager import ProviderHealthManager
        return ProviderHealthManager.get_instance().providers.get("PaytmMoney", {"status": "HEALTHY"})

    def latency(self) -> float:
        return 18.0
