import pytest
from unittest.mock import patch, MagicMock
from application.swing_scanner_service import SwingScannerService

@pytest.fixture
def mock_dependencies():
    with patch("application.swing_scanner_service.get_all_symbols") as mock_symbols, \
         patch("market.yahoo_provider.YahooFinanceProvider.pre_cache") as mock_pre_cache, \
         patch("scanner.scanner_engine.ScannerEngine.scan_market") as mock_scan_market, \
         patch("core.master_signal_pipeline.MasterSignalPipeline.run") as mock_pipeline_run:
         
        mock_symbols.return_value = [
            {"symbol": "TEST1", "sector": "IT", "company_name": "Test Co 1"},
            {"symbol": "TEST2", "sector": "Auto", "company_name": "Test Co 2"},
            {"symbol": "TEST3", "sector": "Bank", "company_name": "Test Co 3"},
            {"symbol": "TEST4", "sector": "Pharma", "company_name": "Test Co 4"},
            {"symbol": "TEST5", "sector": "FMCG", "company_name": "Test Co 5"},
            {"symbol": "BANKBARODA", "sector": "Bank", "company_name": "Bank of Baroda"}
        ]
        yield {
            "symbols": mock_symbols,
            "scan_market": mock_scan_market,
            "pipeline_run": mock_pipeline_run
        }

def test_ready_signal_promotion(mock_dependencies):
    service = SwingScannerService()
    service.config.swing_signal_mode = "Balanced"
    
    # Mock pipeline returning WATCH but with High scores
    # Balanced min_score=75, min_conf=70, min_rr=1.8
    mock_dependencies["pipeline_run"].return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 90.0,
        "target_1": 120.0,  # RR = 20 / 10 = 2.0
        "risk_reward": 2.0,
        "calibrated_confidence": 85.0
    }
    
    class MockScanResult:
        def __init__(self, sym):
            self.symbol = sym
            self.price = 100.0
            self.volume = 1000
            self.signal = "WATCH"
            self.adjusted_score = 80.0
            self.confidence = 85.0
            self.trend_direction = "BULLISH"
            
    mock_dependencies["scan_market"].return_value = [MockScanResult("TEST1")]
    
    res = service.execute_swing_scan()
    trades = res["qualified_results"]
    assert len(trades) > 0
    test1 = [t for t in trades if t["Symbol"] == "TEST1"][0]
    
    # Should be promoted to READY because score 80 >= 75 and conf 85 >= 70 and RR 2.0 >= 1.8
    assert test1["Signal"] == "READY"
    assert "waiting for breakout confirmation" in str(test1["_reasons"])

def test_conservative_mode_downgrades(mock_dependencies):
    service = SwingScannerService()
    service.config.swing_signal_mode = "Conservative" # min_score 80, min_conf 75
    
    mock_dependencies["pipeline_run"].return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 90.0,
        "target_1": 120.0, # RR 2.0
        "calibrated_confidence": 72.0
    }
    
    class MockScanResult:
        def __init__(self):
            self.symbol = "TEST2"
            self.price = 100.0
            self.signal = "BUY"
            self.adjusted_score = 78.0
            self.confidence = 72.0
            self.trend_direction = "BULLISH"
            
    mock_dependencies["scan_market"].return_value = [MockScanResult()]
    
    res = service.execute_swing_scan()
    trade = res["qualified_results"][0]
    
    # In Balanced it would be BUY (since 78 > 75 and 72 > 70).
    # In Conservative it should be downgraded to WATCH
    assert trade["Signal"] == "WATCH"
    assert "Confidence below directional threshold" in str(trade["_reasons"])

def test_aggressive_mode_allows_early(mock_dependencies):
    service = SwingScannerService()
    service.config.swing_signal_mode = "Aggressive" # min_score 70, min_conf 65, min_rr 1.5
    
    mock_dependencies["pipeline_run"].return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 90.0,
        "target_1": 116.0, # RR = 16 / 10 = 1.6
        "calibrated_confidence": 68.0
    }
    
    class MockScanResult:
        def __init__(self):
            self.symbol = "TEST3"
            self.price = 100.0
            self.signal = "BUY"
            self.adjusted_score = 72.0
            self.confidence = 68.0
            self.trend_direction = "BULLISH"
            
    mock_dependencies["scan_market"].return_value = [MockScanResult()]
    
    res = service.execute_swing_scan()
    trade = res["qualified_results"][0]
    
    # In Aggressive it stays BUY
    assert trade["Signal"] == "BUY"

def test_invalid_buy_levels(mock_dependencies):
    service = SwingScannerService()
    service.config.swing_signal_mode = "Balanced"
    
    # Invalid BUY: Stop loss is above entry
    mock_dependencies["pipeline_run"].return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 105.0, # Invalid
        "target_1": 120.0,
        "calibrated_confidence": 90.0
    }
    
    class MockScanResult:
        def __init__(self):
            self.symbol = "TEST4"
            self.price = 100.0
            self.signal = "BUY"
            self.adjusted_score = 90.0
            self.confidence = 90.0
            self.trend_direction = "BULLISH"
            
    mock_dependencies["scan_market"].return_value = [MockScanResult()]
    
    res = service.execute_swing_scan()
    trade = res["qualified_results"][0]
    assert trade["Signal"] == "WATCH"
    assert "Invalid BUY setup: stop loss must be below entry" in str(trade["_reasons"])

def test_invalid_sell_levels(mock_dependencies):
    service = SwingScannerService()
    service.config.swing_signal_mode = "Balanced"
    
    # Invalid SELL: Stop loss is below entry
    mock_dependencies["pipeline_run"].return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 90.0, # Invalid for SELL
        "target_1": 80.0,
        "calibrated_confidence": 90.0
    }
    
    class MockScanResult:
        def __init__(self):
            self.symbol = "TEST5"
            self.price = 100.0
            self.signal = "SELL"
            self.adjusted_score = 90.0
            self.confidence = 90.0
            self.trend_direction = "BEARISH"
            
    mock_dependencies["scan_market"].return_value = [MockScanResult()]
    
    res = service.execute_swing_scan()
    trade = res["qualified_results"][0]
    assert trade["Signal"] == "WATCH"
    assert "Invalid SELL setup: stop loss must be above entry" in str(trade["_reasons"])

def test_regression_bankbaroda(mock_dependencies):
    service = SwingScannerService()
    service.config.swing_signal_mode = "Balanced"
    
    # Confidence is 34.9
    mock_dependencies["pipeline_run"].return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 110.0,
        "target_1": 80.0, # RR 2.0
        "calibrated_confidence": 34.9
    }
    
    class MockScanResult:
        def __init__(self):
            self.symbol = "BANKBARODA"
            self.price = 100.0
            self.signal = "SELL"
            self.adjusted_score = 14.0 # 0-100 Bullish scale, so 14.0 is a strong SELL
            self.confidence = 34.9
            self.trend_direction = "BEARISH"
            
    mock_dependencies["scan_market"].return_value = [MockScanResult()]
    
    res = service.execute_swing_scan()
    trade = res["qualified_results"][0]
    assert trade["Signal"] == "WATCH"
    assert "Confidence below directional threshold" in str(trade["_reasons"])
