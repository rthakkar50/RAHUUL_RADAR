import requests
import time
import logging
import os

# --- LOGGING SETUP ---
from utils.paths import get_logs_dir

log_dir = get_logs_dir()
log_file = log_dir / "nse_connection.log"

logger = logging.getLogger("NSEDataLayer")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

class HeaderManager:
    @staticmethod
    def get_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

class CookieManager:
    def __init__(self, session):
        self.session = session

    def refresh_cookies(self):
        logger.info("CookieManager: Refreshing cookies from nseindia.com...")
        try:
            res = self.session.get("https://www.nseindia.com", timeout=15)
            logger.info(f"CookieManager: Response Code {res.status_code}")
            logger.debug(f"CookieManager: Generated Cookies: {self.session.cookies.get_dict()}")
            return res.status_code in [200, 403, 404] # Sometimes base returns 403 but sets cookies
        except Exception as e:
            logger.error(f"CookieManager: Error {e}")
            return False

class CacheManager:
    def __init__(self):
        self.cache = {}

    def set(self, key, data):
        self.cache[key] = data
        
    def get(self, key):
        return self.cache.get(key)

class RetryManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def execute_with_retry(self, func, *args, **kwargs):
        for attempt in range(1, self.max_retries + 1):
            try:
                res = func(*args, **kwargs)
                if res.status_code == 200:
                    return res
                elif res.status_code in [401, 403, 404, 429, 500]:
                    logger.warning(f"RetryManager: Attempt {attempt} failed with HTTP {res.status_code}")
            except Exception as e:
                logger.error(f"RetryManager: Attempt {attempt} error: {e}")
                
            backoff = 2 ** attempt
            logger.info(f"RetryManager: Sleeping for {backoff} seconds before retry.")
            time.sleep(backoff)
        return None

class SessionManager:
    def __init__(self):
        self.session = None
        self.cookie_manager = None
        self.renew_session()
        
    def get_session(self):
        return self.session
        
    def renew_session(self):
        logger.info("SessionManager: Creating new session...")
        self.session = requests.Session()
        self.session.headers.update(HeaderManager.get_headers())
        self.cookie_manager = CookieManager(self.session)
        self.cookie_manager.refresh_cookies()

class NSEProvider:
    def __init__(self):
        logger.info("NSEProvider: Initializing Professional Data Layer.")
        self.session_manager = SessionManager()
        self.cache_manager = CacheManager()
        self.retry_manager = RetryManager(max_retries=3)
        
    def fetch_data(self, symbol="NIFTY"):
        """Compatible entry point for UI."""
        return self.fetch_option_chain(symbol)
        
    def fetch_option_chain(self, symbol="NIFTY"):
        if symbol in ["SENSEX", "BANKEX"]:
            logger.warning(f"NSEProvider: {symbol} is a BSE index. Returning None.")
            return None
            
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        
        def _make_request():
            session = self.session_manager.get_session()
            logger.info(f"NSEProvider: GET {url}")
            return session.get(url, timeout=15)
            
        res = self.retry_manager.execute_with_retry(_make_request)
        
        if not res or res.status_code != 200:
            logger.warning("NSEProvider: Renewing session for final fallback attempt...")
            self.session_manager.renew_session()
            res = self.retry_manager.execute_with_retry(_make_request)
            
        if res and res.status_code == 200:
            try:
                data = res.json()
                self.cache_manager.set(f"oc_{symbol}", data)
                logger.info(f"NSEProvider: Successfully parsed JSON for {symbol}.")
                return data
            except Exception as e:
                logger.error(f"NSEProvider: JSON parse error: {e}")
                
        logger.error(f"NSEProvider: Final failure for {symbol}. Returning cached data if available.")
        return self.cache_manager.get(f"oc_{symbol}")
