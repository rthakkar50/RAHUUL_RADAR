import inspect
from core.decision_explanation_engine import DecisionExplanationEngine
import json

dee = DecisionExplanationEngine()

def run_test():
    # Mock item dictionary
    item = {
        "_raw_data": {
            "trend": {"score": 85.0},
            "momentum": {"score": 75.0},
            "structure": {"score": 80.0},
            "volume": {"score": 60.0}
        }
    }
    raw_reasons = [
        "ADX Adjusted Confidence: 85.0%",
        "MTCE: Perfect Alignment! Boosting Elite Score (+10)."
    ]
    
    res = dee.explain(signal="BUY", confidence=85.0, elite_score=80.0, raw_reasons=raw_reasons)
    print(json.dumps(res, indent=2))

run_test()
