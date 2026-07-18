import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    service = SwingScannerService()
    
    orig = None
    import application.swing_scanner_service as sss
    orig = sss.get_all_symbols
    sss.get_all_symbols = lambda: [{"symbol": "DIXON.NS", "sector": "IT", "company_name": "DIXON"}]
    
    # We will hook into scanner.scan_market to print the mtf_result before it becomes ScanResult
    orig_scan = None
    
    # Actually, we can just intercept ScannerEngine._enrich_dataframe maybe? 
    # Or just run and read the ScanResult!
    service.execute_swing_scan(progress_callback=lambda x: None)
    
    print("ScanResult MTF Data:", service.last_results[0].mtf_data if service.last_results else "NO RESULTS")

run()
