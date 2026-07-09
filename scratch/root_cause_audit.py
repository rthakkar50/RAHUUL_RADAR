import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from typing import Dict, Any

from config.settings import BASE_DIR
from application.intraday_scanner_service import IntradayScannerService, ScoreFloat, safe_float, safe_int
from market.dhan_provider import DhanProvider
from market.yahoo_provider import YahooFinanceProvider
from market.universe import get_all_symbols
from data.stocks import Stock
from scanner.scanner_engine import ScannerEngine
from ranking.score_engine import ScoreEngine
from core.sector_engine import SectorEngine
from core.institutional_validation_engine import InstitutionalValidationInput
from core.trade_execution_center import ExecutionRequest
from core.elite_selection_engine import EliteSelectionEngine
from core.precision_entry_engine import PrecisionEntryEngine

def run_audit():
    service = IntradayScannerService()
    
    # 1. Setup Providers
    data_provider = YahooFinanceProvider()
    data_provider.connect()
    
    # 2. Get Universe
    fno_data = get_all_symbols()
    stock_list = []
    for item in fno_data:
        sym = item["symbol"]
        sector = item.get("sector", "N/A")
        stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=False, is_nifty50=False))
        
    score_engine = ScoreEngine()
    sector_rotation_service = SectorEngine(data_provider)
    scanner = ScannerEngine(
        data_provider=data_provider,
        trend_engine=service.engines["trend"],
        momentum_engine=service.engines["momentum"],
        structure_engine=service.engines["structure"],
        score_engine=score_engine,
        sector_engine=sector_rotation_service
    )
    
    print("================================================")
    print("ROOT CAUSE ISOLATION AUDIT - PIPELINE TRACE")
    print("================================================\n")
    
    # Trackers
    rejection_counts = {
        "Data / OHLCV": 0,
        "Base Scanner (Watch/Neutral)": 0,
        "Validation (Institutional/False Breakout)": 0,
        "Execution Center": 0,
        "Elite Selection (TQI/RR/Conf)": 0,
        "Precision Entry": 0
    }
    
    total = len(stock_list)
    passed = 0
    
    import io, sys
    # Suppress scanner heavy logs
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    raw_results = scanner.scan_market(stock_list, mode="INTRADAY")
    
    sys.stdout = old_stdout
    
    symbols_scanned = [r.symbol for r in raw_results]
    for stock in stock_list:
        if stock.symbol not in symbols_scanned:
            print(f"{stock.symbol}\nData / OHLCV FAIL\n--------------------------------")
            rejection_counts["Data / OHLCV"] += 1
            
    for r in raw_results:
        symbol = r.symbol
        trace = []
        rejected = False
        rejection_stage = ""
        
        price = getattr(r, 'price', 0.0)
        volume = getattr(r, 'volume', 0.0)
        decision_str = getattr(r.signal, 'value', str(r.signal))
        
        if decision_str not in ["BUY", "SELL"]:
            trace.append("Base Scanner FAIL")
            rejection_stage = "Base Scanner (Watch/Neutral)"
            rejected = True
        else:
            trace.append("Base Scanner PASS")
            
        if not rejected:
            try:
                pipeline_res = service.pipeline.run(
                    symbol=symbol,
                    price=price,
                    decision=decision_str,
                    confidence=safe_float(getattr(r, 'confidence', 80.0), 80.0),
                    trend={"score": getattr(r, 'trend_score', 50.0)},
                    momentum={"score": getattr(r, 'momentum_score', 50.0)},
                    structure={"score": getattr(r, 'structure_score', 50.0)},
                    volume={"score": getattr(r, 'volume_score', 50.0)},
                    risk={"score": getattr(r, 'risk_score', 50.0)},
                    relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)}
                )
                
                engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
                score = safe_int(engine_score, 50)
                bullish_score = score
                if decision_str in ["SELL", "STRONG_SELL"]:
                    score = 100 - bullish_score
                    
                confidence = safe_float(pipeline_res.get("calibrated_confidence", getattr(r, "confidence", 80.0)), 80.0)
                entry = safe_float(pipeline_res.get("recommended_entry", price), price)
                sl = safe_float(pipeline_res.get("stop_loss", price * 0.98), price * 0.98)
                t1 = safe_float(pipeline_res.get("target_1", price * 1.02), price * 1.02)
                t2 = safe_float(pipeline_res.get("target_2", price * 1.05), price * 1.05)
                rr = pipeline_res.get("risk_reward", 2.0)
                
                fs_res = pipeline_res.get("report")
                if fs_res is not None:
                    if hasattr(fs_res, "to_dict"): fs_dict = fs_res.to_dict()
                    elif hasattr(fs_res, "status"): fs_dict = {"status": fs_res.status}
                    elif isinstance(fs_res, dict): fs_dict = fs_res
                    else: fs_dict = {"status": "APPROVED"}
                else:
                    fs_dict = {"status": "APPROVED"}
                    
                val_input = InstitutionalValidationInput(
                    false_signal_result=fs_dict,
                    mtf_result={"status": pipeline_res.get("status") or "APPROVED", "score": 100.0},
                    entry_result={"entry_score": safe_float(pipeline_res.get("entry_score"), 100.0)},
                    exit_result={"exit_action": pipeline_res.get("exit_action") or "HOLD", "exit_confidence": confidence},
                    walk_forward_result={"status": "APPROVED"},
                    ranking_result={"status": "APPROVED"},
                    confidence_result={"confidence": confidence, "status": "APPROVED"},
                    performance_result={"status": "APPROVED"}
                )
                service.validation_engine.validate_all_modules(val_input)
                trace.append("Institution PASS")
                
                req = ExecutionRequest(
                    symbol=symbol,
                    action=decision_str if decision_str in ["BUY", "SELL"] else "BUY",
                    quantity=10,
                    entry_price=entry,
                    stop_loss=sl,
                    target_1=t1,
                    target_2=t2,
                    target_3=t2,
                    confidence=confidence,
                    position_size_factor=1.0,
                    strategy_name="INTRADAY",
                    timestamp=datetime.now().isoformat()
                )
                service.execution_center.validate_request(req)
                service.execution_center.perform_risk_check(req)
                service.execution_center.perform_validation_check(req)
                trace.append("Execution PASS")
                
                processed_res = {
                    "Symbol": symbol,
                    "Company": symbol.replace(".NS", ""),
                    "Sector": getattr(r, "sector", "Unknown"),
                    "Price": round(price, 2),
                    "Signal": decision_str,
                    "Score": score,
                    "Raw Score": bullish_score,
                    "Confidence": round(confidence, 1),
                    "Entry": round(entry, 2),
                    "Stop Loss": round(sl, 2),
                    "Target 1": round(t1, 2),
                    "Target 2": round(t2, 2),
                    "Risk Reward": f"1:{round(rr, 1)}" if isinstance(rr, (int, float)) else str(rr),
                    "Volume": int(volume),
                    "OI": 0,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                ese = EliteSelectionEngine()
                elite_res = ese.evaluate(processed_res)
                if elite_res is None:
                    trace.append("Elite Selection FAIL")
                    rejection_stage = "Elite Selection (TQI/RR/Conf)"
                    rejected = True
                else:
                    trace.append("Elite Selection PASS")
                    pee = PrecisionEntryEngine()
                    pee_res = pee.evaluate(elite_res)
                    if pee_res is None:
                        trace.append("Precision Entry FAIL")
                        rejection_stage = "Precision Entry"
                        rejected = True
                    else:
                        trace.append("Precision Entry PASS")
                        
            except Exception as e:
                err = str(e)
                if "Validation failed" in err or "False breakout" in err or "MTF" in err:
                    trace.append(f"Institution FAIL ({err})")
                    rejection_stage = "Validation (Institutional/False Breakout)"
                elif "Execution" in err or "Risk check failed" in err or "Validation Check failed" in err:
                    trace.append(f"Execution FAIL ({err})")
                    rejection_stage = "Execution Center"
                else:
                    trace.append(f"Unknown FAIL ({err})")
                    rejection_stage = "Validation (Institutional/False Breakout)"
                rejected = True
        
        print(f"{symbol}")
        for t in trace:
            print(t)
        print("--------------------------------")
        
        if rejected:
            rejection_counts[rejection_stage] += 1
        else:
            passed += 1

    print("\n================================================")
    print("STAGE-WISE REJECTION COUNTS")
    print("================================================\n")
    for k, v in rejection_counts.items():
        print(f"{k}: {v}")
        
    print(f"\nFinal Trades Passed: {passed}")
    
    highest = max(rejection_counts, key=rejection_counts.get)
    print(f"\nSINGLE ENGINE RESPONSIBLE FOR HIGHEST REJECTIONS: {highest} ({rejection_counts[highest]} symbols)")

if __name__ == "__main__":
    run_audit()
