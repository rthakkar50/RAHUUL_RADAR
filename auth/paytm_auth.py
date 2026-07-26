import os
import json
import logging
import threading
import requests
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import time

logger = logging.getLogger(__name__)

class PaytmCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        request_token = params.get("requestToken", [None])[0] or params.get("request_token", [None])[0]
        if request_token:
            self.server.request_token = request_token
            html = "<html><body><h1>Authentication Successful!</h1><p>You can close this window now and return to the application.</p></body></html>"
        else:
            html = "<html><body><h1>Authentication Failed!</h1><p>No requestToken found in URL.</p></body></html>"
            
        self.wfile.write(html.encode("utf-8"))
        
    def log_message(self, format, *args):
        pass # Suppress HTTP access logging in console

class PaytmAuthenticator:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.server = None
        self.server_thread = None
        
    def get_login_url(self) -> str:
        # Standard Paytm login URL pattern
        return f"https://login.paytmmoney.com/merchant-login?apiKey={self.api_key}&state=RADAR"
        
    def wait_for_request_token(self, port=8000, timeout=120) -> str:
        """Starts a local server and waits for the callback"""
        self.server = HTTPServer(('127.0.0.1', port), PaytmCallbackHandler)
        self.server.request_token = None
        
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        start_time = time.time()
        while self.server.request_token is None:
            if time.time() - start_time > timeout:
                self.stop_server()
                raise TimeoutError("Timed out waiting for Paytm login callback.")
            time.sleep(0.5)
            
        token = self.server.request_token
        self.stop_server()
        return token
        
    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            
    def generate_access_tokens(self, request_token: str) -> dict:
        url = "https://developer.paytmmoney.com/accounts/v2/gettoken"
        payload = {
            "apiKey": self.api_key,
            "api_key": self.api_key,
            "apiSecretKey": self.api_secret,
            "api_secret_key": self.api_secret,
            "requestToken": request_token,
            "request_token": request_token
        }
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"Paytm token generation failed with HTTP {response.status_code}.")
            response.raise_for_status()
        
        data = response.json()
        logger.info("Paytm access tokens generated successfully.")

        token_data = data.get('data', data) if isinstance(data, dict) else data
        return {
            "access_token": token_data.get("access_token", ""),
            "public_access_token": token_data.get("public_access_token", ""),
            "read_access_token": token_data.get("read_access_token", "")
        }

def start_paytm_auth_flow(api_key: str, api_secret: str, config_path: str = "config.json") -> dict:
    """Helper to run the full flow"""
    auth = PaytmAuthenticator(api_key, api_secret)
    login_url = auth.get_login_url()
    
    webbrowser.open(login_url)
    
    request_token = auth.wait_for_request_token()
    tokens = auth.generate_access_tokens(request_token)
    
    # Save to config.json
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}
            
        if "paytm" not in data:
            data["paytm"] = {}
            
        data["market_provider"] = "paytm"
        data["paytm"]["api_key"] = api_key
        data["paytm"]["api_secret_key"] = api_secret
        data["paytm"]["access_token"] = tokens["access_token"]
        data["paytm"]["public_access_token"] = tokens["public_access_token"]
        data["paytm"]["read_access_token"] = tokens["read_access_token"]
        data["paytm"]["redirect_uri"] = "http://127.0.0.1:8000/callback"
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        logger.error(f"Failed to save tokens to config: {e}")
        
    return tokens
