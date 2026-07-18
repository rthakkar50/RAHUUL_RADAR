import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market.universe import get_all_symbols, get_fno_symbols
from data.stocks import Stock
from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
from ranking.score_engine import ScoreEngine
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.decision_engine import DecisionEngine
from core.master_signal_pipeline import MasterSignalPipeline

fno_data = get_all_symbols()
fno_symbols_set = {item["symbol"] for item in get_fno_symbols()}
stock_list = []
for item in fno_data:
    sym = item["symbol"]
    stock_list.append(Stock(symbol=sym, company_name=sym, sector=item.get("sector", "N/A"), is_fno=(sym in fno_symbols_set), is_nifty50=False))

dp = YahooFinanceProvider()
dp.connect()

te = TrendEngine()
me = MomentumEngine()
se = StructureEngine()
sce = ScoreEngine()
de = DecisionEngine()
pipeline = MasterSignalPipeline()

scanner = ScannerEngine(
    data_provider=dp,
    trend_engine=te,
    momentum_engine=me,
    structure_engine=se,
    score_engine=sce,
    sector_engine=None
)
scanner.decision_engine = de

print("Scanning market...")
results = scanner.scan_market(stock_list, mode="INTRADAY")

buy_reports = []
watch_reports = []

for r in results:
    raw_sig = getattr(r.signal, 'value', str(r.signal))
    if raw_sig in ["NO_DATA", "EXCLUDED"]:
        continue
        
    price = getattr(r, 'price', 0.0)
    volume = getattr(r, 'volume', 0.0)
    
    # Process through pipeline to get final confidence, RR, etc.
    pipeline_res = pipeline.run(
        symbol=r.symbol,
        price=price,
        decision=raw_sig,
        confidence=safe_float(getattr(r, 'confidence', 80.0), 80.0) if 'safe_float' in globals() else getattr(r, 'confidence', 80.0),
        trend={"score": getattr(r, 'trend_score', 50.0)},
        momentum={"score": getattr(r, 'momentum_score', 50.0)},
        structure={"score": getattr(r, 'structure_score', 50.0)},
        volume={"score": getattr(r, 'volume_score', 50.0)},
        risk={"score": getattr(r, 'risk_score', 50.0)},
        relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)}
    )
    
    final_sig = pipeline_res.get("status", raw_sig)
    
    raw_score = getattr(r, 'total_score', 0.0)
    adj_score = getattr(r, 'adjusted_score', raw_score)
    
    report = {
        "Symbol": r.symbol,
        "Raw Score": round(raw_score, 2),
        "Adjusted Score": round(adj_score, 2),
        "Confidence": f"{pipeline_res.get('calibrated_confidence', 80.0):.2f}%",
        "Trend": getattr(r, 'trend_direction', 'N/A'),
        "Momentum": round(getattr(r, 'momentum_score', 0.0), 2),
        "Structure": round(getattr(r, 'structure_score', 0.0), 2),
        "Volume": round(getattr(r, 'volume_score', 0.0), 2),
        "Risk/Reward": pipeline_res.get("risk_reward", "N/A"),
        "Final Decision": final_sig,
        "Rejection Reasons": getattr(r, 'reasons', [])
    }
    
    if raw_sig == "BUY":
        buy_reports.append(report)
    elif raw_sig == "WATCH" and raw_score > 65:
        watch_reports.append(report)

print("\n--- BUY REPORTS ---")
for br in buy_reports:
    print(f"Symbol: {br['Symbol']}")
    print(f"Raw Score: {br['Raw Score']} | Adjusted Score: {br['Adjusted Score']}")
    print(f"Confidence: {br['Confidence']} | RR: {br['Risk/Reward']}")
    print(f"Trend: {br['Trend']} | Mom: {br['Momentum']} | Struct: {br['Structure']} | Vol: {br['Volume']}")
    print(f"Final Decision: {br['Final Decision']}")
    print(f"Reasons: {br['Rejection Reasons']}")
    print("-" * 40)

print("\n--- WATCH > 65 REPORTS ---")
for wr in watch_reports:
    print(f"Symbol: {wr['Symbol']}")
    print(f"Raw Score: {wr['Raw Score']} | Adjusted Score: {wr['Adjusted Score']}")
    print(f"Confidence: {wr['Confidence']} | RR: {wr['Risk/Reward']}")
    print(f"Trend: {wr['Trend']} | Mom: {wr['Momentum']} | Struct: {wr['Structure']} | Vol: {wr['Volume']}")
    print(f"Final Decision: {wr['Final Decision']}")
    print(f"Reasons: {wr['Rejection Reasons']}")
    print("-" * 40)
