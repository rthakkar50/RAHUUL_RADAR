import sys, os, time
import logging
sys.path.append(os.getcwd())
logging.getLogger().setLevel(logging.CRITICAL)

from application.swing_scanner_service import SwingScannerService

scanner = SwingScannerService()
print("Populating RS Cache...")
# Force update on main thread for test
scanner.engines["relative_strength"]._update_rs_cache()
print("Starting complete F&O scan...")
start = time.time()
results = scanner.execute_swing_scan()
end = time.time()

if results:
    scores = [float(r.get("Relative Strength", 0.0)) for r in results if r.get("Relative Strength") is not None]
    if scores:
        print(f"Total Stocks: {len(results)}")
        print(f"Average RS Score: {sum(scores)/len(scores):.2f}")
        print(f"Highest RS Score: {max(scores):.2f}")
        print(f"Lowest RS Score: {min(scores):.2f}")
    else:
        print("No relative strength scores found in results!")
    print(f"Scan completed in {end-start:.2f} seconds.")
else:
    print("Scan failed or returned no results.")
