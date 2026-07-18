import sys, os
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

def run():
    print("Running final validation scan...")
    service = SwingScannerService()
    res = service.execute_swing_scan()
    print(f"FINISHED SCAN. Total Actionable Trades: {len(res)}")
run()
