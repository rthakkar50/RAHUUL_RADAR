import sys
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from application.swing_scanner_service import SwingScannerService

def test_scan():
    service = SwingScannerService()
    
    # Mock data provider to limit scope to save time
    import market.universe
    original_get_all = market.universe.get_all_symbols
    def mocked_get_all():
        return original_get_all()[:20]
    market.universe.get_all_symbols = mocked_get_all

    print("Running execute_swing_scan...")
    results = service.execute_swing_scan()
    print("Scan completed.")
    
    qualified = results.get("qualified_results", [])
    for q in qualified:
        print(f"{q['Symbol']}: Signal={q['Signal']}, Score={q['Score']}, Conf={q['Confidence']}, RR={q['Risk Reward']}")

if __name__ == "__main__":
    test_scan()
