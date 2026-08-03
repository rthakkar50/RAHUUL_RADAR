from core.decision_engine import DecisionEngine
import pandas as pd

engine = DecisionEngine()
# simulate a bearish score:
trend_score = 5
momentum_score = 5
structure_score = 5

t_dir = (trend_score / 30.0) * 2.0 - 1.0
m_dir = (momentum_score / 25.0) * 2.0 - 1.0
s_dir = (structure_score / 25.0) * 2.0 - 1.0

agreement = abs(t_dir + m_dir + s_dir) / 3.0
confidence = min(100.0, max(0.0, agreement * 100.0))

print(f"Confidence for 5,5,5: {confidence}")

# what if it's 10, 10, 10?
trend_score = 10
momentum_score = 10
structure_score = 10

t_dir = (trend_score / 30.0) * 2.0 - 1.0
m_dir = (momentum_score / 25.0) * 2.0 - 1.0
s_dir = (structure_score / 25.0) * 2.0 - 1.0

agreement = abs(t_dir + m_dir + s_dir) / 3.0
confidence = min(100.0, max(0.0, agreement * 100.0))
print(f"Confidence for 10,10,10: {confidence}")
