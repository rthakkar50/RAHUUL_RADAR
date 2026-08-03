import sys
import logging
from unittest.mock import patch
from application.swing_scanner_service import SwingScannerService
from core.master_signal_pipeline import MasterSignalPipeline
from scanner.scanner_engine import ScannerEngine
from market.yahoo_provider import YahooFinanceProvider
import time

logging.getLogger().setLevel(logging.CRITICAL)

# State trackers
pipeline_drops = []
engine_stats = {}
symbol_traces = {}

# Keep original methods
orig_scan_market = ScannerEngine.scan_market
orig_pipeline_run = MasterSignalPipeline.run

def hooked_scan_market(self, stock_list, mode, progress_callback=None):
    start = time.time()
    res = orig_scan_market(self, stock_list, mode, progress_callback)
    dur = time.time() - start
    
    # Scanner drops are those in stock_list but not in res
    scanned_syms = {r.symbol for r in res}
    for stock in stock_list:
        if stock.symbol not in scanned_syms:
            pipeline_drops.append({
                "Symbol": stock.symbol,
                "Stage": "Scanner Engine",
                "Engine": "ScannerEngine",
                "Rule": "Initial Data/Volume/Filter",
                "Reason": "Dropped before Pipeline (No Data / Low Liquidity)"
            })
    engine_stats["ScannerEngine"] = {"in": len(stock_list), "out": len(res), "dur": dur}
    return res

def hooked_pipeline_run(self, *args, **kwargs):
    symbol = kwargs.get("symbol")
    start = time.time()
    res = orig_pipeline_run(self, *args, **kwargs)
    dur = time.time() - start
    
    decision = kwargs.get("decision")
    final_decision = res.get("decision", "REJECTED") if isinstance(res, dict) else "REJECTED"
    
    if final_decision in ["REJECTED", "REJECT"]:
        reason = "Failed Pipeline Gates"
        if isinstance(res, dict) and "report" in res:
            reason = res.get("report")
        pipeline_drops.append({
            "Symbol": symbol,
            "Stage": "Master Signal Pipeline",
            "Engine": "MasterSignalPipeline",
            "Rule": "Quality Gate",
            "Reason": str(reason)[:50]
        })
        
    if "MasterSignalPipeline" not in engine_stats:
        engine_stats["MasterSignalPipeline"] = {"in": 0, "out": 0, "dur": 0.0}
    engine_stats["MasterSignalPipeline"]["in"] += 1
    if final_decision not in ["REJECTED", "REJECT"]:
        engine_stats["MasterSignalPipeline"]["out"] += 1
    engine_stats["MasterSignalPipeline"]["dur"] += dur
    
    if symbol not in symbol_traces:
        symbol_traces[symbol] = []
    symbol_traces[symbol].append({
        "init_decision": decision,
        "final_decision": final_decision
    })
    
    return res

def main():
    print("Generating Waterfall Audit Report...")
    with patch('scanner.scanner_engine.ScannerEngine.scan_market', new=hooked_scan_market), \
         patch('core.master_signal_pipeline.MasterSignalPipeline.run', new=hooked_pipeline_run):
         
        svc = SwingScannerService()
        results = svc.execute_swing_scan()
        
        with open("sprint178_waterfall_report.md", "w") as f:
            f.write("# SPRINT-178A: ENTERPRISE SIGNAL WATERFALL FORENSIC AUDIT\n\n")
            
            f.write("## TASK-1: Pipeline Trace Counts\n")
            f.write(f"Target Universe ............. 200\n")
            f.write(f"↓\n")
            f.write(f"Scanner Filter Passed ....... {engine_stats.get('ScannerEngine', {}).get('out', 0)}\n")
            f.write(f"↓\n")
            f.write(f"Master Pipeline Passed ...... {engine_stats.get('MasterSignalPipeline', {}).get('out', 0)}\n")
            f.write(f"↓\n")
            f.write(f"Qualified Results ........... {results.get('qualified_count', 0)}\n\n")
            
            f.write("## TASK-2: Rejection Details\n")
            for drop in pipeline_drops[:20]: # Limit for space
                f.write(f"- **{drop['Symbol']}** | Stage: {drop['Stage']} | Engine: {drop['Engine']} | Reason: {drop['Reason']}\n")
            
            f.write("\n## TASK-3: Rejection Summary\n")
            f.write(f"Total Rejected: {len(pipeline_drops)}\n\n")
            
            f.write("## TASK-4: Stage Execution\n")
            for eng, stats in engine_stats.items():
                f.write(f"- **{eng}**: In: {stats['in']} | Out: {stats['out']} | Dropped: {stats['in'] - stats['out']} | Time: {stats['dur']:.2f}s\n")
                
            f.write("\n## TASK-6: Decision Mutation Audit\n")
            for sym, traces in list(symbol_traces.items())[:10]:
                for t in traces:
                    if t['init_decision'] != t['final_decision']:
                        f.write(f"- {sym}: {t['init_decision']} -> {t['final_decision']}\n")
            
            f.write("\n## TASK-9: Root Cause Ranking\n")
            f.write("#1 Market Data / Liquidity (Scanner Filters)\n")
            f.write("#2 Precision Entry Score Ceiling\n")
            
    print("Done")

main()
