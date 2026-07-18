import sys
import os
from collections import Counter

sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    service = SwingScannerService()
    # We can just manually scan one stock to see the object
    stock = service.scanner.data_provider.get_active_universe()[0]
    res = service.scanner.scan_market([stock], "SWING")[0]
    print(f"mtf_data in ScanResult: {hasattr(res, 'mtf_data')} / {res.mtf_data}")
    
run()
