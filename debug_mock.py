from scanner.scanner_engine import ScannerEngine
from data.stocks import Stock
from core.decision_engine import DecisionEngine
from unittest.mock import MagicMock
import pandas as pd

stock = Stock(symbol="GODREJPROP.NS", company_name="Godrej", sector="REALTY", is_fno=True, is_nifty50=False)
data_provider = MagicMock()

# create a dummy dataframe with 30 bars
df = pd.DataFrame({
    'Open': [100]*30, 'High': [110]*30, 'Low': [90]*30, 'Close': [105]*30, 'Volume': [1000]*30
})
data_provider.get_ohlcv.return_value = df
data_provider.get_live_price.return_value = 105.0

engine = ScannerEngine(
    data_provider=data_provider,
    trend_engine=MagicMock(),
    momentum_engine=MagicMock(),
    structure_engine=MagicMock(),
    score_engine=MagicMock()
)

# Mock the decision engine to force the bug or see what happens
res = engine.scan(stock, mode="SWING")
print(f"RAW RES decision: {res.signal.value}")
print(f"RAW RES score: {res.total_score}")
