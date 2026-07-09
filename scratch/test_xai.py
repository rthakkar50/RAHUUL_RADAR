import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.xai_engine import ExplainableAIEngine

def test_xai():
    xai = ExplainableAIEngine()
    
    # 1. Test Reject Panel
    reject_data = {
        "symbol": "RELIANCE.NS",
        "decision": "REJECT",
        "score": 45.2,
        "confidence": 58.0,
        "tqi": 83.0,
        "engines": {
            "trend": {"pass": True, "score": 25.0, "reason": "Price > EMA20"},
            "momentum": {"pass": False, "score": 5.0, "reason": "RSI flat"},
            "structure": {"pass": True, "score": 15.0, "reason": "Higher Highs"},
            "adx": {"pass": False, "current": 18.0, "required": ">22"},
            "avwap": {"pass": True, "reason": "Above Volume Anchor"},
            "volume": {"pass": True, "reason": "Spike detected"},
            "relative_strength": {"pass": True, "reason": "Outperforming Nifty"},
            "sector": {"pass": True, "reason": "Energy Bullish"},
            "smart_money": {"pass": False, "reason": "No aggressive buying"},
            "market_regime": {"pass": True, "reason": "Bull Market"},
            "risk_reward": {"pass": True, "rr": "1:2.5"},
            "institutional_validation": {"pass": True, "reason": "Approved"},
            "false_breakout": {"pass": True, "reason": "No trap detected"},
            "elite_selection": {"pass": False, "reason": "TQI < 85"}
        }
    }
    
    print("--- REJECT PANEL ---")
    print(xai.generate_panel(reject_data))
    
    # 2. Test Buy Panel
    buy_data = {
        "symbol": "HDFCBANK.NS",
        "decision": "BUY",
        "score": 92.5,
        "confidence": 88.0,
        "tqi": 91.0,
        "engines": {
            "trend": {"pass": True, "score": 25.0, "reason": "Perfect alignment"},
            "momentum": {"pass": True, "score": 25.0, "reason": "RSI rising"},
            "structure": {"pass": True, "score": 25.0, "reason": "Strong breakout"},
            "adx": {"pass": True, "current": 35.0, "required": ">22"},
            "avwap": {"pass": True, "reason": "At Discount"},
            "volume": {"pass": True, "reason": "Institutional Accumulation"},
            "relative_strength": {"pass": True, "reason": "Outperforming"},
            "sector": {"pass": True, "reason": "Banking Bullish"},
            "smart_money": {"pass": True, "reason": "Aggressive footprints"},
            "market_regime": {"pass": True, "reason": "Bull Market"},
            "risk_reward": {"pass": True, "rr": "1:3.0"},
            "institutional_validation": {"pass": True, "reason": "Approved"},
            "false_breakout": {"pass": True, "reason": "Cleared"},
            "elite_selection": {"pass": True, "reason": "TQI >= 85"}
        }
    }
    
    print("\n--- BUY PANEL ---")
    print(xai.generate_panel(buy_data))

if __name__ == "__main__":
    test_xai()
