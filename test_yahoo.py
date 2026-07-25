from providers.yahoo_provider import YahooProvider
yp = YahooProvider()
data = yp.get_ohlcv("RELIANCE.NS", interval="1d", period="3mo")
print(type(data))
print(len(data))
if data:
    item = data[-1]
    if isinstance(item, dict):
        print(item)
    else:
        print(item.__dict__)
