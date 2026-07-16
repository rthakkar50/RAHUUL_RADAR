from core.decision_explanation_engine import DecisionExplanationEngine
import json

dee = DecisionExplanationEngine()

raw_reasons = [
    "Trend Weight (Max 30) Score: 3.50",
    "Momentum Weight (Max 25) Score: 4.00",
    "Structure Weight (Max 25) Score: 5.00",
    "ADX < 20 Sideways Filter: Downgrading SELL to WATCH.",
    "MTCE: Partial Alignment. Keeping SELL in Balanced mode.",
    "Poor R/R"
]

res = dee.explain(signal="SELL", confidence=65.0, elite_score=40.0, raw_reasons=raw_reasons)
print(json.dumps(res, indent=2))
