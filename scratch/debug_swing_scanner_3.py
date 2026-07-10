import sys
import logging
logging.basicConfig(level=logging.ERROR, format='%(message)s')

from application.swing_scanner_service import SwingScannerService
from core.models import SignalStrength

def test_scan():
    service = SwingScannerService()
    
    import market.universe
    original_get_all = market.universe.get_all_symbols
    def mocked_get_all():
        return original_get_all()[:20]
    market.universe.get_all_symbols = mocked_get_all

    print("Running execute_swing_scan...")
    from scanner.scanner_engine import ScannerEngine
    import yfinance as yf
    
    original_scan_market = ScannerEngine.scan_market
    
    def mocked_scan_market(self, stock_list, mode, progress_callback=None):
        res = original_scan_market(self, stock_list, mode, progress_callback)
        for r in res:
            print(f"[{r.symbol}] Raw ScannerEngine Signal: {r.signal.value}")
        return res
        
    ScannerEngine.scan_market = mocked_scan_market

    results = service.execute_swing_scan()
    print("Scan completed.")
    
    qualified = results.get("qualified_results", [])
    for q in qualified:
        print(f"Final: {q['Symbol']}: Signal={q['Signal']}")

if __name__ == "__main__":
    test_scan()
