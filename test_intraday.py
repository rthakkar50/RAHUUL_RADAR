from unittest.mock import patch
from application.intraday_scanner_service import IntradayScannerService
import market.universe
import logging

logging.getLogger().setLevel(logging.CRITICAL)

original_get_fno = market.universe.get_fno_symbols
def mock_get_fno():
    return original_get_fno()[:20]

def main():
    with patch('application.intraday_scanner_service.get_fno_symbols', new=mock_get_fno):
        scanner = IntradayScannerService()
        try:
            results = scanner.execute_intraday_scan()
            print("Results generated.")
            print(f"Universe: {results.get('total_universe', 0)}")
            print(f"Scanned: {results.get('total_scanned', 0)}")
            print(f"BUY: {results.get('buy_count', 0)}")
            print(f"SELL: {results.get('sell_count', 0)}")
            print(f"WATCH: {results.get('watch_count', 0)}")
            print(f"WAIT: 0")
            print(f"Rejected: {results.get('rejected_count', 0)}")
            print(f"Qualified Count: {results.get('qualified_count', 0)}")
            
            # Print symbols
            print("\nQualified Symbols:")
            for q in results.get('qualified_results', []):
                print(f"Symbol: {q.get('Symbol')}")
                print(f"Trend: {q.get('Trend')}")
                print(f"Momentum: {q.get('Score')}")
                print(f"Confidence: {q.get('Confidence')}")
                print(f"AI Score: {q.get('Raw Score')}")
                print(f"Decision: {q.get('Signal')}")
                print(f"Qualified: YES")
                print("-")
                
        except Exception as e:
            print(f"Exception: {e}")

main()
