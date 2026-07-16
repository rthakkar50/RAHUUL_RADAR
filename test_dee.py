from core.decision_explanation_engine import DecisionExplanationEngine
import json

dee = DecisionExplanationEngine()

raw_reasons = [
    "Trend Weight (Max 30) Score: 24.50",
    "Momentum Weight (Max 25) Score: 18.00",
    "Structure Weight (Max 25) Score: 20.00",
    "ADX Adjusted Confidence: 85.0%",
    "MTCE: Perfect Alignment! Boosting Elite Score (+10).",
    "Excellent R/R"
]

res = dee.explain(signal="BUY", confidence=85.0, elite_score=80.0, raw_reasons=raw_reasons)
print(json.dumps(res, indent=2))
