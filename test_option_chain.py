import sys
from unittest.mock import patch
from market.paytm_provider import PaytmMoneyProvider

def mock_get(url, *args, **kwargs):
    class MockResponse:
        status_code = 200
        def raise_for_status(self): pass
        def json(self):
            return {"data": [{"option_type": "CE", "strike": 25000, "ltp": 100}]}
    return MockResponse()

def run_test():
    provider = PaytmMoneyProvider()
    provider._connected = True
    provider.access_token = "MOCK_TOKEN"
    
    with patch("requests.get", side_effect=mock_get):
        chain = provider.get_option_chain("NIFTY.NS")
        if chain and "data" in chain:
            print("SUCCESS: Option Chain loaded.")
            sys.exit(0)
            
    print("ERROR: Option chain failed to load.")
    sys.exit(1)

if __name__ == "__main__":
    run_test()
