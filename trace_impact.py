import sys
import logging

class MockLogger:
    def __getattr__(self, item):
        return lambda *args, **kwargs: None

import types
mock_loguru = types.ModuleType("loguru")
mock_loguru.logger = MockLogger()
sys.modules["loguru"] = mock_loguru

class MockPsutilProcess:
    def memory_info(self):
        class Mem:
            rss = 0
        return Mem()
    def cpu_percent(self):
        return 0.0

mock_psutil = types.ModuleType("psutil")
mock_psutil.Process = lambda *args, **kwargs: MockPsutilProcess()
sys.modules["psutil"] = mock_psutil

from config.config import AppConfig
from core.decision_engine import DecisionEngine
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from core.sector_engine import SectorEngine
from market.yahoo_provider import YahooFinanceProvider
from scanner.scanner_engine import ScannerEngine
from market.universe import FNO_UNIVERSE
from data.stocks import Stock

logging.basicConfig(level=logging.ERROR)

cfg = AppConfig()
cfg.load()
data_provider = YahooFinanceProvider()
data_provider.connect()
trend_engine = TrendEngine()
momentum_engine = MomentumEngine()
structure_engine = StructureEngine()
score_engine = ScoreEngine()
sector_engine = SectorEngine(data_provider)

scanner = ScannerEngine(
    data_provider=data_provider,
    trend_engine=trend_engine,
    momentum_engine=momentum_engine,
    structure_engine=structure_engine,
    score_engine=score_engine,
    sector_engine=sector_engine
)
scanner.config = cfg 

stock_list = []
for item in FNO_UNIVERSE:
    sym = item["symbol"]
    if not sym.endswith(".NS"): sym += ".NS"
    sector = item.get("sector", "Unknown")
    company = item.get("company_name", sym.replace(".NS", ""))
    stock_list.append(Stock(symbol=sym, company_name=company, sector=sector, is_fno=True, is_nifty50=False))

final_buy = 0
final_sell = 0

original_calculate = scanner.decision_engine.calculate
def tracking_calculate(self, *args, **kwargs):
    global final_buy, final_sell
    res = original_calculate(*args, **kwargs)
    if res.decision == "BUY": final_buy += 1
    if res.decision == "SELL": final_sell += 1
    return res

scanner.decision_engine.calculate = types.MethodType(tracking_calculate, scanner.decision_engine)

try:
    results = scanner.scan_market(stock_list=stock_list, mode="SWING")
except Exception as e:
    pass

print(f"Final BUY entering UI logic: {final_buy}")
print(f"Final SELL entering UI logic: {final_sell}")
