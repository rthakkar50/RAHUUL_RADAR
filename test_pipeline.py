import sys
sys.path.insert(0, '.')
from core.master_signal_pipeline import MasterSignalPipeline

pipe = MasterSignalPipeline()
res = pipe.run(
    symbol="OFSS.NS",
    price=11746.0,
    decision="BUY",
    confidence=80.0,
    data={}
)
print("EXECUTION STATUS:", res.get("execution_status"))
print("EXECUTION REASON:", res.get("execution_reason"))
