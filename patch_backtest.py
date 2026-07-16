import re

with open("backtest/backtest_orchestrator.py", "r") as f:
    content = f.read()

# Remove the engines that overwrite the inputs
# Wait, actually let's just make `engines = {}` so it uses the kwargs!
# But wait, AdaptiveStrategyEngine and MasterAIDecisionEngine might be needed!
content = re.sub(
    r'"trend": TrendEngine\(\),\s*"momentum": MomentumEngine\(\),\s*"structure": StructureEngine\(\),\s*"relative_strength": RelativeStrengthEngine\(\),\s*"sector_rotation": SectorRotationEngine\(\),',
    '',
    content
)

with open("backtest/backtest_orchestrator.py", "w") as f:
    f.write(content)
