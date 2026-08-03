import sys
import logging
import time

# Disable excessive logging
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
logging.getLogger("market.market_data_manager").setLevel(logging.CRITICAL)

from application.intraday_scanner_service import IntradayScannerService
from core.elite_selection_engine import EliteSelectionEngine
from core.precision_entry_engine import PrecisionEntryEngine
from market.universe import get_fno_symbols

def run_audit():
    print("====================================================================")
    print("INTRADAY ENGINE ROOT CAUSE AUDIT")
    print("====================================================================\n")

    print("TASK-4: Threshold Audit")
    print("-------------------------")
    from application.intraday_scanner_service import FNO_BUY_THRESHOLD, FNO_MIN_ADX, FNO_MIN_CONFIDENCE, FNO_MIN_VOLUME_RATIO, FNO_MIN_RR_RATIO, FNO_MIN_LIQUIDITY
    print(f"Confidence: {FNO_MIN_CONFIDENCE}%")
    print(f"Minimum Score: {FNO_BUY_THRESHOLD}")
    print(f"Risk/RR: {FNO_MIN_RR_RATIO}")
    print(f"Volume: {FNO_MIN_LIQUIDITY}")
    print(f"ADX: {FNO_MIN_ADX}")
    print("\n")

    print("TASK-5: Market Regime Audit")
    print("-------------------------")
    scanner = IntradayScannerService()
    # Mock manager to avoid long downloads if possible, but let's just let it run.
    from market.yahoo_provider import YahooFinanceProvider
    from market.market_data_manager import MarketDataManager
    provider = YahooFinanceProvider()
    provider.connect()
    manager = MarketDataManager(yahoo_provider=provider)
    trend = scanner._get_market_trend(manager)
    print(f"Market Bias: {trend}")
    print(f"Adjustment: None natively visible in intraday_scanner_service")
    print(f"Decision Threshold: {FNO_BUY_THRESHOLD}")
    print(f"BUY Threshold: {FNO_BUY_THRESHOLD}")
    print(f"SELL Threshold: 100 - Score (Normalized)")
    print("\n")

    print("Running Full Pipeline...")
    # Hook into FNO filter
    original_validate = scanner.fno_filter.validate_for_fno
    
    stage_counts = {
        "Universe": len(get_fno_symbols()),
        "Raw Scanned": 0,
        "FNO Filter Passed": 0,
        "Elite Passed": 0,
        "Precision Passed": 0
    }
    
    fno_rejections = []
    elite_rejections = []
    precision_rejections = []
    
    decisions = {"BUY": 0, "SELL": 0, "WATCH": 0, "WAIT": 0}
    
    raw_results = []
    
    def progress(p):
        sys.stdout.write(f"\rProgress: {p}%")
        sys.stdout.flush()

    try:
        results = scanner.execute_intraday_scan(progress_callback=progress)
    except Exception as e:
        print(f"\nScan failed: {e}")
        results = scanner.last_results
        
    print("\n\nTASK-1 & TASK-2: Funnel Audit")
    print("-------------------------")
    
    # We must introspect the processed_results and the elite flow
    processed_results = getattr(scanner, 'last_full_results', [])
    
    stage_counts["Raw Scanned"] = len(processed_results)
    
    # FNO Filter Simulation to see what would have passed IF append was AFTER check
    # Actually, they are in processed_results. Let's see how many WOULD pass the check.
    fno_passed_count = 0
    for r in processed_results:
        symbol = r["Symbol"]
        decision = r["Signal"]
        if decision in decisions:
            decisions[decision] += 1
        else:
            decisions[decision] = 1
            
        is_valid, reason = scanner.fno_filter.validate_for_fno({
            "Symbol": symbol,
            "Score": r["Score"],
            "Confidence": r["Confidence"],
            "ADX": r.get("ADX", 0),
            "Volume": r["Volume"],
            "Risk Reward": r["Risk Reward"],
            "OI Change %": r.get("OI Change %", 0),
            "PCR": r.get("PCR", 1.0),
            "Signal": decision
        })
        if is_valid:
            fno_passed_count += 1
        else:
            fno_rejections.append({"Symbol": symbol, "Reason": reason, "Stage": "FNO Filter", "Confidence": r["Confidence"], "Score": r["Score"]})
            
    stage_counts["FNO Filter Passed"] = fno_passed_count
    
    ese = EliteSelectionEngine()
    pee = PrecisionEntryEngine()
    
    elite_passed_count = 0
    for r in processed_results:
        elite_res = ese.evaluate(dict(r))
        if elite_res is not None:
            elite_passed_count += 1
            pee_res = pee.evaluate(elite_res)
            if pee_res is not None:
                stage_counts["Precision Passed"] += 1
            else:
                precision_rejections.append(r["Symbol"])
        else:
            elite_rejections.append(r["Symbol"])
            
    stage_counts["Elite Passed"] = elite_passed_count

    print(f"{stage_counts['Universe']}")
    print("↓")
    print(f"{stage_counts['Raw Scanned']} (Post Master Pipeline)")
    print("↓")
    print(f"{stage_counts['FNO Filter Passed']} (If FNO Filter was applied correctly)")
    print("↓")
    print(f"{stage_counts['Elite Passed']} (Elite Selection Engine)")
    print("↓")
    print(f"{stage_counts['Precision Passed']} (Precision Entry Engine)")
    
    print("\nTASK-3: Decision Audit")
    print("-------------------------")
    print(f"BUY candidates: {decisions.get('BUY', 0)}")
    print(f"SELL candidates: {decisions.get('SELL', 0)}")
    print(f"WATCH candidates: {decisions.get('WATCH', 0)}")
    print(f"WAIT / Rejected by Master Pipeline: {decisions.get('WAIT', 0)}")

    print("\nTASK-6: Data Audit")
    print("-------------------------")
    print(f"Universe Size: {stage_counts['Universe']}")
    print(f"Symbols with data (Scanned): {stage_counts['Raw Scanned']}")
    print(f"Symbols rejected: {stage_counts['Raw Scanned'] - stage_counts['Precision Passed']}")
    print(f"Symbols qualified: {stage_counts['Precision Passed']}")

    print("\nTASK-7: Top 20 Rejections (FNO Filter)")
    print("-------------------------")
    for r in fno_rejections[:20]:
        print(f"{r['Symbol']} | Stage: {r['Stage']} | Reason: {r['Reason']} | Score: {r['Score']} | Confidence: {r['Confidence']}")
        
    print("\nTASK-8: Recovery Simulation")
    print("-------------------------")
    # Simulate if thresholds were relaxed
    sim_70 = 0
    sim_65 = 0
    sim_vol = 0
    for r in processed_results:
        score = r["Score"]
        conf = r["Confidence"]
        if score >= 55 and conf >= 70:
            sim_70 += 1
        if score >= 55 and conf >= 65:
            sim_65 += 1
        if score >= 55 and conf >= 60 and r["Volume"] >= 500:
            sim_vol += 1
            
    print(f"If Confidence = 70, FNO Qualified = {sim_70}")
    print(f"If Confidence = 65, FNO Qualified = {sim_65}")
    print(f"If Volume Threshold reduced, FNO Qualified = {sim_vol}")
    print(f"If Risk Threshold relaxed, TQI passes = (Requires full TQI recalc)")

if __name__ == '__main__':
    run_audit()
