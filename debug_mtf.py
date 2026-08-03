import pandas as pd
from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.mtf_engine import MtfEngine
import logging

logging.basicConfig(level=logging.ERROR)

def _enrich_dataframe(ohlcv_list):
    if not ohlcv_list:
        return pd.DataFrame()
    df = pd.DataFrame([{'Date': c.timestamp, 'Open': c.open, 'High': c.high, 'Low': c.low, 'Close': c.close, 'Volume': c.volume} for c in ohlcv_list])
    df.set_index('Date', inplace=True)
    return df

symbol = "M&MFIN.NS"
print(f"Tracing MTF Engine Inputs for {symbol}")

dp = YahooFinanceProvider()
dp.connect()

# 1. Weekly Data
ohlcv_weekly = dp.get_ohlcv(symbol, interval="1wk", period="1y")
df_weekly = _enrich_dataframe(ohlcv_weekly)

# 2. Daily Data
ohlcv_daily = dp.get_ohlcv(symbol, interval="1d", period="1y")
df_daily = _enrich_dataframe(ohlcv_daily)

# 3. 4H Data
ohlcv_1h = dp.get_ohlcv(symbol, interval="1h", period="1mo")
df_4h = pd.DataFrame()
if ohlcv_1h and len(ohlcv_1h) > 0:
    df_1h = _enrich_dataframe(ohlcv_1h)
    df_4h = df_1h.resample('4h').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna().reset_index()

# Evaluate Trends
mtf = MtfEngine()
w_trend = mtf._evaluate_trend(df_weekly)
d_trend = mtf._evaluate_trend(df_daily)
h4_trend = mtf._evaluate_trend(df_4h)

print(f"Weekly Trend Value: {w_trend}")
print(f"Daily Trend Value: {d_trend}")
print(f"4H Trend Value: {h4_trend}")

# Check sizes
print(f"df_weekly size: {len(df_weekly)}")
print(f"df_daily size: {len(df_daily)}")
print(f"df_4h size: {len(df_4h)}")
