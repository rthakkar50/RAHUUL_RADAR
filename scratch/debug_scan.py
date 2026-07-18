import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    service = SwingScannerService()
    
    # Patch universe to only one stock to be fast
    orig_get_all_symbols = None
    import application.swing_scanner_service as sss
    orig = sss.get_all_symbols
    sss.get_all_symbols = lambda: [{"symbol": "DIXON.NS", "sector": "IT", "company_name": "DIXON"}]
    
    # We will hook into process_post_scan to print mtf_data of the ScanResult!
    orig_process = None
    
    # Since process_post_scan is a nested function, we can just print in pipeline.run
    orig_run = service.pipeline.run
    def mock_run(**kwargs):
        print("DEBUG PIPELINE mock_run args:")
        print("mtf_data value:", kwargs.get("mtf_data"))
        print("mtf_data type:", type(kwargs.get("mtf_data")))
        return orig_run(**kwargs)
    service.pipeline.run = mock_run
    
    service.execute_swing_scan(progress_callback=lambda x: None)

run()
