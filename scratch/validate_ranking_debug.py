import os
import sys
import time
import logging
import traceback

sys.path.append("/Users/pr/RAHUUL_RADAR")
from market.universe import get_all_symbols
from market.yahoo_provider import YahooFinanceProvider
from strategy.ranking_engine import RankingEngine

logging.getLogger().setLevel(logging.CRITICAL)

def run_ranking_test():
    print("Initializing Intraday V2 Ranking Engine Test...")
    provider = YahooFinanceProvider()
    provider.connect()
    
    universe = get_all_symbols()
    symbol_list = [item["symbol"] for item in universe][:5]
    
    ranking_engine = RankingEngine()
    
    results = []
    failed_symbols = 0
    
    for symbol in symbol_list:
        try:
            ohlcv_5m = provider.get_ohlcv(symbol, "5m", "5d")
            ohlcv_1d = provider.get_ohlcv(symbol, "1d", "90d")
            
            if not ohlcv_5m or not ohlcv_1d:
                print(f"{symbol} failed: No Data")
                failed_symbols += 1
                continue
                
            res = ranking_engine.evaluate(symbol, ohlcv_5m, ohlcv_1d)
            if res["status"] == "RANKED":
                results.append(res)
            else:
                print(f"{symbol} failed: {res}")
                failed_symbols += 1
        except Exception as e:
            print(f"{symbol} threw exception: {e}")
            traceback.print_exc()
            failed_symbols += 1
            
if __name__ == "__main__":
    run_ranking_test()
