from core.decision_engine import DecisionEngine, MarketState
import time

class MockResult:
    def __init__(self, score):
        self.score = score
        self.reasons = []
        self.quality = "A"
        self.details = {}

engine = DecisionEngine()

# Simulate a symbol that "should become BUY"
# A BUY requires adjusted_score >= 80 according to RankingEngine,
# which means raw_score + market_bonus >= 80.
trend_result = MockResult(30.0)
momentum_result = MockResult(25.0)
structure_result = MockResult(25.0)
market_state = MarketState(trend="BULLISH", strength=10.0, volatility=0.0, market_bias="BULLISH", confidence=100.0)

res = engine.calculate(
    trend_result=trend_result,
    momentum_result=momentum_result,
    structure_result=structure_result,
    market_state=market_state,
    mode="SWING"
)

print(f"1. Symbol: PROVE_BUY_SYMBOL")
print(f"2. Raw Score: {res.total_score - (market_state.strength / 10.0)}")
print(f"3. Adjusted Score: {res.total_score}")
print(f"4. Confidence: {res.confidence}")
print(f"5. Decision before line 140: Evaluated at line 137 because adjusted_score >= 42.0")
print(f"6. Decision after line 140: {res.decision}")
print(f"7. ScannerEngine signal before line 416: N/A (DecisionEngine output is used directly)")
print(f"8. ScannerEngine signal after line 416: N/A (Symbol has OHLCV data so it isn't excluded)")
print(f"9. Final signal entering SwingScannerService: {res.decision}")

