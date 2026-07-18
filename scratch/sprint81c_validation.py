import sys, os, time, math
import logging
sys.path.append(os.getcwd())
logging.getLogger().setLevel(logging.CRITICAL)

from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from core.sector_engine import SectorEngine
from core.relative_strength_engine import RelativeStrengthEngine
from market.universe import get_fno_symbols
from data.stocks import Stock

data_provider = YahooFinanceProvider()
data_provider.connect()
trend = TrendEngine()
momentum = MomentumEngine()
struct = StructureEngine()
score = ScoreEngine()
sector = SectorEngine(data_provider)

print("Initializing Relative Strength Engine and populating cache...")
cache_start = time.time()
rs = RelativeStrengthEngine()
rs._update_rs_cache()  # Run synchronously to measure time and ensure population
cache_time = time.time() - cache_start
print(f"Cache Refresh Time: {cache_time:.2f} seconds")

scanner = ScannerEngine(
    data_provider=data_provider,
    trend_engine=trend,
    momentum_engine=momentum,
    structure_engine=struct,
    score_engine=score,
    sector_engine=sector,
    relative_strength_engine=rs
)

fno = get_fno_symbols()
stock_list = []
for item in fno:
    stock_list.append(Stock(symbol=item["symbol"], company_name=item["symbol"], sector="F&O", is_fno=True, is_nifty50=False))

print(f"Starting F&O scan for {len(stock_list)} stocks...")
scan_start = time.time()
res = scanner.scan_market(stock_list)
scan_time = time.time() - scan_start
print(f"Scanner Runtime: {scan_time:.2f} seconds")

buy_count = 0
sell_count = 0
watch_count = 0

valid_results = []
rs_scores = []
rs_0_count = 0
rs_80_count = 0
rs_20_count = 0

for r in res:
    if r.status in ["NO_DATA", "EXCLUDED"]:
        continue
    
    sig = getattr(r.signal, 'value', str(r.signal))
    if sig == "BUY" or sig == "STRONG_BULL": buy_count += 1
    elif sig == "SELL" or sig == "STRONG_BEAR": sell_count += 1
    else: watch_count += 1
    
    score = getattr(r, 'relative_strength_score', 0.0)
    rs_scores.append(score)
    valid_results.append({
        "Symbol": r.symbol,
        "RS_Score": score,
        "Decision": sig,
        "Confidence": getattr(r, 'confidence', 0.0)
    })
    
    if score == 0:
        rs_0_count += 1
    if score > 80:
        rs_80_count += 1
    if score < 20:
        rs_20_count += 1

n = len(rs_scores)
avg_rs = sum(rs_scores)/n if n > 0 else 0
variance = sum((x - avg_rs)**2 for x in rs_scores)/n if n > 0 else 0
std_dev = math.sqrt(variance)

print("--- SCAN SUMMARY ---")
print(f"Total Stocks Scanned: {len(stock_list)}")
print(f"Total Valid Stocks: {n}")
print(f"Total BUY: {buy_count}")
print(f"Total SELL: {sell_count}")
print(f"Total WATCH: {watch_count}")

print("\n--- RS STATISTICS ---")
print(f"Average RS Score: {avg_rs:.2f}")
print(f"Highest RS Score: {max(rs_scores) if rs_scores else 0:.2f}")
print(f"Lowest RS Score: {min(rs_scores) if rs_scores else 0:.2f}")
print(f"Standard Deviation: {std_dev:.2f}")
print(f"Number of stocks with RS = 0: {rs_0_count}")
print(f"Number of stocks with RS > 80: {rs_80_count}")
print(f"Number of stocks with RS < 20: {rs_20_count}")

sorted_results = sorted(valid_results, key=lambda x: x["RS_Score"])

print("\n--- TOP 20 RS STOCKS ---")
for r in reversed(sorted_results[-20:]):
    print(f"{r['Symbol']}: RS={r['RS_Score']:.2f}, Decision={r['Decision']}, Conf={r['Confidence']:.2f}")

print("\n--- BOTTOM 20 RS STOCKS ---")
for r in sorted_results[:20]:
    print(f"{r['Symbol']}: RS={r['RS_Score']:.2f}, Decision={r['Decision']}, Conf={r['Confidence']:.2f}")
