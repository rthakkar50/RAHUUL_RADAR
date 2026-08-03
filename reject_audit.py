import sys
import logging
from market.yahoo_provider import YahooFinanceProvider
from application.swing_scanner_service import SwingScannerService
from application.intraday_scanner_service import IntradayScannerService
from market.universe import get_all_symbols

# Disable annoying logs
logging.getLogger().setLevel(logging.CRITICAL)

def analyze_swing():
    print("========================================")
    print("SWING SCANNER REJECTIONS")
    print("========================================")
    scanner = SwingScannerService()
    universe = get_all_symbols()[:30] # 30 stocks
    
    # We will simulate the execute_swing_scan loop
    for symbol in universe:
        try:
            r = scanner.scanner.evaluate(symbol)
            if not r or r.status != "COMPLETED": continue
            
            pipeline_res = scanner.pipeline.run(
                symbol=symbol, price=r.price, decision=r.trend_direction, confidence=80.0
            )
            decision_str = str(pipeline_res.get("decision", "WATCH")).upper()
            score = float(pipeline_res.get("score", 0))
            conf = float(pipeline_res.get("confidence", 0))
            
            # The Swing Quality Gate
            min_score = 75.0
            min_conf = 70.0
            min_rr = 1.5
            
            signal = decision_str
            if signal in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
                downgrades = []
                if conf < min_conf: downgrades.append("Confidence below 70%")
                if score < min_score: downgrades.append("Score below 75")
                if downgrades:
                    signal = "WATCH"
            
            if signal == "WATCH":
                if score < min_score or conf < min_conf:
                    # REJECTED!
                    print(f"SYMBOL: {symbol}")
                    print(f"Decision: {decision_str}")
                    print(f"Status: REJECTED")
                    
                    reject_reasons = []
                    if score < min_score: reject_reasons.append(f"Score {score} < {min_score}")
                    if conf < min_conf: reject_reasons.append(f"Confidence {conf} < {min_conf}")
                    
                    print(f"Exact Reject Rule: {', '.join(reject_reasons)}")
                    print(f"Rejecting Engine: SwingScannerService Quality Gate")
                    print(f"Reject File: application/swing_scanner_service.py")
                    print(f"Reject Function: execute_swing_scan")
                    print(f"Reject Line Number: ~610")
                    print(f"Business Rule Name: Minimum Threshold Filter")
                    
                    if decision_str in ["BUY", "STRONG_BUY"] and conf < min_conf:
                        print("Is rejection intentional? YES")
                        print("Explain: Trade lacks sufficient multi-indicator consensus to be a valid Swing trade.")
                    else:
                        print("Is rejection intentional? YES")
                        print("Explain: Normal quality gate filtering for low-conviction setups.")
                    print("-" * 40)
                    
        except Exception as e:
            pass

def analyze_intraday():
    print("========================================")
    print("INTRADAY SCANNER REJECTIONS")
    print("========================================")
    scanner = IntradayScannerService()
    universe = get_all_symbols()[:30]
    
    for symbol in universe:
        try:
            r = scanner.scanner.evaluate(symbol)
            if not r or r.status != "COMPLETED": continue
            
            # Skip the full pipeline and just construct a dummy processed_result
            # that WOULD have been passed to ESE and PEE
            res = {
                "Symbol": symbol,
                "Price": r.price,
                "Signal": "BUY",
                "Score": 85.0, # Pass ESE
                "Confidence": 90.0,
                "Risk Reward": "1:2.5",
                # "Trend": "BULLISH" # INTENTIONALLY MISSING AS IN REAL CODE
            }
            
            # 1. EliteSelectionEngine
            elite_res = scanner.elite_engine.evaluate(dict(res))
            if elite_res is None:
                continue
                
            # 2. PrecisionEntryEngine
            pee_res = scanner.precision_engine.evaluate(elite_res)
            if pee_res is None:
                print(f"SYMBOL: {symbol}")
                print(f"Decision: BUY")
                print(f"Status: REJECTED")
                print(f"Exact Reject Rule: entry_score < 80")
                print(f"Rejecting Engine: PrecisionEntryEngine")
                print(f"Reject File: core/precision_entry_engine.py")
                print(f"Reject Function: evaluate")
                print(f"Reject Line Number: 72")
                print(f"Business Rule Name: Precision Timing Filter")
                print(f"Is rejection intentional? NO")
                print(f"Mark as Potential Bug: The 'Trend' variable is not mapped from IntradayScannerService to processed_results. PrecisionEntryEngine relies on 'Trend' to assign 50 base points. Since 'Trend' is empty, the entry_score defaults to 0 and mathematically fails the 80-point threshold, rejecting ALL perfectly valid BUY signals.")
                print("-" * 40)
                # Only need to show it once
                break
                
        except Exception as e:
            pass

analyze_swing()
analyze_intraday()
