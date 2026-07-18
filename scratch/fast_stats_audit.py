import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market.universe import get_all_symbols, get_fno_symbols
from data.stocks import Stock
from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
from ranking.score_engine import ScoreEngine

fno_data = get_all_symbols()
fno_symbols_set = {item["symbol"] for item in get_fno_symbols()}
stock_list = []
for item in fno_data:
    sym = item["symbol"]
    stock_list.append(Stock(symbol=sym, company_name=sym, sector=item.get("sector", "N/A"), is_fno=(sym in fno_symbols_set), is_nifty50=False))

dp = YahooFinanceProvider()
dp.connect()

# We only need scanner_engine and score_engine to get the decision
scanner = ScannerEngine(
    data_provider=dp,
    trend_engine=None,
    momentum_engine=None,
    structure_engine=None,
    score_engine=ScoreEngine(),
    sector_engine=None
)

print("Scanning market...")
results = scanner.scan_market(stock_list, mode="INTRADAY")

total = len(results)
buy_scores = []
sell_scores = []
watch_scores = []
wait_scores = []

for r in results:
    sig = getattr(r.signal, 'value', str(r.signal))
    score = getattr(r, 'adjusted_score', getattr(r, 'total_score', 0.0))
    
    if sig == "BUY":
        buy_scores.append(score)
    elif sig == "SELL":
        sell_scores.append(score)
    elif sig == "WATCH":
        watch_scores.append(score)
    elif sig == "WAIT":
        wait_scores.append(score)

print("\n--- STATISTICS ---")
print(f"Total scanned: {total}")
print(f"BUY count: {len(buy_scores)}")
print(f"SELL count: {len(sell_scores)}")
print(f"WATCH count: {len(watch_scores)}")
print(f"WAIT count: {len(wait_scores)}")

def print_stats(name, scores):
    if not scores:
        print(f"\n{name} Stats: N/A (Count 0)")
        return
    avg = sum(scores) / len(scores)
    min_s = min(scores)
    max_s = max(scores)
    print(f"\n{name} Stats:")
    print(f"  Average {name} score: {avg:.2f}")
    print(f"  Lowest {name} score:  {min_s:.2f}")
    print(f"  Highest {name} score: {max_s:.2f}")

print_stats("BUY", buy_scores)
print_stats("SELL", sell_scores)
print_stats("WATCH", watch_scores)

