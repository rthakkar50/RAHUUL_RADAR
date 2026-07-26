import pytest
from utils.validation import validate_trade_levels
from application.swing_scanner_service import SwingScannerService
from unittest.mock import patch, MagicMock

# --- Unit Tests for validate_trade_levels ---

def test_buy_valid():
    is_valid, reason = validate_trade_levels("BUY", 100, 95, 110)
    assert is_valid == True
    assert reason in ("", "Valid trade levels")

def test_buy_invalid_sl():
    is_valid, reason = validate_trade_levels("BUY", 100, 105, 110)
    assert is_valid == False
    assert "stop loss" in reason.lower()

def test_buy_invalid_target():
    is_valid, reason = validate_trade_levels("BUY", 100, 95, 90)
    assert is_valid == False
    assert "target" in reason.lower()

def test_sell_valid():
    is_valid, reason = validate_trade_levels("SELL", 100, 105, 90)
    assert is_valid == True
    assert reason in ("", "Valid trade levels")

def test_sell_invalid_sl():
    is_valid, reason = validate_trade_levels("SELL", 100, 95, 90)
    assert is_valid == False
    assert "stop loss" in reason.lower()

def test_sell_invalid_target():
    is_valid, reason = validate_trade_levels("SELL", 100, 105, 110)
    assert is_valid == False
    assert "target" in reason.lower()

def test_regression_screenshot_example():
    # SELL entry 244.60, SL 239.71, target 249.49 must be invalid
    is_valid, reason = validate_trade_levels("SELL", 244.60, 239.71, 249.49)
    assert is_valid == False


# --- Integration Tests for SwingScannerService Pipeline ---

@patch("market.yahoo_provider.YahooFinanceProvider.pre_cache")
@patch("application.swing_scanner_service.get_all_symbols")
@patch("scanner.scanner_engine.ScannerEngine.scan_market")
@patch("core.master_signal_pipeline.MasterSignalPipeline.run")
def test_pipeline_confidence_and_rr(mock_pipeline_run, mock_scan_market, mock_get_all_symbols, mock_pre_cache):
    """
    Test that the swing scanner service correctly applies confidence gating and RR calculations
    during process_post_scan.
    """
    mock_get_all_symbols.return_value = [{"symbol": "TEST.NS", "sector": "IT", "company_name": "Test Co"}]
    
    # Mock the ScannerEngine output
    class MockScanResult:
        def __init__(self):
            self.symbol = "TEST.NS"
            self.price = 100.0
            self.volume = 1000
            self.signal = "SELL"
            self.confidence = 34.9
            self.adjusted_score = 86.0
            self.trend_direction = "BEARISH"
            self.breakdown_detail = {}
            
    mock_scan_market.return_value = [MockScanResult()]
    
    # Mock the MasterSignalPipeline.run output
    # This represents the output of the pipeline which gets fed into process_post_scan
    mock_pipeline_run.return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 102.0,       # Risk = 2.0
        "target_1": 96.0,         # Reward = 4.0 -> RR = 2.0
        "risk_reward": 2.0,
        "execution_status": "READY"
    }
    
    service = SwingScannerService()
    # Explicitly set thresholds to ensure predictable behavior
    service.config.min_directional_confidence = 70.0
    service.config.min_directional_score = 75.0
    service.config.min_risk_reward = 1.2
    
    result = service.execute_swing_scan()
    
    assert result["total_scanned"] == 1
    qualified = result["qualified_results"]
    assert len(qualified) == 1
    
    # Verification: Low confidence directional signal downgraded to WATCH
    # signal SELL, score 86, confidence 34.9 -> downgraded to WATCH
    assert qualified[0]["Signal"] == "WATCH"
    assert any("Confidence below directional threshold" in r for r in qualified[0]["_reasons"])
    
    # Verification: RR calculation produces 1:2 correctly for SELL
    assert qualified[0]["Risk Reward"] == "1:2.0"
    
    
@patch("market.yahoo_provider.YahooFinanceProvider.pre_cache")
@patch("application.swing_scanner_service.get_all_symbols")
@patch("scanner.scanner_engine.ScannerEngine.scan_market")
@patch("core.master_signal_pipeline.MasterSignalPipeline.run")
def test_pipeline_fallback_rr(mock_pipeline_run, mock_scan_market, mock_get_all_symbols, mock_pre_cache):
    """
    Test that the swing scanner service correctly calculates fallback targets and RR.
    """
    mock_get_all_symbols.return_value = [{"symbol": "TEST2.NS", "sector": "IT", "company_name": "Test Co 2"}]
    
    class MockScanResult:
        def __init__(self, sig="BUY"):
            self.symbol = "TEST2.NS"
            self.price = 100.0
            self.volume = 1000
            self.signal = sig
            self.confidence = 80.0
            self.adjusted_score = 80.0
            self.trend_direction = "BULLISH" if sig == "BUY" else "BEARISH"
            self.breakdown_detail = {}
            
    mock_scan_market.return_value = [MockScanResult("BUY")]
    
    # Pass 0.0 for targets to trigger fallback
    mock_pipeline_run.return_value = {
        "recommended_entry": 100.0,
        "stop_loss": 0.0,  
        "target_1": 0.0,   
        "risk_reward": 0.0,
        "execution_status": "READY"
    }
    
    service = SwingScannerService()
    
    # Test BUY
    result = service.execute_swing_scan()
    qualified = result["qualified_results"]
    assert len(qualified) == 1
    assert qualified[0]["Signal"] == "BUY"
    assert qualified[0]["Stop Loss"] == 98.0  # Fallback: 100 * 0.98
    assert qualified[0]["Target 1"] == 104.0  # Fallback: 100 + (2 * 2.0)
    assert qualified[0]["Risk Reward"] == "1:2.0"
    
    # Test SELL
    mock_scan_market.return_value = [MockScanResult("SELL")]
    result = service.execute_swing_scan()
    qualified = result["qualified_results"]
    assert len(qualified) == 1
    assert qualified[0]["Signal"] == "SELL"
    assert qualified[0]["Stop Loss"] == 102.0 # Fallback: 100 * 1.02
    assert qualified[0]["Target 1"] == 96.0   # Fallback: 100 - (2 * 2.0)
    assert qualified[0]["Risk Reward"] == "1:2.0"
