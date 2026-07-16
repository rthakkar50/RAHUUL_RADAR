import sys
sys.path.insert(0, '.')
from core.decision_engine import DecisionEngine
from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult

de = DecisionEngine()
# Max possible scores to get 80+
tr = TrendResult(score=30, direction="BULLISH", ema20=100, ema50=90, vwap=95, reasons=[])
mr = MomentumResult(score=25, rsi=60, adx=30, macd_bullish=True, reasons=[])
sr = StructureResult(score=25, condition="BULLISH", reasons=[], details={})

res = de.calculate(tr, mr, sr, mode="SWING")
print("Adjusted Score:", res.adjusted_score)
print("Decision:", res.decision)
