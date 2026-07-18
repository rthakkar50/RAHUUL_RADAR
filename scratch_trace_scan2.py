import sys, os, json
sys.path.append(os.path.abspath('.'))

import concurrent.futures
from application.swing_scanner_service import SwingScannerService
from scanner.scanner_engine import ScannerEngine

orig_scan_market = ScannerEngine.scan_market
scan_market_results = []

def mock_scan_market(*args, **kwargs):
    res = orig_scan_market(*args, **kwargs)
    scan_market_results.append(res)
    return res

ScannerEngine.scan_market = mock_scan_market

orig_submit = concurrent.futures.ThreadPoolExecutor.submit
process_post_scan_returns = []

def mock_submit(self, fn, *args, **kwargs):
    if getattr(fn, '__name__', '') == 'process_post_scan':
        def wrapped_fn(*f_args, **f_kwargs):
            try:
                res = fn(*f_args, **f_kwargs)
                process_post_scan_returns.append(res)
                return res
            except Exception as e:
                process_post_scan_returns.append("EXCEPTION")
                raise e
        return orig_submit(self, wrapped_fn, *args, **kwargs)
    return orig_submit(self, fn, *args, **kwargs)

concurrent.futures.ThreadPoolExecutor.submit = mock_submit

service = SwingScannerService()
print("Starting trace...", flush=True)

# Patch the Quality Gate loop to count drop-offs
orig_execute = SwingScannerService.execute_swing_scan

def mock_execute(*args, **kwargs):
    pass # Too complex to mock the local loop.

final_results = service.execute_swing_scan(progress_callback=lambda x: None)
if isinstance(final_results, str):
    try:
        final_results = json.loads(final_results)
    except:
        pass

raw_results = scan_market_results[0] if scan_market_results else []
universe_loaded = len(raw_results)
symbols_entering_process = len(process_post_scan_returns)
symbols_returning_none = sum(1 for x in process_post_scan_returns if x is None)

# In SwingScannerService, processed_results contains the non-None returns
symbols_entering_quality = len([x for x in process_post_scan_returns if x is not None and x != "EXCEPTION"])

waits = 0
qualified = 0

if isinstance(final_results, list):
    for r in final_results:
        if isinstance(r, dict):
            if r.get("Signal") == "WATCH":
                waits += 1
            else:
                qualified += 1

print("\n--- EXACT EXECUTION TRACE ---")
print(f"1. Universe loaded: {universe_loaded}")
print(f"2. Raw results returned by ScannerEngine: {len(raw_results)}")
print(f"3. Symbols rejected before process_scan_result(): {universe_loaded - symbols_entering_process}")
print(f"4. Symbols entering process_scan_result(): {symbols_entering_process}")
print(f"5. Symbols where process_scan_result() returns None: {symbols_returning_none}")
print(f"6. Symbols entering Quality Gate: {symbols_entering_quality}")
print(f"7. WAIT count: {waits}")
print(f"8. Qualified count: {qualified}")
print("-----------------------------")

