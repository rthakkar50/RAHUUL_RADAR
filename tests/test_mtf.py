import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.stocks import Stock
from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from scanner.scanner_engine import ScannerEngine
from utils.logger import get_logger

logger = get_logger(__name__)

def test_mtf():
    print("\n--- Running MTF Engine Test ---")
    
    provider = YahooFinanceProvider()
    provider.connect()
    trend = TrendEngine()
    momentum = MomentumEngine()
    structure = StructureEngine()
    score = ScoreEngine()
    
    scanner = ScannerEngine(provider, trend, momentum, structure, score)
    
    # Test on a few stocks
    stocks = [
        Stock("RELIANCE.NS", "Reliance", "Energy", True, True),
        Stock("TCS.NS", "TCS", "IT", True, True)
    ]
    
    results = scanner.scan_market(stocks)
    
    print("\n--- SCAN RESULTS ---")
    for res in results:
        mtf_star = "⭐" if getattr(res, "mtf_score", 0) > 0 else ""
        print(f"[{res.signal}] {res.symbol} {mtf_star} | Score: {res.total_score} | MTF Score: {getattr(res, 'mtf_score', 0)}")
    
    print("----------------------------\n")

if __name__ == "__main__":
    test_mtf()
