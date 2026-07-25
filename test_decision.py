from core.decision_engine import DecisionEngine
from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult

de = DecisionEngine()
res = de.calculate(
    trend_result=TrendResult(score=15, direction="NEUTRAL", ema20=0, ema50=0, vwap=0, details={}),
    momentum_result=MomentumResult(score=12.5, direction="NEUTRAL", rsi=50, adx=20, plus_di=10, minus_di=10, details={}),
    structure_result=StructureResult(score=12.5, current_structure="SIDEWAYS", key_levels=[], details={}),
    market_state=None,
    mode="SWING"
)
print("Calculated Confidence:", res.confidence)
