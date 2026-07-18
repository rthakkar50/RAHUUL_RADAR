import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83c_validation.py", "r") as f:
    content = f.read()

bad_init = "scanner = ScannerEngine()"
good_init = """from market.yahoo_provider import YahooFinanceProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine

scanner = ScannerEngine(YahooFinanceProvider(), TrendEngine(), MomentumEngine(), StructureEngine(), ScoreEngine())"""

content = content.replace(bad_init, good_init)

with open("scratch/sprint83c_validation.py", "w") as f:
    f.write(content)

