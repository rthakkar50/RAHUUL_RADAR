import sys
from backtest.backtest_orchestrator import BacktestOrchestrator
from backtest.historical_data_provider import HistoricalDataProvider
from core.master_signal_pipeline import MasterSignalPipeline
from scanner.scanner_engine import ScannerEngine
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.relative_strength_engine import RelativeStrengthEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.adaptive_strategy_engine import AdaptiveStrategyEngine
from core.master_ai_decision_engine import MasterAIDecisionEngine
from ranking.score_engine import ScoreEngine

class DebugOrchestrator(BacktestOrchestrator):
    def run(self, symbols, start_date, end_date, timeframe):
        data_provider = HistoricalDataProvider(start_date, end_date, timeframe)
        data_provider._fetch_symbol("^NSEI")
            
        engines = {
            "trend": TrendEngine(),
            "momentum": MomentumEngine(),
            "structure": StructureEngine(),
            "relative_strength": RelativeStrengthEngine(),
            "sector_rotation": SectorRotationEngine(),
            "adaptive_strategy": AdaptiveStrategyEngine.get_instance() if hasattr(AdaptiveStrategyEngine, 'get_instance') else AdaptiveStrategyEngine(),
            "master_ai": MasterAIDecisionEngine()
        }
        pipeline = MasterSignalPipeline(engines)
        
        score_engine = ScoreEngine()
        scanner = ScannerEngine(
            data_provider=data_provider,
            trend_engine=engines["trend"],
            momentum_engine=engines["momentum"],
            structure_engine=engines["structure"],
            score_engine=score_engine
        )
        
        rejected_trades = []
        
        for i in range(data_provider.get_total_steps()):
            current_date = data_provider.get_date_at(i)
            data_provider.current_date_index = i
            
            for symbol in symbols:
                raw_results = scanner.scan_market([symbol], data_provider)
                if not raw_results:
                    continue
                r = raw_results[0]
                price = getattr(r, 'price', 0.0)
                decision_str = getattr(r.signal, 'value', str(r.signal))
                
                if decision_str not in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
                    continue
                    
                breakdown = getattr(r, 'breakdown_detail', {}) or {}
                atr_val = breakdown.get("atr", 0.0)
                structure_details = breakdown.get("structure", {})
                
                pipeline_res = pipeline.run(
                    symbol=symbol,
                    price=price,
                    decision=decision_str,
                    confidence=getattr(r, 'confidence', 80.0),
                    atr=atr_val,
                    structure={"details": structure_details},
                    trend={"score": getattr(r, 'trend_score', 50.0)},
                    momentum={"score": getattr(r, 'momentum_score', 50.0)},
                    structure_score={"score": getattr(r, 'structure_score', 50.0)},
                    volume={"score": getattr(r, 'volume_score', 50.0)},
                    risk={"score": getattr(r, 'risk_score', 50.0)},
                    relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)}
                )
                
                entry = pipeline_res.get("recommended_entry", 0.0)
                sl = pipeline_res.get("stop_loss", 0.0)
                t1 = pipeline_res.get("target_1", 0.0)
                t2 = pipeline_res.get("target_2", 0.0)

                if entry == 0.0 or sl == 0.0 or t1 == 0.0:
                    rejected_trades.append({
                        "symbol": symbol,
                        "decision": decision_str,
                        "entry": entry,
                        "sl": sl,
                        "t1": t1,
                        "status": pipeline_res.get("Pipeline Status") or pipeline_res.get("status"),
                        "alignment_report": pipeline_res.get("alignment_report") or pipeline_res.get("report", [])
                    })
                    continue
        
        return rejected_trades

orchestrator = DebugOrchestrator()
rejected = orchestrator.run(["HDFCBANK.NS"], "2025-01-01", "2025-06-30", "1d")

reason_counts = {"entry_zero": 0, "sl_zero": 0, "t1_zero": 0, "all_zero": 0}
print(f"Total Rejected: {len(rejected)}")
for idx, r in enumerate(rejected):
    if r["entry"] == 0.0 and r["sl"] == 0.0 and r["t1"] == 0.0:
        reason_counts["all_zero"] += 1
        print(f"{idx+1}. {r['symbol']} | Decision: {r['decision']} | Values: Entry=0.0, SL=0.0, T1=0.0 | Status: {r['status']}")
        if r['alignment_report']:
            for m in r['alignment_report']:
                if "REJECT" in m or "FAIL" in m or "ERROR" in m or "INVALID" in m:
                    print("   -", m)
    else:
        if r["entry"] == 0.0: reason_counts["entry_zero"] += 1
        if r["sl"] == 0.0: reason_counts["sl_zero"] += 1
        if r["t1"] == 0.0: reason_counts["t1_zero"] += 1
        print(f"{idx+1}. {r['symbol']} | Decision: {r['decision']} | Values: Entry={r['entry']}, SL={r['sl']}, T1={r['t1']} | Status: {r['status']}")
    
print("Reason Counts:", reason_counts)

