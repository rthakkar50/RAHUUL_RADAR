import sys, os, json
sys.path.append(os.path.abspath('.'))
from application.swing_scanner_service import SwingScannerService
service = SwingScannerService()
print("Executing scan...")
results = service.execute_swing_scan(progress_callback=lambda x: None)
if isinstance(results, str):
    try:
        results = json.loads(results)
    except:
        pass
from collections import Counter
c = Counter()
for item in results:
    if isinstance(item, dict):
        c[item.get("Signal")] += 1
print("FINAL COUNTS:", c)
print("TOTAL QUALIFIED:", len([i for i in results if isinstance(i, dict)]))
