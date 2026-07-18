import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application.intraday_scanner_service import IntradayScannerService

service = IntradayScannerService()

print("Running intraday scan (this may take a minute)...")
results = service.execute_intraday_scan()

total = len(results)
buy_scores = []
sell_scores = []
watch_scores = []
wait_count = 0

for r in results:
    sig = r.get("signal", "WAIT")
    # "score" in final output from trade_priority_engine or pipeline is 'score'
    # Wait, EliteSelectionEngine might drop things to WAIT.
    score = r.get("score", 0)
    
    if sig == "BUY":
        buy_scores.append(score)
    elif sig == "SELL":
        sell_scores.append(score)
    elif sig == "WATCH":
        watch_scores.append(score)
    elif sig == "WAIT":
        wait_count += 1
    else:
        wait_count += 1

print("\n--- STATISTICS ---")
print(f"Total returned by service: {total}")
print(f"BUY count: {len(buy_scores)}")
print(f"SELL count: {len(sell_scores)}")
print(f"WATCH count: {len(watch_scores)}")
print(f"WAIT count: {wait_count}")

def print_stats(name, scores):
    if not scores:
        print(f"\n{name} Stats: N/A (Count 0)")
        return
    avg = sum(scores) / len(scores)
    min_s = min(scores)
    max_s = max(scores)
    print(f"\n{name} Stats:")
    print(f"  Average: {avg:.2f}")
    print(f"  Lowest:  {min_s}")
    print(f"  Highest: {max_s}")

print_stats("BUY", buy_scores)
print_stats("SELL", sell_scores)
print_stats("WATCH", watch_scores)

