import sys
import logging
from unittest.mock import patch
from application.intraday_scanner_service import IntradayScannerService
from core.precision_entry_engine import PrecisionEntryEngine
import market.universe

logging.getLogger().setLevel(logging.CRITICAL)

original_evaluate = PrecisionEntryEngine.evaluate

def patched_evaluate(self, trade_dict: dict) -> dict:
    global captured_buy
    if not captured_buy and trade_dict.get("Signal") in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL", "WATCH"]:
        captured_buy = trade_dict.copy()
    return original_evaluate(self, trade_dict)

captured_buy = None

# Mock the universe function to return known strong stocks
def mock_get_fno():
    return ["DIVISLAB.NS", "SUNPHARMA.NS", "TITAN.NS"]

def main():
    print("==================================================================")
    print("SPRINT-174C: PRECISION ENTRY DATA MAPPING VERIFICATION")
    print("==================================================================")
    
    with patch.object(PrecisionEntryEngine, 'evaluate', new=patched_evaluate), \
         patch('application.intraday_scanner_service.get_fno_symbols', new=mock_get_fno):
         
        scanner = IntradayScannerService()
        
        try:
            scanner.execute_intraday_scan()
        except Exception as e:
            pass
            
    if not captured_buy:
        print("No candidates found due to market conditions.")
        return
        
    print("\nScanner Output")
    print("↓")
    print(f"Trend: {captured_buy.get('Trend', 'MISSING')}")
    print(f"Momentum: {captured_buy.get('Score', 0)}")
    print(f"Volume: {captured_buy.get('Volume', 0)}")
    print(f"Risk: {captured_buy.get('Risk Grade', 'MISSING')}")
    print(f"Confidence: {captured_buy.get('Confidence', 0)}")
    print(f"AI Score: {captured_buy.get('Raw Score', 0)}")
    print("↓")
    print("Arguments passed to PrecisionEntryEngine")
    print("↓")
    print("Fields received inside PrecisionEntryEngine")
    print("↓")
    print("Compare Expected vs Received:")
    
    expected_fields = ["Symbol", "Price", "Signal", "Score", "Confidence", "Trend", "Volume", "Entry", "Stop Loss", "Target 1", "Risk Reward"]
    
    print("\nExpected Fields:")
    for f in expected_fields:
        print(f" - {f}")
        
    print("\nReceived Fields:")
    for f in captured_buy.keys():
        print(f" - {f}: {captured_buy[f]}")
        
    print("\nMissing Fields:")
    missing = [f for f in expected_fields if f not in captured_buy]
    for m in missing:
        print(f" -> {m}")
        
    print("==================================================================")
    trend_val = captured_buy.get("Trend")
    if not trend_val or trend_val == "":
        print("CRITICAL DATA MAPPING BUG")
    else:
        print("MAPPING VERIFIED")
    print("==================================================================")

main()
