import os
import sys
import json
sys.path.append(os.path.abspath('.'))

from application.swing_scanner_service import SwingScannerService

def main():
    service = SwingScannerService()
    results = service.execute_swing_scan(progress_callback=lambda x: None)
    
    if isinstance(results, str):
        results = json.loads(results)
    
    buys = []
    sells = []
    waits = []
    
    for r in results:
        if isinstance(r, dict):
            sig = r.get("Signal")
            if sig in ["BUY", "STRONG_BUY"]:
                buys.append(r)
            elif sig in ["SELL", "STRONG_SELL"]:
                sells.append(r)
            elif sig == "WATCH":
                waits.append(r)

    print(f"Total Qualified: {len(buys) + len(sells)}")
    print(f"BUY Signals: {len(buys)}")
    print(f"SELL Signals: {len(sells)}")
    print(f"WAIT Signals: {len(waits)}")
    
    if buys:
        avg_buy_conf = sum(float(b.get("Confidence", 0)) for b in buys) / len(buys)
        print(f"Avg BUY Confidence: {avg_buy_conf:.2f}%")
    else:
        print("Avg BUY Confidence: N/A")
        
    if sells:
        avg_sell_conf = sum(float(s.get("Confidence", 0)) for s in sells) / len(sells)
        print(f"Avg SELL Confidence: {avg_sell_conf:.2f}%")
    else:
        print("Avg SELL Confidence: N/A")

if __name__ == '__main__':
    main()
