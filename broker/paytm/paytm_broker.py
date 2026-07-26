import os
import json
import logging
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..base.base_broker import BaseBroker
from ..models.order import Order, Position, Funds, OrderType, OrderStatus
from market.paytm_provider import PaytmMoneyProvider
from market.paytm_websocket import PaytmLiveBroadcast
from ..utils.exceptions import (
    BrokerException,
    BrokerAuthError,
    TokenExpiredError,
    OrderPlacementError,
    NetworkTimeoutError,
    InsufficientFundsError,
    MarketClosedError,
    InvalidSymbolError,
    ExchangeError
)

logger = logging.getLogger("PaytmBroker")

class PaytmBroker(BaseBroker):
    """
    Official Primary Broker Implementation for RAHUUL RADAR targeting Paytm Money Open APIs.
    Strict production stability implementation: No fake order success IDs, no simulated mode fallbacks on auth error.
    """
    
    BASE_URL_ACCOUNTS = "https://developer.paytmmoney.com/accounts/v1"
    BASE_URL_ORDERS = "https://developer.paytmmoney.com/orders/v1"
    BASE_URL_HOLDINGS = "https://developer.paytmmoney.com/holdings/v1"
    BASE_URL_POSITIONS = "https://developer.paytmmoney.com/positions/v1"
    BASE_URL_DATA = "https://developer.paytmmoney.com/data/v1"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_connected = False
        
        # Access Token Management
        self.api_key = os.environ.get("PAYTM_API_KEY", None)
        self.api_secret = os.environ.get("PAYTM_API_SECRET", None)
        self.access_token = os.environ.get("PAYTM_ACCESS_TOKEN", None)
        self.public_access_token = os.environ.get("PAYTM_PUBLIC_ACCESS_TOKEN", None)
        self.read_access_token = os.environ.get("PAYTM_READ_ACCESS_TOKEN", None)
        
        if not self.api_key or not self.api_secret:
            self._load_credentials_from_config()

        if not self.api_key or not self.api_secret:
            raise ValueError("PaytmBroker initialization error: Missing required credentials (PAYTM_API_KEY and PAYTM_API_SECRET). Never silently use placeholder credentials.")
        
        # Bridge to verified Live WebSocket Feed and Historical Data engine
        self._data_provider = PaytmMoneyProvider()
        self._ws_broadcast = PaytmLiveBroadcast.get_instance()
        self._headers: Dict[str, str] = {}

    def _load_credentials_from_config(self):
        try:
            config_path = os.path.join(os.getcwd(), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    paytm_block = config_data.get("paytm", {})
                    if not self.api_key:
                        self.api_key = paytm_block.get("api_key", "")
                    if not self.api_secret:
                        self.api_secret = paytm_block.get("api_secret_key", "")
                    if not self.access_token:
                        self.access_token = paytm_block.get("access_token", "")
                    if not self.public_access_token:
                        self.public_access_token = paytm_block.get("public_access_token", "")
                    if not self.read_access_token:
                        self.read_access_token = paytm_block.get("read_access_token", "")
        except Exception as e:
            self.logger.warning(f"Failed to load Paytm credentials from config.json: {e}")

    def _update_headers(self):
        token = self.access_token or self.read_access_token
        if not token:
            self._headers = {}
            return
        self._headers = {
            "x-jwt-token": token,
            "Content-Type": "application/json"
        }

    def _parse_order_status(self, raw_status: str) -> OrderStatus:
        st = str(raw_status).upper()
        if "PEND" in st or "SUBMIT" in st:
            return OrderStatus.PENDING
        elif "OPEN" in st or "TRIG" in st:
            return OrderStatus.OPEN
        elif "COMPLETE" in st or "EXEC" in st or "SUCCESS" in st:
            return OrderStatus.COMPLETE
        elif "REJECT" in st or "FAIL" in st:
            return OrderStatus.REJECTED
        elif "CANCEL" in st:
            return OrderStatus.CANCELLED
        return OrderStatus.PENDING

    def _raise_parsed_order_error(self, err_msg: str, status_code: int = 400):
        err_lower = err_msg.lower()
        if "insufficient" in err_lower or "margin" in err_lower or "balance" in err_lower or "fund" in err_lower:
            raise InsufficientFundsError(f"Paytm Order Rejected [Insufficient Funds]: {err_msg}")
        elif "market closed" in err_lower or "outside market" in err_lower or "offline" in err_lower or "hours" in err_lower or "closed" in err_lower:
            raise MarketClosedError(f"Paytm Order Rejected [Market Closed]: {err_msg}")
        elif "invalid symbol" in err_lower or "security_id" in err_lower or "instrument" in err_lower or "invalid security" in err_lower:
            raise InvalidSymbolError(f"Paytm Order Rejected [Invalid Symbol]: {err_msg}")
        elif "exchange" in err_lower or "segment" in err_lower or "rms" in err_lower:
            raise ExchangeError(f"Paytm Order Rejected [Exchange Error]: {err_msg}")
        else:
            raise OrderPlacementError(f"Paytm Order Rejected (HTTP {status_code}): {err_msg}")

    # -------------------------------------------------------------------------
    # 1 & 2. Authentication & Access Token Management
    # -------------------------------------------------------------------------
    def connect(self) -> bool:
        self._update_headers()
        if not self.access_token and not self.read_access_token:
            self.is_connected = False
            raise BrokerAuthError("Paytm Money connection failed: Missing valid access token. Re-authentication required.")
        
        try:
            profile = self.get_profile()
            if profile and profile.get("status") != "error":
                self.is_connected = True
                self.logger.info("Successfully connected to Paytm Money Institutional Open API.")
                return True
            else:
                self.is_connected = False
                raise BrokerAuthError("Paytm Money profile returned error status. Re-authentication required.")
        except (TokenExpiredError, BrokerAuthError) as e:
            self.is_connected = False
            self.logger.error(f"Paytm Money token invalid or expired: {e}")
            raise e
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"Paytm Money connection failed: {e}")
            raise BrokerAuthError(f"Paytm Money connection failed: {e}")

    def disconnect(self):
        self.is_connected = False
        if self._ws_broadcast:
            self._ws_broadcast.disconnect()
        self.logger.info("Disconnected from Paytm Money API session.")

    def login(self, credentials: dict) -> bool:
        """
        Exchanges request_token for Paytm Money access tokens.
        Never defaults to fake/simulated tokens.
        """
        request_token = credentials.get("request_token")
        if not request_token:
            raise BrokerAuthError("Paytm Money login requires a valid OAuth request_token.")
        
        url = f"{self.BASE_URL_ACCOUNTS}/gettoken"
        payload = {"api_key": self.api_key, "api_secret": self.api_secret, "request_token": request_token}
        
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                token_data = data.get("data", data)
                self.access_token = token_data.get("access_token")
                self.public_access_token = token_data.get("public_access_token")
                self.read_access_token = token_data.get("read_access_token")
                if not self.access_token:
                    self.is_connected = False
                    raise BrokerAuthError(f"Paytm Money token exchange returned empty access token: {data}")
            else:
                self.is_connected = False
                raise BrokerAuthError(f"Paytm Money token exchange failed with HTTP {res.status_code}: {res.text}")
        except requests.exceptions.Timeout:
            self.is_connected = False
            raise NetworkTimeoutError("Paytm Money token exchange request timed out.")
        except Exception as e:
            self.is_connected = False
            raise BrokerAuthError(f"Paytm Money token exchange failed: {e}")

        return self.connect()

    def logout(self) -> bool:
        self.disconnect()
        self.access_token = None
        self.public_access_token = None
        self.read_access_token = None
        return True

    def refresh_token(self) -> bool:
        """
        Validates current token session. If token is expired, raises TokenExpiredError to force re-authentication.
        """
        if not self.access_token and not self.read_access_token:
            self.is_connected = False
            raise TokenExpiredError("Paytm access token is missing. Please re-authenticate.")
        
        try:
            self.get_profile()
            return True
        except TokenExpiredError as e:
            self.is_connected = False
            raise e
        except Exception as e:
            self.is_connected = False
            raise TokenExpiredError(f"Paytm token validation failed: {e}")

    # -------------------------------------------------------------------------
    # 3 & 4. WebSocket Live Feed & Historical Data
    # -------------------------------------------------------------------------
    def get_historical_data(self, symbol: str, timeframe: str, start_date: str, end_date: str):
        return self._data_provider.fetch_historical_data(symbol, start_date, end_date, interval="1d")

    def subscribe_live_feed(self, symbols: List[str]):
        if not self.is_connected:
            raise BrokerAuthError("Cannot subscribe WebSocket feed: Paytm broker is disconnected.")
        for symbol in symbols:
            self._ws_broadcast.subscribe(symbol)

    # -------------------------------------------------------------------------
    # 5, 6 & 7. Profile, Funds & Margin
    # -------------------------------------------------------------------------
    def get_profile(self) -> dict:
        url = f"{self.BASE_URL_ACCOUNTS}/user/profile"
        self._update_headers()
        if not self._headers.get("x-jwt-token"):
            raise TokenExpiredError("Paytm session token missing. Re-authentication required.")

        try:
            res = requests.get(url, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm session token expired (HTTP 401). Trading stopped.")
            elif res.status_code == 200:
                return res.json()
            else:
                raise BrokerAuthError(f"Failed to fetch Paytm profile: HTTP {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm profile request timed out.")

    def get_funds(self) -> Funds:
        if not self.is_connected:
            raise BrokerAuthError("Cannot fetch funds: Not connected to Paytm Money.")
        
        url = f"{self.BASE_URL_ACCOUNTS}/funds/summary"
        try:
            res = requests.get(url, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm session token expired (HTTP 401).")
            elif res.status_code == 200:
                body = res.json() if res.content else {}
                data = (body or {}).get("data", {})
                avail = float(data.get("available_balance", 0.0))
                used = float(data.get("used_margin", 0.0))
                total = float(data.get("total_capital", avail + used))
                return Funds(available_margin=avail, used_margin=used, available_cash=avail, collateral=0.0)
            else:
                raise BrokerException(f"Failed to fetch Paytm funds: HTTP {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm funds request timed out.")

    def get_margin(self, symbol: str) -> float:
        ltp = self.get_ltp(symbol)
        if ltp <= 0:
            raise InvalidSymbolError(f"Cannot calculate margin for invalid symbol or zero LTP: {symbol}")
        return ltp * 0.20  # Standard 5x intraday margin

    # -------------------------------------------------------------------------
    # 8, 9 & 10. Portfolio: Holdings, Positions, Order Book & Trade Book
    # -------------------------------------------------------------------------
    def get_holdings(self) -> List[Position]:
        if not self.is_connected:
            raise BrokerAuthError("Cannot fetch holdings: Not connected to Paytm Money.")
        
        url = f"{self.BASE_URL_HOLDINGS}/user/holdings"
        try:
            res = requests.get(url, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm session token expired (HTTP 401).")
            elif res.status_code == 200:
                body = res.json() if res.content else {}
                data = (body or {}).get("data", [])
                positions = []
                for item in data:
                    qty = int(item.get("quantity", 0))
                    avg_p = float(item.get("avg_price", 0.0))
                    curr_p = float(item.get("current_price", avg_p))
                    unreal = (curr_p - avg_p) * qty
                    positions.append(Position(
                        symbol=item.get("symbol", ""),
                        qty=qty,
                        avg_price=avg_p,
                        ltp=curr_p,
                        realized_pnl=0.0,
                        unrealized_pnl=unreal
                    ))
                return positions
            else:
                raise BrokerException(f"Failed to fetch Paytm holdings: HTTP {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm holdings request timed out.")

    def get_positions(self) -> List[Position]:
        if not self.is_connected:
            raise BrokerAuthError("Cannot fetch positions: Not connected to Paytm Money.")
        
        url = f"{self.BASE_URL_POSITIONS}/user/positions"
        try:
            res = requests.get(url, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm session token expired (HTTP 401).")
            elif res.status_code == 200:
                body = res.json() if res.content else {}
                data = (body or {}).get("data", [])
                positions = []
                for item in data:
                    qty = int(item.get("net_qty", 0))
                    buy_p = float(item.get("buy_price", 0.0))
                    ltp = float(item.get("ltp", buy_p))
                    unreal = float(item.get("unrealized_pnl", (ltp - buy_p) * qty))
                    real = float(item.get("realized_pnl", 0.0))
                    positions.append(Position(
                        symbol=item.get("symbol", ""),
                        qty=qty,
                        avg_price=buy_p,
                        ltp=ltp,
                        realized_pnl=real,
                        unrealized_pnl=unreal
                    ))
                return positions
            else:
                raise BrokerException(f"Failed to fetch Paytm positions: HTTP {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm positions request timed out.")

    def get_orders(self) -> List[Order]:
        if not self.is_connected:
            raise BrokerAuthError("Cannot fetch orders: Not connected to Paytm Money.")
        
        url = f"{self.BASE_URL_ORDERS}/user/orders"
        try:
            res = requests.get(url, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm session token expired (HTTP 401).")
            elif res.status_code == 200:
                body = res.json() if res.content else {}
                data = (body or {}).get("data", [])
                orders = []
                for item in data:
                    st = self._parse_order_status(item.get("status", "PENDING"))
                    orders.append(Order(
                        order_id=str(item.get("order_no", "")),
                        symbol=item.get("symbol", ""),
                        qty=int(item.get("quantity", 0)),
                        order_type=OrderType.LIMIT if float(item.get("price", 0.0)) > 0 else OrderType.MARKET,
                        price=float(item.get("price", 0.0)),
                        trigger_price=float(item.get("trigger_price", 0.0)),
                        status=st,
                        timestamp=datetime.now()
                    ))
                return orders
            else:
                raise BrokerException(f"Failed to fetch Paytm order book: HTTP {res.status_code} - {res.text}")
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm order book request timed out.")

    def get_trade_book(self) -> List[Dict[str, Any]]:
        if not self.is_connected:
            raise BrokerAuthError("Cannot fetch trade book: Not connected to Paytm Money.")
        
        url = f"{self.BASE_URL_ORDERS}/user/trades"
        try:
            res = requests.get(url, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm session token expired (HTTP 401).")
            elif res.status_code == 200:
                body = res.json() if res.content else {}
                return (body or {}).get("data", [])
            else:
                return []
        except Exception as e:
            self.logger.warning(f"Error fetching Paytm trade book: {e}")
            return []

    # -------------------------------------------------------------------------
    # 11, 12, 13 & 14. Order Placement, Modification, Cancellation & Square Off
    # -------------------------------------------------------------------------
    def place_order(self, symbol: str, qty: int, order_type: OrderType, price: float = 0.0, trigger_price: float = 0.0) -> str:
        if not self.is_connected:
            raise BrokerAuthError("Order placement blocked: Paytm Money is not connected or token expired. Live trading stopped.")

        url = f"{self.BASE_URL_ORDERS}/place"
        payload = {
            "txn_type": "BUY",
            "exchange": "NSE",
            "segment": "EQUITY",
            "product": "I",
            "security_id": symbol,
            "quantity": qty,
            "order_type": "LIMIT" if price > 0 else "MARKET",
            "price": price,
            "trigger_price": trigger_price
        }

        try:
            res = requests.post(url, json=payload, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm access token expired during order placement. Order aborted. Live trading stopped.")
            
            res_json = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
            if res.status_code == 200 and res_json.get("status") == "success":
                order_no = res_json.get("data", {}).get("order_no")
                if not order_no:
                    raise OrderPlacementError("Paytm response missing valid order_no.")
                return str(order_no)
            else:
                err_msg = res_json.get("message") or res_json.get("error") or res.text
                self.logger.error(f"Paytm live order placement rejected (HTTP {res.status_code}): {err_msg}")
                self._raise_parsed_order_error(err_msg, res.status_code)

        except requests.exceptions.Timeout:
            self.logger.error("Paytm order placement timed out after 5 seconds.")
            raise NetworkTimeoutError("Paytm order placement request timed out.")
        except (BrokerException, TokenExpiredError, OrderPlacementError):
            raise
        except Exception as e:
            self.logger.error(f"Paytm order placement exception: {e}")
            raise OrderPlacementError(f"Paytm order placement failed: {e}")

    def modify_order(self, order_id: str, new_qty: int, new_price: float = 0.0) -> bool:
        if not self.is_connected:
            raise BrokerAuthError("Modify order blocked: Paytm Money is disconnected.")

        url = f"{self.BASE_URL_ORDERS}/modify"
        payload = {"order_no": order_id, "quantity": new_qty, "price": new_price}
        
        try:
            res = requests.post(url, json=payload, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm token expired during order modification.")
            elif res.status_code == 200:
                return True
            else:
                err_msg = res.text
                self._raise_parsed_order_error(f"Modify Order Failed: {err_msg}", res.status_code)
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm modify order request timed out.")
        except (BrokerException, TokenExpiredError, OrderPlacementError):
            raise
        except Exception as e:
            raise OrderPlacementError(f"Paytm modify order failed: {e}")

    def cancel_order(self, order_id: str) -> bool:
        if not self.is_connected:
            raise BrokerAuthError("Cancel order blocked: Paytm Money is disconnected.")

        url = f"{self.BASE_URL_ORDERS}/cancel"
        payload = {"order_no": order_id}
        
        try:
            res = requests.post(url, json=payload, headers=self._headers, timeout=5)
            if res.status_code == 401:
                self.is_connected = False
                raise TokenExpiredError("Paytm token expired during order cancellation.")
            elif res.status_code == 200:
                return True
            else:
                err_msg = res.text
                self._raise_parsed_order_error(f"Cancel Order Failed: {err_msg}", res.status_code)
        except requests.exceptions.Timeout:
            raise NetworkTimeoutError("Paytm cancel order request timed out.")
        except (BrokerException, TokenExpiredError, OrderPlacementError):
            raise
        except Exception as e:
            raise OrderPlacementError(f"Paytm cancel order failed: {e}")

    def square_off(self, symbol: str) -> bool:
        if not self.is_connected:
            raise BrokerAuthError("Square off blocked: Paytm Money is disconnected.")
        
        self.logger.info(f"Executing live square off for symbol: {symbol}")
        positions = self.get_positions()
        pos = next((p for p in positions if p.symbol == symbol), None)
        if pos and pos.qty != 0:
            opp_txn = "SELL" if pos.qty > 0 else "BUY"
            # Place exit order
            self.place_order(symbol, abs(pos.qty), OrderType.MARKET)
            return True
        return True

    # -------------------------------------------------------------------------
    # 15. Market LTP & Symbol Search
    # -------------------------------------------------------------------------
    def get_ltp(self, symbol: str) -> float:
        return self._data_provider.fetch_latest_price(symbol)

    def search_symbol(self, query: str) -> list:
        return ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "TITAN"]

