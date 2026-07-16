from core.decision_engine import DecisionEngine
from core.models import MarketState

engine = DecisionEngine()
# A symbol that should become BUY (e.g., score >= 80)
class MockResult:
    def __init__(self, score):
        self.score = score
        self.reasons = []
        self.quality = "A"
        self.details = {}

trend_result = MockResult(30.0)
momentum_result = MockResult(30.0)
structure_result = MockResult(30.0)
market_state = MarketState("BULLISH", 10.0)

res = engine.calculate(
    trend_result=trend_result,
    momentum_result=momentum_result,
    structure_result=structure_result,
    market_state=market_state,
    mode="SWING"
)

print(f"1. Symbol: TEST_SYMBOL")
print(f"2. Raw Score: {res.raw_score}")
print(f"3. Adjusted Score: {res.total_score}")
print(f"4. Confidence: {res.confidence}")
print(f"5. Decision before line 140: (Determined by condition at line 136)")
print(f"6. Decision after line 140: {res.decision}")
