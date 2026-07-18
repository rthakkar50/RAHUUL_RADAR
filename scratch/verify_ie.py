import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategy.intraday_engine import IntradayEngine
from market.yahoo_provider import YahooFinanceProvider

dp = YahooFinanceProvider()
dp.connect()
symbol = "TCS.NS"
ohlcv_intra = dp.get_ohlcv(symbol, interval="5m", period="5d")
ohlcv_15m = dp.get_ohlcv(symbol, interval="15m", period="5d")
ohlcv_1h = dp.get_ohlcv(symbol, interval="1h", period="1mo")
ohlcv_1d = dp.get_ohlcv(symbol, interval="1d", period="1mo")

ie = IntradayEngine()
res = ie.evaluate(symbol, ohlcv_intra, ohlcv_15m, ohlcv_1h, ohlcv_1d, "BULLISH")
print(res)
