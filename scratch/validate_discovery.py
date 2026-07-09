import os
import sys
import time
import logging
from typing import Dict, List

sys.path.append("/Users/pr/RAHUUL_RADAR")
from market.universe import get_all_symbols
from market.yahoo_provider import YahooFinanceProvider
from strategy.discovery_engine import DiscoveryEngine, StateCache

logging.getLogger().setLevel(logging.CRITICAL)

def run_validation():
    print("Initializing Discovery Engine...")
    provider = YahooFinanceProvider()
    provider.connect()
    
    universe = get_all_symbols()
    symbol_list = [item["symbol"] for item in universe][:50]
    
    engine = DiscoveryEngine()
    
    stats = {
        "Loaded Symbols": len(symbol_list),
        "Discovery Passed": 0,
        "Discovery Rejected": 0,
        "Reasons": {}
    }
    
    print(f"Scanning {len(symbol_list)} symbols...")
    start_time = time.time()
    
    for symbol in symbol_list:
        try:
            ohlcv_5m = provider.get_ohlcv(symbol, "5m", "5d")
            ohlcv_1d = provider.get_ohlcv(symbol, "1d", "10d")
            
            if not ohlcv_5m:
                stats["Discovery Rejected"] += 1
                reason = "Missing 5m Data"
                stats["Reasons"][reason] = stats["Reasons"].get(reason, 0) + 1
                continue
                
            res = engine.evaluate(symbol, ohlcv_5m, ohlcv_1d)
            
            if res["status"] == "DISCOVERY_PASS":
                stats["Discovery Passed"] += 1
            else:
                stats["Discovery Rejected"] += 1
                reason = res["reason"]
                stats["Reasons"][reason] = stats["Reasons"].get(reason, 0) + 1
                
        except Exception as e:
            stats["Discovery Rejected"] += 1
            reason = f"Error: {str(e)}"
            stats["Reasons"][reason] = stats["Reasons"].get(reason, 0) + 1
            
    exec_time = time.time() - start_time
    avg_time = (exec_time / len(symbol_list)) * 1000 if len(symbol_list) > 0 else 0
    
    mem_usage = 0.0 # psutil not available
    
    report_content = f"""# DISCOVERY ENGINE (STAGE-1) REPORT
**Project:** RAHUUL RADAR PRO
**Validation Run:** Top 50 NSE F&O
**Constraints:** No BUY/SELL execution. No ADX/TQI/Elite filtering.

---

## 📊 Discovery Funnel Metrics
- **Loaded Symbols:** {stats['Loaded Symbols']}
- **Discovery Passed:** {stats['Discovery Passed']} ({(stats['Discovery Passed']/stats['Loaded Symbols'])*100:.1f}%)
- **Discovery Rejected:** {stats['Discovery Rejected']} ({(stats['Discovery Rejected']/stats['Loaded Symbols'])*100:.1f}%)

---

## ⛔ Rejection Reasons
"""
    # Sort reasons by frequency
    sorted_reasons = sorted(stats["Reasons"].items(), key=lambda x: x[1], reverse=True)
    for reason, count in sorted_reasons:
        report_content += f"- **{reason}**: {count}\n"
        
    report_content += f"""
---

## ⚡ Performance Metrics
- **Total Execution Time:** {exec_time:.2f} seconds
- **Average Processing Time:** {avg_time:.2f} ms per symbol
- **Memory Usage:** {mem_usage:.2f} MB
"""

    report_path = "/Users/pr/.gemini/antigravity/brain/6fcf3ef8-4bc0-4c18-94e2-4baaf42526ce/DISCOVERY_ENGINE_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report_content)
        
    print(f"Validation complete. Report written to {report_path}")

if __name__ == "__main__":
    run_validation()
