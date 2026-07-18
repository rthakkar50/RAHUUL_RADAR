import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

service = SwingScannerService()
res = service.execute_swing_scan()
qualified_results = res.get("qualified_results", [])

print("\n--- ELITE SELECTION FAILURES ---")
for item in qualified_results:
    score = float(item.get("Score", 0.0))
    conf = float(item.get("Confidence", 0.0))
    
    try: 
        entry = float(item.get("Entry", 0.0))
        sl = float(item.get("Stop Loss", 0.0))
        t1 = float(item.get("Target 1", 0.0))
        if abs(entry - sl) > 0:
            rr = abs(t1 - entry) / abs(entry - sl)
        else:
            rr = 0.0
    except: 
        rr = 0.0
        
    min_score = 75.0
    min_conf = 70.0
    min_rr = 1.8
    
    if score >= min_score and conf >= min_conf and rr >= min_rr:
        if item.get("Execution Status") != "READY":
            print(f"{item['Symbol']} ({item['Signal']}): Score={score}, Conf={conf}")
            print(f"Reason: {item.get('Execution Reason')}")
            print("-" * 30)
