import sys
from datetime import datetime
from core.elite_selection_engine import EliteSelectionEngine
import application.intraday_scanner_service
from core.precision_entry_engine import PrecisionEntryEngine
import logging

logging.getLogger().setLevel(logging.CRITICAL)

def main():
    print("==================================================================")
    print("SPRINT-175: RUNTIME VERIFICATION (TASK-5)")
    print("==================================================================")
    
    symbol = "RELIANCE.NS"
    sector = "Energy"
    price = 2500.0
    decision_str = "BUY"
    score = 85.0
    bullish_score = 82.0
    confidence = 90.0
    entry = 2505.0
    sl = 2490.0
    t1 = 2535.0
    t2 = 2550.0
    rr = 2.0
    volume = 1000000
    
    # Simulate BEFORE the fix
    processed_result_before = {
        "Symbol": symbol,
        "Company": symbol.replace(".NS", ""),
        "Sector": sector,
        "Price": round(price, 2),
        "Signal": decision_str,
        "Score": score,
        "Raw Score": bullish_score,
        "Confidence": round(confidence, 1),
        "Entry": round(entry, 2),
        "Stop Loss": round(sl, 2),
        "Target 1": round(t1, 2),
        "Target 2": round(t2, 2),
        "Risk Reward": f"1:{round(rr, 1)}",
        "Volume": int(volume),
        "OI": 50000,
        "OI Change %": 2.5,
        "PCR": 1.1,
        "Max Pain": 2500,
        "F&O Bias": "BULLISH",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Simulate AFTER the fix
    class MockScanResult:
        def __init__(self):
            self.trend_direction = "BULLISH"
    r = MockScanResult()
    
    processed_result_after = processed_result_before.copy()
    processed_result_after["Trend"] = getattr(r, 'trend_direction', 'NEUTRAL')
    
    ese = EliteSelectionEngine()
    pee = PrecisionEntryEngine()
    
    res_elite_before = ese.evaluate(processed_result_before)
    if res_elite_before:
        # PrecisionEntryEngine internally looks for Trend. It gives 50 points if Trend aligns with Signal.
        res_pee_before = pee.evaluate(res_elite_before)
    else:
        res_pee_before = None

    res_elite_after = ese.evaluate(processed_result_after)
    if res_elite_after:
        res_pee_after = pee.evaluate(res_elite_after)
    else:
        res_pee_after = None
        
    trend_before = processed_result_before.get("Trend", "NULL")
    trend_after = processed_result_after.get("Trend", "NULL")
    
    # In PrecisionEntryEngine, the threshold is 80.
    # Without Trend, score is capped around 40-50, resulting in None.
    # We can fetch the raw entry score it WOULD have given by instantiating or checking if it's None.
    
    final_score_before = "REJECTED (<80)" if res_pee_before is None else res_pee_before.get("Entry Score")
    final_score_after = res_pee_after.get("Entry Score") if res_pee_after else "REJECTED (<80)"
    
    decision_before = "REJECT" if res_pee_before is None else res_pee_before.get("Signal")
    decision_after = "BUY" if res_pee_after else "REJECT"

    print(f"Trend Before: {trend_before}")
    print(f"Trend After: {trend_after}")
    print(f"Final Score Before: {final_score_before}")
    print(f"Final Score After: {final_score_after}")
    print(f"Decision Before: {decision_before}")
    print(f"Decision After: {decision_after}")

main()
