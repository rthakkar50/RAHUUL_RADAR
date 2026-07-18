import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    service = SwingScannerService()
    
    # Overwrite get_all_symbols to speed up
    import application.swing_scanner_service as sss
    sss.get_all_symbols = lambda: [{"symbol": "DIXON.NS", "sector": "IT", "company_name": "DIXON"}]
    
    res = service.execute_swing_scan()
    print("FINISHED")

run()
