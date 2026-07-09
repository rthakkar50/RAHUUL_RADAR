"""
Centralized weight configuration for RAHUUL_RADAR scoring engine.
Accuracy Sprint - Stage 2 (Weight Table)
"""

# Maximum points allowed for each category (Total: 100)
WEIGHTS = {
    "trend": 25.0,
    "momentum": 25.0,
    "structure": 25.0,
    "market": 10.0,
    "volume": 5.0,
    "oi_pcr": 5.0,
    "sector": 5.0
}

def get_max_weight(category: str) -> float:
    return WEIGHTS.get(category, 0.0)

def get_total_weight() -> float:
    return sum(WEIGHTS.values())
