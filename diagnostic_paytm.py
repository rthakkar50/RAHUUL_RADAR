import json
import sys
from config.config import AppConfig
from market.paytm_provider import PaytmMoneyProvider
from application.swing_scanner_service import ScannerEngine # just to test which provider would be instantiated

def run_diagnostics():
    config = AppConfig()
    config.load()
    
    print("1. Which provider instance is created at runtime?")
    market_provider_str = getattr(config, 'market_provider', getattr(config, 'data_provider', 'yahoo'))
    print(f"   Configured provider string: {market_provider_str}")
    
    provider = None
    if market_provider_str == 'paytm':
        provider = PaytmMoneyProvider()
        print(f"   Instantiated: {provider.__class__.__name__}")
    else:
        print(f"   Instantiated: Not Paytm")
        
    if not isinstance(provider, PaytmMoneyProvider):
        print("   Exiting because Paytm is not the active provider.")
        sys.exit(0)
        
    print("\n2. Is Paytm authenticated?")
    print(f"   _connected status: {provider.is_connected()}")
    
    print("\n3. Is access_token present?")
    print(f"   access_token: {bool(provider.access_token)}")
    
    print("\n4. Is public_access_token present?")
    print(f"   public_access_token: {bool(provider.public_access_token)}")
    
    print("\n5. Is read_access_token present?")
    print(f"   read_access_token: {bool(provider.read_access_token)}")
    
    print("\n6. Was any successful REST call made to the Paytm API?")
    # Try connecting if not connected
    rest_success = False
    try:
        if not provider.is_connected():
            print("   Attempting to connect...")
            provider.connect()
        rest_success = provider.is_connected()
    except Exception as e:
        print(f"   Connection failed: {e}")
        
    if rest_success:
        try:
            # Make a test REST call
            print("   Attempting to fetch Option Chain (REST)...")
            res = provider.get_option_chain("NIFTY.NS")
            if res:
                print("   REST Call Successful (Option Chain fetched).")
            else:
                print("   REST Call Failed or empty.")
        except Exception as e:
            print(f"   REST Call Failed: {e}")
            
    print("\n7. Was any WebSocket opened?")
    # Test WebSocket
    ws_status = "No"
    try:
        from market.paytm_websocket import PaytmLiveBroadcast
        import time
        ws = PaytmLiveBroadcast.get_instance()
        if provider.public_access_token:
            ws.set_token(provider.public_access_token)
            ws.connect()
            time.sleep(2)
            if ws.is_connected():
                ws_status = "Yes"
            else:
                ws_status = "No, connection failed"
            ws.disconnect()
        else:
            ws_status = "No, missing public_access_token"
    except Exception as e:
        ws_status = f"No, error: {e}"
    print(f"   {ws_status}")
    
    print("\n8. If Paytm credentials are missing, explain exactly why the UI still shows 'API: Paytm'.")
    print("   The UI reads from 'market_provider' in config.json. If this is set to 'paytm', the UI combo box will show 'API: Paytm' regardless of whether the actual credentials inside the 'paytm' dictionary are valid or present. The UI only dictates the preferred provider, while the actual connection attempt happens later during runtime (e.g. scanner execution).")

if __name__ == "__main__":
    run_diagnostics()
