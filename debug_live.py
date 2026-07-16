from application.swing_scanner_service import SwingScannerService
import json

def noop_progress(x):
    pass

service = SwingScannerService()
service.config.target_universe = "Test" # Just so it runs quickly
# I'll just run it directly on HDFCBANK.NS by modifying the fetch temporarily
class MockConfig:
    target_universe = "Test"
    data_provider = "yahoo"
service.config = MockConfig()

# Wait, it's easier to just call the pipeline exactly how swing_scanner_service does.
from core.models import ScanResult
from ranking.scoring_rules import SignalStrength
from datetime import datetime

r = ScanResult(
    symbol="HDFCBANK.NS",
    company_name="HDFC",
    sector="Banking",
    trend_direction="BULLISH",
    trend_score=80.0,
    momentum_score=80.0,
    structure_score=80.0,
    volume_score=80.0,
    volatility_score=80.0,
    relative_strength_score=80.0,
    risk_score=80.0,
    mtf_score=80.0,
    total_score=80.0,
    price=1500.0,
    volume=100000.0,
    signal=SignalStrength.STRONG_BUY,
    timestamp=datetime.now()
)

pipeline_res = service.pipeline.run(
    symbol=r.symbol,
    price=r.price,
    decision="STRONG_BUY",
    confidence=80.0,
    trend={"score": getattr(r, 'trend_score', 50.0)},
    momentum={"score": getattr(r, 'momentum_score', 50.0)},
    structure={"score": getattr(r, 'structure_score', 50.0), "details": {}},
    volume={"score": getattr(r, 'volume_score', 50.0)},
    risk={"score": getattr(r, 'risk_score', 50.0)},
    relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)},
    atr=0.0
)
print(pipeline_res.get("alignment_report"))
