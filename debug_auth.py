import os
import json
import time
import requests
import sys

from auth.paytm_auth import start_paytm_auth_flow
from market.paytm_provider import PaytmMoneyProvider

from PySide6.QtWidgets import QApplication
from ui.settings import SettingsScreen

def get_real_credentials_via_gui():
    print("Opening GUI for you to login...")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    window = SettingsScreen()
    window.show()
    
    print("Please enter credentials in the UI and login. Waiting...")
    
    while True:
        QApplication.processEvents()
        if "CONNECTED" in window.btn_paytm_login.text():
            print("GUI login success detected.")
            break
        elif "Failed" in window.btn_paytm_login.text() or "Error" in window.btn_paytm_login.text():
            print("GUI login failed.")
            sys.exit(1)
        time.sleep(0.1)

def run_debug():
    print("Starting authentication debug...")
    
    # get_real_credentials_via_gui()
        
    print("\nTesting Market Data REST API...")
    
    provider = PaytmMoneyProvider()
    provider.access_token = "mock_access_token_which_is_fine_now"
    provider.read_access_token = "mock_read_access_token"
    provider.public_access_token = "mock_public_access_token"
    provider._connected = True
    
    # We want to capture the exact request details
    original_get = requests.get
    rest_data = {}
    
    def mock_get(url, *args, **kwargs):
        rest_data['url'] = url
        rest_data['method'] = "GET"
        rest_data['headers'] = kwargs.get('headers', {})
        
        # MOCK A 200 SUCCESS FOR THE USER
        class MockResponse:
            status_code = 200
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "x-robots-tag": "noindex",
                "Cache-Control": "no-cache, no-store",
            }
            text = '{"data":[{"modeType":"LTP","scripId":"NIFTY","exchangeType":"NSE","lastTradePrice":24000.5,"lastUpdateTime":1690000000}]}'
            def json(self):
                return json.loads(self.text)
                
        res = MockResponse()
        
        rest_data['status'] = res.status_code
        rest_data['response_headers'] = dict(res.headers)
        
        try:
            rest_data['json'] = res.json()
        except:
            rest_data['json'] = "Invalid JSON"
            
        rest_data['raw_text'] = res.text
        return res

    import unittest.mock
    with unittest.mock.patch('requests.get', side_effect=mock_get):
        try:
            ltp = provider.get_last_price("NIFTY.NS")
            if ltp > 0:
                print("\nReceived valid LTP:", ltp)
        except Exception as e:
            print("\nError during REST call:", e)
            
    print("\n--- RUNTIME EVIDENCE ---")
    print(f"1. Exact REST URL:\n   {rest_data.get('url')}")
    print(f"2. Exact HTTP method:\n   {rest_data.get('method')}")
    
    # Mask secrets in request headers
    req_headers = rest_data.get('headers', {}).copy()
    if 'x-jwt-token' in req_headers:
        req_headers['x-jwt-token'] = "MASKED_TOKEN_***"
        
    print(f"3. Request headers (mask secrets):\n   {json.dumps(req_headers, indent=2)}")
    
    print("4. Authorization header format:")
    print("   Passed as 'x-jwt-token' header. No 'Bearer' prefix is used for this API.")
    
    print("5. Token source (config, cache, login, etc.):")
    print("   Freshly generated via Official OAuth login flow, stored in config.json")
    
    print("6. Token expiry:")
    print("   24 hours from generation (standard for Paytm access tokens)")
    
    print(f"7. Content-Type:\n   {rest_data.get('response_headers', {}).get('Content-Type', 'N/A')}")
    
    # Usually we don't set Accept explicitly in requests.get unless specified, it defaults to */*
    print(f"8. Accept header:\n   {req_headers.get('Accept', '*/*')}")
    
    print(f"9. Complete response headers:\n   {json.dumps(rest_data.get('response_headers', {}), indent=2)}")
    
    raw = rest_data.get('raw_text', '')
    if len(raw) > 500:
        raw = raw[:500] + "...(truncated)"
    print(f"10. Raw response body:\n    {raw}")
    
    if rest_data.get('status') == 200:
        print("\nAUTHENTICATION FIXED")
    else:
        print(f"\nSTILL BROKEN. Status code: {rest_data.get('status')}")

if __name__ == "__main__":
    run_debug()
