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
pers_scores = []

for r in res:
    if r.status in ["NO_DATA", "EXCLUDED"]:
        continue
    
    sig = getattr(r.signal, 'value', getattr(r.signal, 'name', str(r.signal)))
    if sig in ["BUY", "STRONG_BUY"]: buy_count += 1
    elif sig in ["SELL", "STRONG_SELL", "WEAK", "AVOID"]: sell_count += 1
    else: watch_count += 1
    
    p_score = getattr(r, 'trend_persistence', 50.0)
    pers_scores.append(p_score)
    valid_results.append({
        "Symbol": r.symbol,
        "Persistence": p_score,
        "RS_Score": getattr(r, 'relative_strength_score', 0.0),
        "Momentum": getattr(r, 'relative_momentum', 0.0),
        "Decision": sig,
        "Confidence": getattr(r, 'confidence', 0.0)
    })

n = len(pers_scores)
avg_pers = sum(pers_scores)/n if n > 0 else 0
variance = sum((x - avg_pers)**2 for x in pers_scores)/n if n > 0 else 0
std_dev = math.sqrt(variance)
over_80 = sum(1 for p in pers_scores if p > 80)
under_20 = sum(1 for p in pers_scores if p < 20)

print("--- SCAN SUMMARY ---")
print(f"Total Stocks Scanned: {len(stock_list)}")
print(f"Total Valid Stocks: {n}")
print(f"Total BUY: {buy_count}")
print(f"Total SELL: {sell_count}")
print(f"Total WATCH: {watch_count}")

print("\n--- PERSISTENCE STATISTICS ---")
print(f"Average Persistence: {avg_pers:.2f}")
print(f"Highest Persistence: {max(pers_scores) if pers_scores else 0:.2f}")
print(f"Lowest Persistence: {min(pers_scores) if pers_scores else 0:.2f}")
print(f"Standard Deviation: {std_dev:.2f}")
print(f"Persistence > 80: {over_80}")
print(f"Persistence < 20: {under_20}")

sorted_results = sorted(valid_results, key=lambda x: x["Persistence"])

print("\n--- TOP 20 PERSISTENCE STOCKS ---")
for r in reversed(sorted_results[-20:]):
    print(f"{r['Symbol']}: Pers={r['Persistence']:.2f}, Mom={r['Momentum']:.2f}, RS={r['RS_Score']:.2f}, Decision={r['Decision']}, Conf={r['Confidence']:.2f}")

print("\n--- BOTTOM 20 PERSISTENCE STOCKS ---")
for r in sorted_results[:20]:
    print(f"{r['Symbol']}: Pers={r['Persistence']:.2f}, Mom={r['Momentum']:.2f}, RS={r['RS_Score']:.2f}, Decision={r['Decision']}, Conf={r['Confidence']:.2f}")

