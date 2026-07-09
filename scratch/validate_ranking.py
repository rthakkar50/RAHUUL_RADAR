import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.ranking_engine import RankingEngine
from market.yahoo_provider import YahooFinanceProvider

def test():
    print("Testing Ranking Engine...")
    re = RankingEngine()
    yf = YahooFinanceProvider()
    yf.connect()
    
    symbols = ["RELIANCE.NS", "TCS.NS"]
    for sym in symbols:
        ohlcv_1d = yf.get_ohlcv(sym, "1d", "90d")
        ohlcv_intra = yf.get_ohlcv(sym, "1d", "10d") # mock intra
        if not ohlcv_1d or not ohlcv_intra:
            print(f"No data for {sym}")
            continue
            
        res = re.evaluate(sym, ohlcv_intra, ohlcv_1d)
        print(f"Result for {sym}: Grade: {res.get('grade')}, Score: {res.get('score')}")
        assert "score" in res, "Score missing"
        assert "grade" in res, "Grade missing"
        assert "reason" in res, "Reason missing"

if __name__ == "__main__":
    test()
    print("Validation Successful.")
