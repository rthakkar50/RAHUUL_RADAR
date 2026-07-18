import sys, os, json
sys.path.append(os.path.abspath('.'))

from application.swing_scanner_service import SwingScannerService

service = SwingScannerService()
print("Executing scan...")
results = service.execute_swing_scan(progress_callback=lambda x: None)

if isinstance(results, str):
    results = json.loads(results)

from collections import Counter
counts = Counter(r.get("Signal") for r in results)
print("FINAL COUNTS:", counts)
print("TOTAL QUALIFIED:", len(results))
