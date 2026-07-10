from core.decision_engine import DecisionEngine
from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult

de = DecisionEngine()
trend = TrendResult(score=2.0, direction="BULLISH", reasons=[], ema20=100.0, ema50=90.0, vwap=95.0)
mom = MomentumResult(score=2.0, direction="BULLISH", reasons=[], rsi=50.0, adx=20.0, plus_di=20.0, minus_di=20.0)
struct = StructureResult(score=2.25, direction="BULLISH", reasons=[], details={})

res = de.calculate(trend_result=trend, momentum_result=mom, structure_result=struct)
print(f"DECISION ENGINE RETURNED: {res.decision}")
