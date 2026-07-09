import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from application.intraday_scanner_service import IntradayScannerService
from market.yahoo_provider import YahooFinanceProvider
from data.stocks import Stock
from scanner.scanner_engine import ScannerEngine
from ranking.score_engine import ScoreEngine
from market.universe import get_all_symbols

def run():
    provider = YahooFinanceProvider()
    provider.connect()
    service = IntradayScannerService()
    
    fno_data = get_all_symbols()
    stock_list = []
    for item in fno_data:
        sym = item["symbol"]
        sector = item.get("sector", "N/A")
        stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=True, is_nifty50=False))
        
    scanner = ScannerEngine(
        data_provider=provider,
        trend_engine=service.engines["trend"],
        momentum_engine=service.engines["momentum"],
        structure_engine=service.engines["structure"],
        score_engine=ScoreEngine(),
        sector_engine=None
    )
    
    # We will just run the scan and look at the "reasons" inside each scan_result.
    results = scanner.scan_market(stock_list, mode="INTRADAY")
    
    rejection_counts = {
        "Only two engines agree": 0,
        "ADX < 20 Sideways Filter": 0,
        "Failed BUY validation": 0,
        "Failed SELL validation": 0,
        "MTCE Major Conflict": 0,
        "MTCE No Alignment": 0,
        "MTCE Wait for confirmation": 0,
        "Other WAIT/WATCH": 0
    }
    
    total = len(results)
    watch_wait_count = 0
    
    for r in results:
        signal = getattr(r, "signal", "WATCH")
        signal_str = getattr(signal, "value", str(signal))
        
        # If we have reasons, let's parse the final downgrades
        reasons = getattr(r, "reasons", [])
        
        # We only care about symbols that resulted in WATCH or WAIT at the base scanner level
        # Actually, in base scanner, is the signal mapped to WAIT?
        # In scanner_engine, mapped_signal = signal_map.get(decision, WATCH).
        # decision can be WAIT, so it maps to WATCH.
        if "WATCH" in signal_str or "WAIT" in signal_str or "NEUTRAL" in signal_str or getattr(r, "decision", "") in ["WATCH", "WAIT"]:
            watch_wait_count += 1
            
            # Find the primary reason for being WATCH/WAIT.
            # We look in reverse order to see the FINAL downgrade that pushed it to WATCH/WAIT
            found = False
            for reason in reversed(reasons):
                if "Downgrading" in reason or "Decision: [WATCH]" in reason:
                    if "Only two engines agree" in reason:
                        rejection_counts["Only two engines agree"] += 1
                        found = True
                        break
                    elif "ADX < 20 Sideways Filter" in reason:
                        rejection_counts["ADX < 20 Sideways Filter"] += 1
                        found = True
                        break
                    elif "Failed BUY validation" in reason:
                        rejection_counts["Failed BUY validation"] += 1
                        found = True
                        break
                    elif "Failed SELL validation" in reason:
                        rejection_counts["Failed SELL validation"] += 1
                        found = True
                        break
                    elif "MTCE" in reason and "Major Conflict" in reason:
                        rejection_counts["MTCE Major Conflict"] += 1
                        found = True
                        break
                    elif "MTCE" in reason and "Wait for confirmation" in reason:
                        rejection_counts["MTCE Wait for confirmation"] += 1
                        found = True
                        break
                    elif "MTCE" in reason and "No Alignment" in reason:
                        rejection_counts["MTCE No Alignment"] += 1
                        found = True
                        break
                        
            if not found:
                rejection_counts["Other WAIT/WATCH"] += 1

    print("=== REJECTION REASONS ===")
    print(f"Total processed: {total}")
    print(f"Total WATCH/WAIT: {watch_wait_count}")
    for k, v in rejection_counts.items():
        if v > 0:
            pct = (v / watch_wait_count) * 100 if watch_wait_count > 0 else 0
            print(f"{k}: {v} ({pct:.1f}%)")
    
if __name__ == "__main__":
    run()
