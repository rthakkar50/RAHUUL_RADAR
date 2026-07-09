import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from application.intraday_scanner_service import IntradayScannerService
from market.yahoo_provider import YahooFinanceProvider
from data.stocks import Stock
from scanner.scanner_engine import ScannerEngine
from ranking.score_engine import ScoreEngine

def run():
    provider = YahooFinanceProvider()
    provider.connect()
    service = IntradayScannerService()
    
    symbols = ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "TCS.NS", "ICICIBANK.NS", "SBI.NS", "BHARTIARTL.NS", "ITC.NS", "L&T.NS", "HINDUNILVR.NS"]
    stock_list = [Stock(symbol=sym, company_name=sym, sector="N/A", is_fno=True, is_nifty50=True) for sym in symbols]
    
    scanner = ScannerEngine(
        data_provider=provider,
        trend_engine=service.engines["trend"],
        momentum_engine=service.engines["momentum"],
        structure_engine=service.engines["structure"],
        score_engine=ScoreEngine(),
        sector_engine=None
    )
    
    # Enable DEBUG implicitly because it's true in scanner_engine.py
    results = scanner.scan_market(stock_list, mode="INTRADAY")
    
if __name__ == "__main__":
    run()
