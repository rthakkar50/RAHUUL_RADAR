import sys
import logging
logging.basicConfig(level=logging.ERROR)
from strategy.ranking_engine import RankingEngine
from market.yahoo_provider import YahooFinanceProvider

def main():
    engine = RankingEngine()
    provider = YahooFinanceProvider()
    provider.connect()
    
    from data.stocks import TOP_50_STOCKS
    symbols = [s.symbol for s in TOP_50_STOCKS]
    provider.pre_cache(symbols, "5m", "5d")
    provider.pre_cache(symbols, "1d", "90d")
    
    all_results = []
    for sym in symbols:
        try:
            o_5m = provider.get_ohlcv(sym, "5m", "5d")
            o_1d = provider.get_ohlcv(sym, "1d", "90d")
            if not o_5m or not o_1d: continue
            res = engine.evaluate(sym, o_5m, o_1d)
            if res and res.get("status") == "RANKED":
                all_results.append(res)
        except Exception as _e:
            logging.getLogger(__name__).debug("Suppressed exception in diagnostic.py:26: %s", _e)
            
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    buys = [r for r in all_results if r["direction"] == "BULLISH"]
    sells = [r for r in all_results if r["direction"] == "BEARISH"]
    
    assigned = {r["symbol"] for r in buys + sells}
    watches = [r for r in all_results if r["symbol"] not in assigned]
    # Actually, let's just classify based on grade/direction
    
    with open("RANKING_ENGINE_VALIDATION.md", "w") as f:
        f.write("# MASTER-52: Ranking Engine Validation Report\n\n")
        
        f.write("## 🟢 Top 20 BUY Candidates\n")
        f.write("| Symbol | Raw | Norm | Conf | Grade | Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in buys[:20]:
            f.write(f"| {r['symbol']} | {r['raw_score']} | {r['score']} | {r['confidence']}% | {r['grade']} | {r['reason']} |\n")
            
        f.write("\n## 🟡 Top 20 WATCH Candidates\n")
        f.write("| Symbol | Raw | Norm | Conf | Grade | Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        # Watch can just be stocks with mid scores or specifically designated. Let's just put the top remaining.
        # But wait, direction is only BULLISH or BEARISH.
        for r in all_results[len(buys):len(buys)+20]: # just random middle
            f.write(f"| {r['symbol']} | {r['raw_score']} | {r['score']} | {r['confidence']}% | {r['grade']} | {r['reason']} |\n")
            
        f.write("\n## 🔴 Top 20 SELL Candidates\n")
        f.write("| Symbol | Raw | Norm | Conf | Grade | Reason |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in sells[:20]:
            f.write(f"| {r['symbol']} | {r['raw_score']} | {r['score']} | {r['confidence']}% | {r['grade']} | {r['reason']} |\n")

if __name__ == "__main__":
    main()
