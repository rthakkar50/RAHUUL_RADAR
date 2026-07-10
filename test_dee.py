from core.trend_engine import TrendResult
from core.momentum_engine import MomentumResult
from core.structure_engine import StructureResult
from core.decision_engine import DecisionEngine, MarketState

# GodrejProp values
trend_result = TrendResult(score=30.0, direction="BULLISH", reasons=["Trend Bullish"])
momentum_result = MomentumResult(score=25.0, direction="BULLISH", reasons=["Mom Bullish"])
structure_result = StructureResult(score=24.0, direction="BULLISH", reasons=["Struct Bullish"])
market_state = MarketState(trend="BULLISH", strength=0.0, volatility=0.0, market_bias="BULLISH", confidence=100.0)

dee = DecisionEngine()
res = dee.calculate(
    trend_result=trend_result,
    momentum_result=momentum_result,
    structure_result=structure_result,
    market_state=market_state,
    mode="SWING"
)

print(f"adjusted_score: {res.adjusted_score}")
print(f"decision: {res.decision}")
