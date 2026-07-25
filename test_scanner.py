import sys
import os
import asyncio
from application.swing_scanner_service import SwingScannerService
from core.models.domain_models import ScanResult, SignalStrength

def test_scan():
    svc = SwingScannerService()
    # Mocking the pipeline output to simulate the fix
    class MockPipeline:
        def run(self, **kwargs):
            return {"calibrated_confidence": 73.5, "recommended_entry": 100, "stop_loss": 90, "target_1": 110}
            
    svc.pipeline = MockPipeline()
    
    # Mock raw result
    r = ScanResult(
        symbol="SUPREMEIND", company_name="Supreme", sector="Manufacturing",
        trend_direction="BULL", trend_score=25, momentum_score=20, structure_score=20,
        volume_score=15, volatility_score=0, relative_strength_score=0, risk_score=0, mtf_score=0,
        total_score=80, price=100, volume=1000, signal=SignalStrength.BUY, timestamp=None,
    )
    r.confidence = 100.0 # From raw decision engine
    r.adjusted_score = 80
    
    class MockManager:
        def get_live_price(self, sym): return 100
        def get_live_quote(self, sym): return {'volume': 1000}
        
    res = []
    # Test just the processing block
    confidence_test = 0
    pipeline_res = svc.pipeline.run()
    
    conf_from_engine = getattr(r, 'confidence', None)
    conf_from_pipeline = pipeline_res.get("calibrated_confidence", None)
    if conf_from_pipeline is not None and conf_from_pipeline > 0:
        confidence_test = conf_from_pipeline
    elif conf_from_engine is not None and conf_from_engine > 0:
        confidence_test = conf_from_engine
        
    print(f"Final confidence selected: {confidence_test}")

if __name__ == "__main__":
    test_scan()
