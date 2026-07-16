from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.score_engine import ScoreEngine
from core.master_signal_pipeline import MasterSignalPipeline
import logging

provider = YahooFinanceProvider()
scanner = ScannerEngine(
    data_provider=provider,
    trend_engine=TrendEngine(),
    momentum_engine=MomentumEngine(),
    structure_engine=StructureEngine(),
    score_engine=ScoreEngine()
)
pipeline = MasterSignalPipeline()

raw_results = scanner.scan_market()

reasons = {
    "No market data": [],
    "Invalid symbol": [],
    "Exception in indicator": [],
    "Risk filter": [],
    "RR filter": [],
    "Weak Setup (Score/Conf < 50)": [],
    "Signal WAIT": [],
    "Other": []
}

for r in raw_results:
    if getattr(r, 'status', '') == 'NO_DATA':
        reasons["No market data"].append((r.symbol, "scanner_engine.py", 148))
        continue
    if getattr(r, 'status', '') == 'ERROR':
        reasons["Exception in indicator"].append((r.symbol, "scanner_engine.py", 180))
        continue
    if getattr(r, 'status', '') == 'EXCLUDED':
        reasons["Other"].append((r.symbol, "scanner_engine.py", 172))
        continue
        
    try:
        pipeline_res = pipeline.run(
            symbol=r.symbol,
            price=getattr(r, 'price', 0.0),
            decision=getattr(r, 'decision', 'WAIT'),
            confidence=float(getattr(r, 'confidence', 80.0)),
            trend={"score": getattr(r, 'trend_score', 50.0)},
            momentum={"score": getattr(r, 'momentum_score', 50.0)},
            structure={"score": getattr(r, 'structure_score', 50.0), "details": getattr(r, 'structure_details', {})},
            volume={"score": getattr(r, 'volume_score', 50.0)},
            risk={"score": getattr(r, 'risk_score', 50.0)},
            relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)},
            atr=getattr(r, 'atr_value', 0.0)
        )
    except Exception as e:
        reasons["Exception in indicator"].append((r.symbol, "master_signal_pipeline.py", 0))
        continue
        
    if pipeline_res is None:
        reasons["Other"].append((r.symbol, "swing_scanner_service.py", 231))
        continue
        
    entry = pipeline_res.get("entry_price", 0.0)
    sl = pipeline_res.get("stop_loss", 0.0)
    t1 = pipeline_res.get("target_1", 0.0)
    
    if entry == 0.0 or sl == 0.0 or t1 == 0.0:
        reasons["Risk filter"].append((r.symbol, "swing_scanner_service.py", 231))
        continue
        
    score = pipeline_res.get("score", 0.0)
    conf = pipeline_res.get("confidence", 0.0)
    
    if score < 50.0 and conf < 50.0:
        reasons["Weak Setup (Score/Conf < 50)"].append((r.symbol, "swing_scanner_service.py", 373))
        continue
        
    signal = pipeline_res.get("signal", "WAIT")
    if signal not in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL", "WATCH"]:
        reasons["Signal WAIT"].append((r.symbol, "swing_scanner_service.py", 374))
        continue
        
print("--- SUMMARY ---")
for k, v in reasons.items():
    if v:
        print(f"{k:30} {len(v)}")
        print(f"  First: {v[0][0]} at {v[0][1]}:{v[0][2]}")
