import sys
import logging
logging.basicConfig(level=logging.ERROR)
from strategy.ranking_engine import RankingEngine
from application.swing_scanner_service import SwingScannerService
from market.yahoo_provider import YahooFinanceProvider
from market.universe import FNO_UNIVERSE
from data.stocks import TOP_50_STOCKS

def run_boundary_tests(engine):
    boundaries = [49.9, 50.0, 59.9, 60.0, 69.9, 70.0, 79.9, 80.0, 89.9, 90.0]
    results = []
    for score in boundaries:
        grade = engine.get_grade(score)
        results.append(f"Score {score} -> Grade {grade}")
    return results

def generate_proof():
    provider = YahooFinanceProvider()
    provider.connect()
    engine = RankingEngine()
    
    reports = {}
    
    # Boundary Tests
    boundary_results = run_boundary_tests(engine)
    reports["Boundary Tests"] = boundary_results
    
    # Modes
    modes = {
        "1. NIFTY 50": ([s.symbol for s in TOP_50_STOCKS], "5m", "5d"),
        "2. NSE F&O": ([item["symbol"] for item in FNO_UNIVERSE], "5m", "5d"),
        "3. Swing": ([item["symbol"] for item in FNO_UNIVERSE], "1d", "90d"),
        "4. Intraday": ([s.symbol for s in TOP_50_STOCKS], "15m", "5d")
    }
    
    for mode_name, (symbols, intra_tf, intra_lookback) in modes.items():
        print(f"Running {mode_name}...")
        provider.pre_cache(symbols, intra_tf, intra_lookback)
        provider.pre_cache(symbols, "1d", "90d")
        
        all_results = []
        for sym in symbols:
            try:
                if intra_tf == "1d":
                    o_intra = provider.get_ohlcv(sym, "1d", "90d")
                else:
                    o_intra = provider.get_ohlcv(sym, intra_tf, intra_lookback)
                o_1d = provider.get_ohlcv(sym, "1d", "90d")
                if not o_intra or not o_1d: continue
                res = engine.evaluate(sym, o_intra, o_1d)
                if res and res.get("status") == "RANKED":
                    all_results.append(res)
            except Exception as e:
                pass
                
        all_results.sort(key=lambda x: x["score"], reverse=True)
        reports[mode_name] = all_results
        
    return reports

if __name__ == "__main__":
    reports = generate_proof()
    
    with open("GRADE_PRECISION_REPORT.md", "w") as f:
        f.write("# MASTER-52.2: Grade Precision Report\n\n")
        
        f.write("## 1. Root Cause & Solution\n")
        f.write("- **Root Cause**: The raw internal score (e.g. 49.96) was being passed directly to `get_grade()`, which evaluated `< 50` and assigned 'Weak'. However, the score returned to the UI dictionary was `round(final_score, 1)`, which became `50.0`. This caused the UI to show '50.0' alongside 'Weak'.\n")
        f.write("- **Files Changed**: `strategy/ranking_engine.py`\n")
        f.write("- **Lines Changed**: 395-403\n")
        f.write("- **Solution applied**: We calculate `rounded_final_score = round(final_score, 1)` *first*, and then strictly use that exact same value for BOTH display (`score: rounded_final_score`) and grading (`grade: self.get_grade(rounded_final_score)`). Now, the UI and the grading engine mathematically share the identical float precision.\n\n")
        
        f.write("## 2. Boundary Test Results\n")
        f.write("```text\n")
        for res in reports.pop("Boundary Tests"):
            f.write(res + "\n")
        f.write("```\n\n")
        
        f.write("## 3. Real-World Output Consistency Verification\n")
        for mode, all_results in reports.items():
            f.write(f"### {mode}\n")
            
            # Verifications
            grade_check = "PASS"
            failed_examples = []
            
            # Find borderline examples to show Before/After theoretically
            for r in all_results:
                score = r['score']
                grade = r['grade']
                expected = "Weak"
                if score >= 90: expected = "A+"
                elif score >= 80: expected = "A"
                elif score >= 70: expected = "B"
                elif score >= 60: expected = "C"
                elif score >= 50: expected = "Watch"
                if grade != expected:
                    grade_check = f"FAIL: {r['symbol']} scored {score} but got {grade}"
                    failed_examples.append(grade_check)
            
            if failed_examples:
                f.write(f"Consistency Check: **FAIL**\n")
                for err in failed_examples:
                    f.write(f"- {err}\n")
            else:
                f.write(f"Consistency Check (Display == Grade rules): **PASS** across {len(all_results)} evaluated stocks.\n")
            
            f.write("\n")
            
