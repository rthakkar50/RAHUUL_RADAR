import yfinance as yf

symbols = ['GMRINFRA.NS', 'GMRAIRPORT.NS', 'LTIM.NS', 'PEL.NS', 'PIRAMALENT.NS', 'GUJGASLTD.NS', 'TATAMOTORS.NS', 'TATAMOTOR.NS']

for sym in symbols:
    ticker = yf.Ticker(sym)
    try:
        hist = ticker.history(period="1d")
        if not hist.empty:
            print(f"{sym} -> OK (Last Close: {hist['Close'].iloc[-1]})")
        else:
            print(f"{sym} -> FAILED (No data)")
    except Exception as e:
        print(f"{sym} -> ERROR: {e}")
