import asyncio
from application.swing_scanner_service import SwingScannerService
import pandas as pd

svc = SwingScannerService()
raw_results = svc.execute_swing_scan()

print(f"Total raw results: {len(raw_results)}")
from collections import Counter
reasons = Counter()

# Let's run the exact same logic as SwingScannerService._on_scan_finished
processed_results = []
for r in raw_results:
    if getattr(r, 'status', '') == 'NO_DATA':
        reasons["No market data"] += 1
        continue
    if getattr(r, 'status', '') == 'ERROR':
        reasons["Exception in indicator"] += 1
        continue
    if getattr(r, 'status', '') == 'EXCLUDED':
        reasons["Excluded by scanner engine"] += 1
        continue

    # Let's mock process_post_scan
    # (actually we can just call it)
    try:
        from core.master_signal_pipeline import MasterSignalPipeline
        pipeline = MasterSignalPipeline()
        symbol = r.symbol
        price = getattr(r, 'price', 0.0)
        decision_str = getattr(r, 'decision', 'WAIT')
        confidence = float(getattr(r, 'confidence', 80.0))
        structure_details = getattr(r, 'structure_details', {})
        atr_val = getattr(r, 'atr_value', 0.0)
        
        pipeline_res = pipeline.run(
            symbol=symbol,
            price=price,
            decision=decision_str,
            confidence=confidence,
            trend={"score": getattr(r, 'trend_score', 50.0)},
            momentum={"score": getattr(r, 'momentum_score', 50.0)},
            structure={"score": getattr(r, 'structure_score', 50.0), "details": structure_details},
            volume={"score": getattr(r, 'volume_score', 50.0)},
            risk={"score": getattr(r, 'risk_score', 50.0)},
            relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)},
            atr=atr_val
        )
        
        if pipeline_res is None:
            reasons["Pipeline returned None"] += 1
            continue
            
        entry = pipeline_res.get("entry_price", 0.0)
        sl = pipeline_res.get("stop_loss", 0.0)
        t1 = pipeline_res.get("target_1", 0.0)
        
        if entry == 0.0 or sl == 0.0 or t1 == 0.0:
            reasons["Risk filter (Invalid entry/sl/t1)"] += 1
            continue
            
        score = pipeline_res.get("score", 0.0)
        conf = pipeline_res.get("confidence", 0.0)
        
        if score < 50.0 and conf < 50.0:
            reasons["Score/Conf < 50 (Very weak)"] += 1
            continue
            
        signal = pipeline_res.get("signal", "WAIT")
        if signal not in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL", "WATCH"]:
            reasons[f"Invalid signal: {signal}"] += 1
            continue
            
        processed_results.append(pipeline_res)
    except Exception as e:
        reasons[f"Exception: {str(e)}"] += 1
        
print("Qualified:", len(processed_results))
for k, v in reasons.items():
    print(f"{k}: {v}")
