import sys
sys.path.insert(0, '.')
from application.swing_scanner_service import SwingScannerService

svc = SwingScannerService()
svc.config.swing_signal_mode = 'Aggressive'
# We will monkey patch SwingScannerService to just print out the ScanResults directly!

original_scan_market = svc.scanner_engine.scan_market if hasattr(svc, "scanner_engine") else None

def intercept(*args, **kwargs):
    print("Intercept!")
    
if original_scan_market is None:
    # Just run it and print
    result = svc.execute_swing_scan()
    print("FINISHED")
