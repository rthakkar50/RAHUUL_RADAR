with open("backtest/backtest_orchestrator.py", "r") as f:
    lines = f.readlines()

out = []
in_engines = False
for line in lines:
    if "engines = {}" in line:
        out.append("""        engines = {
            "trend": TrendEngine(),
            "momentum": MomentumEngine(),
            "structure": StructureEngine(),
            "relative_strength": RelativeStrengthEngine(),
            "sector_rotation": SectorRotationEngine(),
            "adaptive_strategy": AdaptiveStrategyEngine.get_instance() if hasattr(AdaptiveStrategyEngine, 'get_instance') else AdaptiveStrategyEngine(),
            "master_ai": MasterAIDecisionEngine()
        }
""")
    else:
        out.append(line)

with open("backtest/backtest_orchestrator.py", "w") as f:
    f.writelines(out)
