import sys, os
sys.path.append(os.getcwd())
import yfinance as yf
print(yf.download("DIVISLAB.NS", period="1mo").tail(2))
