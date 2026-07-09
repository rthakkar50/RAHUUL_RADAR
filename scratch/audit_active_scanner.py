import sys
import time
import logging

sys.path.append("/Users/pr/RAHUUL_RADAR")

from application.intraday_scanner_service import IntradayScannerService
from core.elite_selection_engine import EliteSelectionEngine
from core.precision_entry_engine import PrecisionEntryEngine

logging.getLogger().setLevel(logging.CRITICAL)

def audit_scanner():
    print("Running Active Scanner Audit...")
    service = IntradayScannerService()
    
    # We will run the execute_intraday_scan but we will inject counting logic
    # Actually, if we just run it, the service doesn't store intermediate rejection reasons.
    # We need to manually run the pipeline steps as done in `execute_intraday_scan`
    
    from market.yahoo_provider import YahooFinanceProvider
    from market.universe import get_all_symbols
    from data.stocks import Stock
    from scanner.scanner_engine import ScannerEngine
    from ranking.score_engine import ScoreEngine
    from core.sector_engine import SectorEngine
    
    provider = YahooFinanceProvider()
    provider.connect()
    
    fno_data = get_all_symbols()
    loaded_symbols = len(fno_data)
    
    stock_list = []
    for item in fno_data:
        sym = item["symbol"]
        sector = item.get("sector", "N/A")
        stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=False, is_nifty50=False))
        
    score_engine = ScoreEngine()
    sector_rotation_service = SectorEngine(provider)
    scanner = ScannerEngine(
        data_provider=provider,
        trend_engine=service.engines["trend"],
        momentum_engine=service.engines["momentum"],
        structure_engine=service.engines["structure"],
        score_engine=score_engine,
        sector_engine=sector_rotation_service
    )
    
    print("Scanning...")
    raw_results = scanner.scan_market(stock_list, mode="INTRADAY")
    scanned_symbols = len(raw_results)
    
    reasons = {
        "Data Missing / API Error": loaded_symbols - scanned_symbols,
        "Low Score (<60)": 0,
        "Low Confidence (<60)": 0,
        "Poor Risk Reward (<2.0)": 0,
        "Failed TQI (<85)": 0,
        "Precision Entry Reject (<80)": 0
    }
    
    processed_results = []
    for r in raw_results:
        symbol = r.symbol
        price = getattr(r, 'price', 0.0)
        decision_str = getattr(r.signal, 'value', str(r.signal))
        
        try:
            pipeline_res = service.pipeline.run(
                symbol=symbol,
                price=price,
                decision=decision_str,
                confidence=float(getattr(r, 'confidence', 80.0)),
                trend={"score": getattr(r, 'trend_score', 50.0)},
                momentum={"score": getattr(r, 'momentum_score', 50.0)},
                structure={"score": getattr(r, 'structure_score', 50.0)},
                volume={"score": getattr(r, 'volume_score', 50.0)},
                risk={"score": getattr(r, 'risk_score', 50.0)},
                relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)}
            )
            
            engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
            score = int(engine_score) if engine_score else 50
            bullish_score = score
            if decision_str in ["SELL", "STRONG_SELL"]:
                score = 100 - bullish_score
                
            confidence = float(pipeline_res.get("calibrated_confidence", getattr(r, "confidence", 80.0)))
            entry = float(pipeline_res.get("recommended_entry", price))
            sl = float(pipeline_res.get("stop_loss", price * 0.98))
            t1 = float(pipeline_res.get("target_1", price * 1.02))
            t2 = float(pipeline_res.get("target_2", price * 1.05))
            rr = pipeline_res.get("risk_reward", 2.0)
            
            processed_results.append({
                "Symbol": symbol,
                "Signal": decision_str,
                "Score": score,
                "Confidence": confidence,
                "Entry": entry,
                "Stop Loss": sl,
                "Target 1": t1,
                "Target 2": t2,
                "Risk Reward": f"1:{round(rr, 1)}" if isinstance(rr, (int, float)) else str(rr),
                "Volume": getattr(r, 'volume', 0.0)
            })
        except:
            pass
            
    reached_elite = len(processed_results)
    elite_passed = 0
    pee_passed = 0
    
    for res in processed_results:
        # Re-implement Elite Selection Logic just to count why it fails
        score = float(res.get("Score", 0))
        conf = float(res.get("Confidence", 0))
        vol = float(res.get("Volume", 0))
        
        rr_str = str(res.get("Risk Reward", "1:2.0"))
        try:
            rr_val = float(rr_str.split(":")[1])
        except:
            rr_val = 2.0
            
        if rr_val < 2.0:
            reasons["Poor Risk Reward (<2.0)"] += 1
            continue
            
        tqi = (score * 0.45) + (conf * 0.45) + (min(vol / 100000.0, 10.0) * 0.5) + (min(rr_val, 4.0) * 1.25)
        tqi = min(100.0, max(0.0, tqi))
        
        if score < 60:
            reasons["Low Score (<60)"] += 1
            continue
        if conf < 60:
            reasons["Low Confidence (<60)"] += 1
            continue
            
        if tqi < 85:
            reasons["Failed TQI (<85)"] += 1
            continue
            
        elite_passed += 1
        
        # PEE
        entry_score = 50.0 + (min(rr_val, 4.0) * 10) + (min(vol / 200000.0, 1.0) * 10)
        if score >= 90:
            entry_score += 10
        entry_score = min(100.0, max(0.0, entry_score))
        
        if entry_score < 80:
            reasons["Precision Entry Reject (<80)"] += 1
            continue
            
        pee_passed += 1

    print(f"Loaded Symbols: {loaded_symbols}")
    print(f"Actually Scanned: {scanned_symbols}")
    print(f"Reached Elite Selection: {reached_elite}")
    print(f"Rejected by Elite: {reached_elite - elite_passed}")
    print(f"Rejected by Precision Entry: {elite_passed - pee_passed}")
    print(f"Final Passed: {pee_passed}")
    print("\nRejection Reasons:")
    for k, v in reasons.items():
        print(f"{k}: {v}")
        
if __name__ == "__main__":
    audit_scanner()
