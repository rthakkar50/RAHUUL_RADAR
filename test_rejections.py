import sys
from backtest.backtest_orchestrator import BacktestOrchestrator
from core.master_signal_pipeline import MasterSignalPipeline

original_run = MasterSignalPipeline.run

rejections = []

def intercepted_run(self, *args, **kwargs):
    res = original_run(self, *args, **kwargs)
    
    entry = res.get("recommended_entry", 0.0)
    sl = res.get("stop_loss", 0.0)
    t1 = res.get("target_1", 0.0)
    
    if entry == 0.0 or sl == 0.0 or t1 == 0.0:
        rejections.append({
            "symbol": kwargs.get("symbol"),
            "decision": kwargs.get("decision"),
            "entry": entry,
            "sl": sl,
            "t1": t1,
            "pipeline_status": res.get("Pipeline Status", ""),
            "status": res.get("status", ""),
            "alignment_report": res.get("alignment_report", res.get("report", []))
        })
    return res

MasterSignalPipeline.run = intercepted_run

orchestrator = BacktestOrchestrator()
orchestrator.run(["HDFCBANK.NS"], "2025-01-01", "2025-06-30", "1d")

for r in rejections:
    print(r["alignment_report"])
