import requests
import logging

logger = logging.getLogger("DataManager")

class HeaderManager:
    @staticmethod
    def get_nse_headers():
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }

class CookieManager:
    def __init__(self, session):
        self.session = session

    def refresh_nse_cookies(self):
        try:
            res = self.session.get("https://www.nseindia.com", timeout=10)
            return res.status_code in [200, 403, 404]
        except:
            return False

class SessionManager:
    def __init__(self):
        self.nse_session = None
        self.renew_nse_session()
        
    def renew_nse_session(self):
        self.nse_session = requests.Session()
        self.nse_session.headers.update(HeaderManager.get_nse_headers())
        cm = CookieManager(self.nse_session)
        cm.refresh_nse_cookies()
        
    def get_nse_session(self):
        return self.nse_session
