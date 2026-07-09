import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.ranking_engine import RankingEngine
from market.yahoo_provider import YahooFinanceProvider
from market.universe import FNO_UNIVERSE

def audit_buys():
    print("Starting BUY Side Audit...")
    re = RankingEngine()
    yf = YahooFinanceProvider()
    yf.connect()
    
    symbols = [item["symbol"] for item in FNO_UNIVERSE][:20] # Take sample to save time, actually let's do all
    symbols = [item["symbol"] for item in FNO_UNIVERSE]
    
    stats = {"Total": len(symbols), "BULLISH": 0, "BEARISH": 0, "REJECTED": 0}
    all_results = []
    
    print(f"Scanning {len(symbols)} symbols...")
    start_time = time.time()
    
    # We will limit to first 30 for a quick audit, but let's do all to be sure
    for idx, symbol in enumerate(symbols):
        try:
            ohlcv_1d = yf.get_ohlcv(symbol, "1d", "90d")
            ohlcv_1wk = yf.get_ohlcv(symbol, "1wk", "1y")
            
            if not ohlcv_1d or not ohlcv_1wk:
                stats["REJECTED"] += 1
                continue
                
            res = re.evaluate(symbol, ohlcv_1d, ohlcv_1wk)
            
            if res["status"] == "RANKED":
                all_results.append(res)
                if res["direction"] == "BULLISH":
                    stats["BULLISH"] += 1
                else:
                    stats["BEARISH"] += 1
            else:
                stats["REJECTED"] += 1
        except Exception as e:
            stats["REJECTED"] += 1
            
    print(f"\nScan completed in {time.time() - start_time:.2f}s")
    print(f"Stats: {stats}")
    
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    buys = [r for r in all_results if r["direction"] == "BULLISH"]
    sells = [r for r in all_results if r["direction"] == "BEARISH"]
    
    print(f"\nTop 5 BUYS:")
    for b in buys[:5]:
        print(f" {b['symbol']}: Score: {b['score']}, Raw Score: {b['raw_score']}")
        
    print(f"\nTop 5 SELLS:")
    for s in sells[:5]:
        print(f" {s['symbol']}: Score: {s['score']}, Raw Score: {s['raw_score']}")
        
    # Let's check Market Regime penalty
    regime = re.regime_data.get("Market Regime", "UNKNOWN")
    print(f"\nCurrent Market Regime: {regime}")
    
    # Are BUY scores systematically lower?
    avg_buy = sum(b['score'] for b in buys) / max(len(buys), 1)
    avg_sell = sum(s['score'] for s in sells) / max(len(sells), 1)
    
    print(f"Average BUY Score: {avg_buy:.2f}")
    print(f"Average SELL Score: {avg_sell:.2f}")
    
if __name__ == "__main__":
    audit_buys()
