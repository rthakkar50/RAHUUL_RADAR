import sys
import os

from core.master_signal_pipeline import MasterSignalPipeline
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.relative_strength_engine import RelativeStrengthEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.adaptive_strategy_engine import AdaptiveStrategyEngine
from core.master_ai_decision_engine import MasterAIDecisionEngine

engines = {
    "trend": TrendEngine(),
    "momentum": MomentumEngine(),
    "structure": StructureEngine(),
    "relative_strength": RelativeStrengthEngine(),
    "sector_rotation": SectorRotationEngine(),
    "adaptive_strategy": AdaptiveStrategyEngine(),
    "master_ai": MasterAIDecisionEngine()
}
pipeline = MasterSignalPipeline(engines)

pipeline_res = pipeline.run(
    symbol="RELIANCE.NS",
    price=100.0,
    decision="BUY",
    confidence=90.0,
    trend={"score": 90.0},
    momentum={"score": 90.0},
    structure={"score": 90.0, "details": {}},
    volume={"score": 90.0},
    risk={"score": 90.0},
    relative_strength={"score": 90.0},
    atr=2.0
)

print(pipeline_res)
