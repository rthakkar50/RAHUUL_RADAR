import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    service = SwingScannerService()
    
    # Overwrite get_all_symbols to speed up
    import application.swing_scanner_service as sss
    sss.get_all_symbols = lambda: [{"symbol": "HDFCBANK.NS", "sector": "FINANCE", "company_name": "HDFCBANK"}]
    
    # Disable redirect_stdout in this script
    res = service.execute_swing_scan()
    print("FINISHED")
    print("Final result mtf_data type:", type(getattr(res[0], 'mtf_data', None)) if res else "NO RESULTS")

run()
