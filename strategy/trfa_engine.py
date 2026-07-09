import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TradeForensicEngine:
    """
    MASTER-10: TRADE REPLAY & FORENSIC ANALYSIS ENGINE (TRFA) V2.0
    The Black Box Data Recorder. Analyzes closed trades to generate root causes and forensic reports.
    """
    
    def __init__(self):
        # Could integrate with a TRFA specific database here
        pass
        
    def analyze_closed_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a closed trade and return a Forensic Report.
        trade_data must contain: symbol, signal, entry, exit, stop_loss, target_1, target_2, pnl, exit_reason
        """
        symbol = trade_data.get("symbol", "UNKNOWN")
        signal = trade_data.get("signal", "BUY")
        entry = trade_data.get("entry_price", 0.0)
        exit_price = trade_data.get("current_price", 0.0) # From LTME, the final price
        pnl = trade_data.get("pnl", 0.0)
        pnl_pct = trade_data.get("pnl_pct", 0.0)
        exit_reason = trade_data.get("exit_reason", "Manual")
        
        is_winner = pnl > 0
        
        report = {
            "symbol": symbol,
            "signal": signal,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "exit_reason": exit_reason,
            "timestamp": datetime.now().isoformat(),
            "status": "WIN" if is_winner else "LOSS",
            "root_cause": "",
            "explanation": "",
            "recommendation": ""
        }
        
        if is_winner:
            self._analyze_winner(report, trade_data)
        else:
            self._analyze_loser(report, trade_data)
            
        # AI AUDIT Logging
        logger.info(f"[TRFA] {symbol} Forensic Report: {report['status']} | Root Cause: {report['root_cause']}")
        return report
        
    def _analyze_winner(self, report: Dict, trade_data: Dict):
        exit_reason = report["exit_reason"]
        
        if "Target" in exit_reason or "TSL" in exit_reason:
            report["root_cause"] = "Trend Aligned & Momentum Sustained"
            report["explanation"] = "The trade successfully captured the intended move. Volume supported the breakout."
            report["recommendation"] = "Keep executing this setup. Do not change parameters."
        else:
            report["root_cause"] = "Premature Manual Exit or Market Reversal"
            report["explanation"] = f"Trade exited in profit due to: {exit_reason}."
            report["recommendation"] = "Review if exit was emotional or system-driven."

    def _analyze_loser(self, report: Dict, trade_data: Dict):
        exit_reason = report["exit_reason"]
        
        if "Stop Loss" in exit_reason or "SL" in exit_reason:
            # Basic analysis (in production this would pull historical market data)
            report["root_cause"] = "Fake Breakout or Market Reversal"
            report["explanation"] = "Price failed to sustain momentum after entry. Possible false breakout trap or broader sector collapse."
            report["recommendation"] = "Review Entry Validation (EVE) and FBDE logs for this timestamp to ensure no weak wicks were ignored."
        elif "Time" in exit_reason:
            report["root_cause"] = "Stagnation / Low Volatility"
            report["explanation"] = "The setup was valid but the market lacked the liquidity/momentum to push to target."
            report["recommendation"] = "Avoid trading this setup during low-volume periods (e.g., lunch hour)."
        else:
            report["root_cause"] = "Unexpected Market Shock or Manual Exit"
            report["explanation"] = f"Trade exited with loss due to: {exit_reason}."
            report["recommendation"] = "Ensure manual exits are justified by capital protection rules."
