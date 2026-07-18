import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    service = SwingScannerService()
    
    orig = None
    import application.swing_scanner_service as sss
    orig = sss.get_all_symbols
    sss.get_all_symbols = lambda: [{"symbol": "DIXON.NS", "sector": "IT", "company_name": "DIXON"}]
    
    # Run scan
    res = service.scanner.scan_market(sss.get_all_symbols(), "SWING")
    print("Length:", len(res))
    if res:
        r = res[0]
        print(f"ScanResult object mtf_data directly: {getattr(r, 'mtf_data', 'MISSING')}")

run()
