import sys, os
import yfinance as yf
sys.path.append(os.getcwd())
print(yf.download("EXIDEIND.NS", period="1mo").tail(3))
