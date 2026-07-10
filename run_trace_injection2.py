from scanner.scanner_engine import ScannerEngine
from data.stocks import Stock
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from unittest.mock import MagicMock
from datetime import datetime

class MockCandle:
    def __init__(self):
        self.timestamp = datetime.now()
        self.open = 100
        self.high = 110
        self.low = 90
        self.close = 105
        self.volume = 1000

data_provider = MagicMock()
data_provider.get_ohlcv.return_value = [MockCandle() for _ in range(30)]
data_provider.get_live_price.return_value = 105.0

scanner = ScannerEngine(
    data_provider=data_provider,
    trend_engine=TrendEngine(),
    momentum_engine=MomentumEngine(),
    structure_engine=StructureEngine(),
    score_engine=ScoreEngine()
)

# Monkeypatch scanner._enrich_dataframe to avoid AttributeError
import pandas as pd
def _enrich_dataframe(ohlcv_list):
    df = pd.DataFrame([{"Date": c.timestamp, "Open": c.open, "High": c.high, "Low": c.low, "Close": c.close, "Volume": c.volume} for c in ohlcv_list])
    return df
scanner._enrich_dataframe = _enrich_dataframe

stock = Stock(symbol="GODREJPROP.NS", company_name="Godrej", sector="REALTY", is_fno=True, is_nifty50=False)
results = scanner.scan_market([stock], mode="SWING")
res = results[0]
print(f"TRACED SIGNAL: {res.signal.value if hasattr(res.signal, 'value') else res.signal}")
print(f"TRACED TOTAL SCORE: {res.total_score}")
