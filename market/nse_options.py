import requests
import time
import logging
import os
import json
from datetime import datetime

# Setup dedicated logger
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "option_chain.log")

logger = logging.getLogger("OptionChainManager")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Clear existing handlers if any
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class OptionChainDataManager:
    """
    Dedicated NSE Option Chain Data Engine.
    Handles Sessions, Cookies, Rate Limits, and Caching.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.cookies_set = False
        
        # Cache for Last Successful Data
        self.cache = {} # symbol -> data
        
        logger.info("OptionChainDataManager Initialized.")
        
    def _refresh_cookies(self):
        logger.info("Attempting to refresh NSE cookies...")
        try:
            url = 'https://www.nseindia.com'
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                self.cookies_set = True
                logger.info("Successfully refreshed NSE cookies.")
                return True
            else:
                logger.error(f"Failed to refresh cookies. HTTP {res.status_code}")
                return False
        except requests.exceptions.Timeout:
            logger.error("Timeout while refreshing cookies.")
            return False
        except Exception as e:
            logger.error(f"Cookie refresh error: {e}")
            return False

    def fetch_data(self, symbol="NIFTY"):
        if symbol in ["SENSEX", "BANKEX"]:
            logger.warning(f"Requested BSE symbol {symbol} which is not supported by NSE API.")
            return None
            
        if not self.cookies_set:
            self._refresh_cookies()
            
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        retries = 3
        
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Fetching data for {symbol} (Attempt {attempt}/{retries})")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 401 or response.status_code == 403:
                    logger.warning(f"Rate limited or unauthorized (HTTP {response.status_code}). Refreshing cookies.")
                    self._refresh_cookies()
                    time.sleep(2) # Backoff
                    continue
                    
                if response.status_code == 200:
                    data = response.json()
                    self.cache[symbol] = data # Update Cache
                    logger.info(f"Successfully fetched option chain for {symbol}.")
                    return data
                    
                logger.error(f"Unexpected HTTP {response.status_code} while fetching {symbol}.")
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout while fetching {symbol} on attempt {attempt}.")
            except requests.exceptions.ConnectionError:
                logger.error(f"Connection error while fetching {symbol} on attempt {attempt}.")
            except Exception as e:
                logger.error(f"Exception during fetch for {symbol}: {e}")
                
            time.sleep(2) # Delay before retry
            
        # If all retries fail, return the last successful data from cache
        logger.error(f"All retries failed for {symbol}. Attempting to return cached data.")
        return self.cache.get(symbol, None)
