from core.decision_engine import DecisionEngine
from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult

de = DecisionEngine()
trend = TrendResult(score=2.0, direction="BULLISH", reasons=[], ema20=100.0, ema50=90.0, vwap=95.0)
mom = MomentumResult(score=2.0, direction="BULLISH", reasons=[], rsi=50.0, adx=20.0, plus_di=20.0, minus_di=20.0)
struct = StructureResult(score=2.25, direction="BULLISH", reasons=[], details={})

print(f"SWING: {de.calculate(trend, mom, struct, mode='SWING').decision}")
print(f"OPTIONS: {de.calculate(trend, mom, struct, mode='OPTIONS').decision}")
print(f"INTRADAY: {de.calculate(trend, mom, struct, mode='INTRADAY').decision}")
print(f"None: {de.calculate(trend, mom, struct, mode=None).decision}")
