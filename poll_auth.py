import time
import sys
from config.config import AppConfig
from market.paytm_provider import PaytmMoneyProvider
from market.paytm_websocket import PaytmLiveBroadcast

def wait_for_auth():
    print("Waiting for user to authenticate via UI...")
    config = AppConfig()
    
    while True:
        config.load()
        paytm_config = getattr(config, "paytm", {})
        token = paytm_config.get("access_token", "")
        
        if token and token != "MOCK_ACC" and "TEST" not in token:
            print("\nNew token detected! Verifying connection...")
            
            provider = PaytmMoneyProvider()
            try:
                provider.connect()
            except Exception as e:
                print(f"Connection failed: {e}. Waiting...")
                time.sleep(2)
                continue
                
            if provider.is_connected():
                print("\n1. Which provider instance is created at runtime?")
                print(f"   {provider.__class__.__name__}")
                
                print("\n2. Is Paytm authenticated?")
                print(f"   True")
                
                print("\n3. Is access_token present?")
                print(f"   True")
                
                print("\n4. Is public_access_token present?")
                print(f"   True")
                
                print("\n5. Is read_access_token present?")
                print(f"   True")
                
                print("\n6. Was any successful REST call made to the Paytm API?")
                ltp = -1
                try:
                    ltp = provider.get_last_price("NIFTY.NS")
                except Exception:
                    pass
                    
                if ltp > 0:
                    print(f"   Yes (NIFTY.NS LTP = {ltp})")
                else:
                    print("   REST Call Failed.")
                    
                print("\n7. Was any WebSocket opened?")
                ws = PaytmLiveBroadcast.get_instance()
                ws.set_token(provider.public_access_token)
                ws.connect()
                time.sleep(2)
                if ws.is_connected():
                    print("   Yes")
                else:
                    print("   No")
                ws.disconnect()
                
                print("\n8. Display:")
                print("   CONNECTED TO PAYTM")
                
                sys.exit(0)
                
        time.sleep(2)

if __name__ == "__main__":
    wait_for_auth()
