import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ChartWorkspaceService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_chart_data(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes raw scanner pipeline data into structured payload for the Chart Workspace.
        Returns a clean dictionary that avoids crashes if keys are missing.
        """
        if not scan_data:
            return {"error": "No chart data available"}
            
        raw = scan_data.get("_raw_data", {})
        data_block = raw.get("data", {})
        scores_block = raw.get("confidence_calibration", {}).get("Engine Contributions", {})

        return {
            "header": {
                "company": scan_data.get("Company", "Unknown"),
                "symbol": scan_data.get("Symbol", "N/A"),
                "sector": scan_data.get("Sector", "N/A"),
                "price": scan_data.get("Price", 0.0),
                "signal": scan_data.get("Signal", "WAIT"),
                "confidence": scan_data.get("Confidence", 0.0),
                "market_status": data_block.get("Market Trend", "N/A")
            },
            "ai_panel": {
                "trend_score": scores_block.get("trend_score", {}).get("raw_value", 0.0),
                "momentum_score": scores_block.get("momentum_score", {}).get("raw_value", 0.0),
                "structure_score": scores_block.get("structure_score", {}).get("raw_value", 0.0),
                "volume_score": scores_block.get("volume_score", {}).get("raw_value", 0.0),
                "confidence": scan_data.get("Confidence", 0.0),
                "institution_grade": raw.get("institution_grade", "N/A"),
                "master_ai": scan_data.get("Signal", "WAIT")
            },
            "trade_plan": {
                "entry": scan_data.get("Entry", 0.0),
                "stop_loss": scan_data.get("Stop Loss", 0.0),
                "target_1": scan_data.get("Target 1", 0.0),
                "target_2": scan_data.get("Target 2", 0.0),
                "target_3": raw.get("target_3", 0.0),
                "risk_reward": scan_data.get("Risk Reward", "N/A"),
                "position_size": raw.get("position_size_factor", "1.0x")
            },
            "watch_panel": {
                "latest_signal": scan_data.get("Signal", "WAIT"),
                "previous_signal": raw.get("history", {}).get("Previous Signal", "N/A"),
                "win_rate": raw.get("history", {}).get("Win Rate", "N/A"),
                "average_return": raw.get("history", {}).get("Average Return", "N/A"),
                "signal_quality": raw.get("data", {}).get("Signal Quality", "N/A")
            },
            "overlays": {
                "ema": True,
                "vwap": True,
                "volume": True,
                "atr": True,
                "support": data_block.get("Support", "N/A"),
                "resistance": data_block.get("Resistance", "N/A"),
                "swing_high": data_block.get("Swing High", "N/A"),
                "swing_low": data_block.get("Swing Low", "N/A"),
                "ai_entry": scan_data.get("Entry", 0.0),
                "ai_sl": scan_data.get("Stop Loss", 0.0),
                "ai_t1": scan_data.get("Target 1", 0.0),
                "ai_t2": scan_data.get("Target 2", 0.0),
                "ai_t3": raw.get("target_3", 0.0),
                "trailing_stop": raw.get("trailing_stop", "N/A")
            }
        }
