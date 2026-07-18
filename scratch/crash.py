import sys, os
sys.path.append(os.getcwd())
from core.decision_engine import DecisionEngine
de = DecisionEngine()
de.calculate(None, None, None)
