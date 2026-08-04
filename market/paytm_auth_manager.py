"""
PaytmAuthManager: Production-grade Paytm authentication and token management module.
Handles credential loading, token validation, automatic refresh, and Telegram notifications.
"""
import os
import json
import time
import logging
import requests
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("PaytmAuthManager")

class PaytmAuthManager:
    _instance = None

    BASE_URL_ACCOUNTS = "https://developer.paytmmoney.com/accounts"
    DEFAULT_HTTP_TIMEOUT = 5.0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.api_key: Optional[str] = None
        self.api_secret: Optional[str] = None
        self.request_token: Optional[str] = None
        self.access_token: Optional[str] = None
        self.read_access_token: Optional[str] = None
        self.public_access_token: Optional[str] = None
        self.token_expiry: float = 0.0
        self.last_refresh_time: float = 0.0
        self.last_refresh_status: str = "NEVER_ATTEMPTED"
        
        self.load_credentials()

    def load_credentials(self) -> None:
        """Load API keys and tokens from environment variables or config.json."""
        self.api_key = os.environ.get("PAYTM_API_KEY")
        self.api_secret = os.environ.get("PAYTM_API_SECRET")
        self.request_token = os.environ.get("PAYTM_REQUEST_TOKEN")
        self.access_token = os.environ.get("PAYTM_ACCESS_TOKEN")
        self.read_access_token = os.environ.get("PAYTM_READ_ACCESS_TOKEN")
        self.public_access_token = os.environ.get("PAYTM_PUBLIC_ACCESS_TOKEN")

        config_path = os.path.join(os.getcwd(), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cdata = json.load(f)
                    paytm_cfg = cdata.get("paytm", {})
                    if not self.api_key:
                        self.api_key = paytm_cfg.get("api_key")
                    if not self.api_secret:
                        self.api_secret = paytm_cfg.get("api_secret_key")
                    if not self.request_token:
                        self.request_token = paytm_cfg.get("request_token")
                    if not self.access_token:
                        self.access_token = paytm_cfg.get("access_token")
                    if not self.read_access_token:
                        self.read_access_token = paytm_cfg.get("read_access_token")
                    if not self.public_access_token:
                        self.public_access_token = paytm_cfg.get("public_access_token")
                    self.token_expiry = float(paytm_cfg.get("token_expiry", 0.0))
            except Exception as e:
                logger.warning(f"Error reading config.json in PaytmAuthManager: {e}")

    def save_tokens_to_config(self) -> None:
        """Save active access tokens to config.json."""
        config_path = os.path.join(os.getcwd(), "config.json")
        try:
            cdata = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    cdata = json.load(f)
            
            if "paytm" not in cdata:
                cdata["paytm"] = {}
                
            cdata["paytm"]["access_token"] = self.access_token or ""
            cdata["paytm"]["read_access_token"] = self.read_access_token or ""
            cdata["paytm"]["public_access_token"] = self.public_access_token or ""
            cdata["paytm"]["token_expiry"] = self.token_expiry
            
            with open(config_path, "w") as f:
                json.dump(cdata, f, indent=4)
            logger.info("Saved updated Paytm tokens to config.json")
        except Exception as e:
            logger.warning(f"Failed to save tokens to config.json: {e}")

    def is_authenticated(self) -> bool:
        """Returns True if a valid non-empty access token is loaded and not expired."""
        jwt = self.get_valid_jwt()
        if not jwt:
            return False
        if self.token_expiry > 0 and time.time() > self.token_expiry:
            logger.info("Paytm Token Expired")
            return False
        return True

    def get_valid_jwt(self) -> Optional[str]:
        """Returns active JWT token if non-empty and non-placeholder."""
        token = self.read_access_token or self.access_token
        if token and str(token).strip() and not str(token).startswith("MOCK") and str(token) != "YOUR_PAYTM_ACCESS_TOKEN":
            return str(token).strip()
        return None

    def refresh_token(self) -> Tuple[bool, str]:
        """Performs token refresh / authentication via Paytm API."""
        if not self.api_key or not self.api_secret or not self.request_token:
            msg = "Paytm Login Required: Missing API Key, Secret, or Request Token."
            logger.warning(msg)
            self.last_refresh_status = "FAILED_MISSING_CREDENTIALS"
            self.notify_telegram_login_required()
            return False, msg

        url = f"{self.BASE_URL_ACCOUNTS}/v2/gettoken"
        payload = {
            "apiKey": self.api_key,
            "api_key": self.api_key,
            "apiSecretKey": self.api_secret,
            "api_secret_key": self.api_secret,
            "requestToken": self.request_token,
            "request_token": self.request_token
        }
        headers = {'Content-Type': 'application/json'}

        try:
            logger.info("Attempting Paytm token refresh...")
            resp = requests.post(url, json=payload, headers=headers, timeout=self.DEFAULT_HTTP_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                tdata = data.get('data', data) if isinstance(data, dict) else data
                acc_tok = tdata.get('access_token')
                read_tok = tdata.get('read_access_token')
                pub_tok = tdata.get('public_access_token')

                if acc_tok:
                    self.access_token = acc_tok
                    self.read_access_token = read_tok or acc_tok
                    self.public_access_token = pub_tok
                    self.token_expiry = time.time() + (24 * 3600)  # 24 hour expiry
                    self.last_refresh_time = time.time()
                    self.last_refresh_status = "SUCCESS"
                    self.save_tokens_to_config()
                    logger.info("Paytm Login Success: Token Refreshed successfully.")
                    return True, "Token refreshed successfully"
                else:
                    logger.warning(f"Paytm Token refresh returned empty data: {data}")
            
            logger.warning(f"Token Refreshed failed: HTTP {resp.status_code} - {resp.text}")
            self.last_refresh_status = f"FAILED_HTTP_{resp.status_code}"
        except Exception as e:
            logger.warning(f"Paytm Token refresh network exception: {e}")
            self.last_refresh_status = f"FAILED_EXCEPTION_{e}"

        logger.info("Fallback to Yahoo")
        self.notify_telegram_login_required()
        return False, "Paytm Login Required: Refresh failed. Fallback to Yahoo active."

    def notify_telegram_login_required(self) -> None:
        """Sends Telegram notification when Paytm Login is required."""
        try:
            from core.telegram_service import TelegramService
            svc = TelegramService.get_instance()
            cfg = svc.get_config()
            tok = cfg.get("telegram_bot_token")
            chat_id = cfg.get("telegram_authorized_chat_id")
            if tok and chat_id:
                msg = (
                    "🔑 *Paytm Login Required*\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• *Status*: Unauthenticated / Token Expired\n"
                    "• *Action*: Automatic fallback to Yahoo active.\n"
                    "• *Command*: Send `/refreshtoken` or update `request_token`."
                )
                svc.send_message(tok, chat_id, msg)
        except Exception as e:
            logger.warning(f"Failed to send Telegram login alert: {e}")

    def get_auth_status(self) -> Dict[str, Any]:
        """Generates summary dict for status report commands."""
        auth = self.is_authenticated()
        exp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.token_expiry)) if self.token_expiry > 0 else "N/A"
        ref_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.last_refresh_time)) if self.last_refresh_time > 0 else "N/A"
        return {
            "provider": "Paytm Money Open API",
            "authenticated": auth,
            "login_status": "Authenticated" if auth else "Login Required",
            "token_expiry": exp_str,
            "last_refresh_time": ref_str,
            "refresh_status": self.last_refresh_status,
            "fallback_active": not auth
        }
