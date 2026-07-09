import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TradeWorkspaceService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_workspace_data(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses raw scanner data into structured sections for the Trade Workspace.
        """
        if not scan_data:
            return {"error": "Not Available"}
            
        raw = scan_data.get("_raw_data", {})
        data_block = raw.get("data", {})
        
        # Section 1 & 8: Trade Summary & Readiness
        summary = {
            "company": scan_data.get("Company", "Unknown"),
            "symbol": scan_data.get("Symbol", "N/A"),
            "sector": scan_data.get("Sector", "N/A"),
            "price": scan_data.get("Price", 0.0),
            "signal": scan_data.get("Signal", "WAIT"),
            "confidence": scan_data.get("Confidence", 0.0),
            "overall_score": scan_data.get("Score", 0.0),
            "institution_grade": raw.get("institution_grade", "Not Available"),
            "readiness": "Ready" if scan_data.get("Signal") in ["BUY", "SELL"] else "Wait"
        }
        
        # Section 2: Trade Setup
        setup = {
            "entry": scan_data.get("Entry", 0.0),
            "stop_loss": scan_data.get("Stop Loss", 0.0),
            "target_1": scan_data.get("Target 1", 0.0),
            "target_2": scan_data.get("Target 2", 0.0),
            "target_3": raw.get("target_3", 0.0),
            "risk_reward": scan_data.get("Risk Reward", "Not Available"),
            "trailing_stop": raw.get("trailing_stop", "Not Available")
        }
        
        # Section 3: Risk Meter
        risk = {
            "level": raw.get("risk_level", "Medium"),
            "capital_risk": "2%",
            "volatility": "Not Available",
            "atr_risk": data_block.get("ATR", "Not Available")
        }
        
        # Section 4: Expected Reward
        reward = {
            "expected_return": data_block.get("Expected Return", "Not Available"),
            "expected_holding": data_block.get("Expected Holding", "Not Available"),
            "win_probability": f"{scan_data.get('Confidence', 0.0)}%",
            "historical_win_rate": raw.get("history", {}).get("Win Rate", "Not Available"),
            "risk_adjusted_return": "Not Available"
        }
        
        # Section 5: Technical Snapshot
        technical = {
            "ema": data_block.get("EMA Status", "Not Available"),
            "vwap": data_block.get("VWAP", "Not Available"),
            "rsi": data_block.get("RSI", "Not Available"),
            "macd": data_block.get("MACD", "Not Available"),
            "adx": data_block.get("ADX", "Not Available"),
            "atr": data_block.get("ATR", "Not Available"),
            "volume": data_block.get("Volume Rating", "Not Available"),
            "relative_strength": data_block.get("Relative Strength", "Not Available"),
            "sector_strength": data_block.get("Sector Strength", "Not Available"),
            "market_breadth": data_block.get("Market Breadth", "Not Available")
        }
        
        # Section 6 & 7: AI Reasoning & Warnings
        reasons = scan_data.get("_reasons", ["No specific reasoning provided by AI."])
        warnings = data_block.get("Warnings", [])
        
        # Right Panel & Bottom
        chart_data = {
            "current_candle": "Not Available",
            "entry": setup["entry"],
            "sl": setup["stop_loss"],
            "targets": [setup["target_1"], setup["target_2"], setup["target_3"]]
        }
        
        timeline = {
            "previous_signal": raw.get("history", {}).get("Previous Signal", "Not Available"),
            "current_signal": scan_data.get("Signal", "WAIT"),
            "next_review": "EOD"
        }
        
        return {
            "summary": summary,
            "setup": setup,
            "risk": risk,
            "reward": reward,
            "technical": technical,
            "reasons": reasons,
            "warnings": warnings,
            "chart_data": chart_data,
            "timeline": timeline,
            "decision": scan_data.get("Signal", "WAIT")
        }
