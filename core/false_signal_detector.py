from typing import Dict, Any, Tuple, List

class FalseSignalDetector:
    """
    Identifies weak and unreliable trading signals before they reach the trader.
    This engine never creates signals; it only blocks bad signals.
    """
    
    def __init__(self) -> None:
        pass

    def check_trend_alignment(self, data: Dict[str, Any], decision: str) -> Tuple[bool, str]:
        """Validates that the intended trade aligns with the overarching trend."""
        trend = data.get("Trend", "UNKNOWN")
        if decision == "BUY" and trend == "BEAR":
            return False, "Trend alignment failure: Buying in a BEAR trend."
        if decision == "SELL" and trend == "BULL":
            return False, "Trend alignment failure: Selling in a BULL trend."
        return True, ""

    def check_volume_confirmation(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Ensures that the trade is backed by sufficient trading volume."""
        vol = data.get("Volume", "UNKNOWN")
        if isinstance(vol, (int, float)) and vol < 30:
            return False, "Volume confirmation failure: Low volume."
        elif vol == "LOW":
            return False, "Volume confirmation failure: Low volume."
        return True, ""

    def check_market_regime(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Filters out trades generated in unfavorable broader market environments."""
        regime = data.get("Market Regime", "UNKNOWN")
        if regime in ("CHOPPY", "SIDEWAYS", "UNKNOWN") or (isinstance(regime, (int, float)) and regime < 30):
            return False, "Market regime failure: Choppy or unfavorable market environment."
        return True, ""

    def check_sector_strength(self, data: Dict[str, Any], decision: str) -> Tuple[bool, str]:
        """Validates that the asset's sector supports the direction of the trade."""
        sec = data.get("Sector Rotation", "UNKNOWN")
        if decision == "BUY" and sec == "WEAK":
            return False, "Sector strength failure: Buying in a WEAK sector."
        if decision == "SELL" and sec == "STRONG":
            return False, "Sector strength failure: Selling in a STRONG sector."
        return True, ""

    def check_relative_strength(self, data: Dict[str, Any], decision: str) -> Tuple[bool, str]:
        """Ensures the asset exhibits proper relative strength against benchmarks."""
        rs = data.get("Relative Strength", "UNKNOWN")
        if decision == "BUY" and rs == "WEAK":
            return False, "Relative strength failure: Asset is underperforming the market."
        if decision == "SELL" and rs == "STRONG":
            return False, "Relative strength failure: Asset is outperforming the market."
        return True, ""

    def check_option_chain_confirmation(self, data: Dict[str, Any], decision: str) -> Tuple[bool, str]:
        """Cross-references options flow to prevent trades against strong derivatives positioning."""
        oc = data.get("Option Chain", "UNKNOWN")
        if decision == "BUY" and oc == "BEARISH":
            return False, "Option chain confirmation failure: Options data shows bearish resistance."
        if decision == "SELL" and oc == "BULLISH":
            return False, "Option chain confirmation failure: Options data shows bullish support."
        return True, ""
        
    def build_rejection_report(self, is_approved: bool, reasons: List[str]) -> Dict[str, Any]:
        """Constructs the standard rejection/approval payload."""
        return {
            "status": "APPROVED" if is_approved else "REJECTED",
            "reasons": reasons
        }

    def detect(self, data: Dict[str, Any], decision: str = "WATCH") -> Dict[str, Any]:
        """
        Runs all false signal detection checks on the proposed signal.
        
        Args:
            data: Dictionary of evaluated states from the pipeline engines.
            decision: Intended signal direction (BUY/SELL).
            
        Returns:
            Dictionary containing final 'status' (APPROVED or REJECTED) 
            and a 'reasons' list documenting every failed check.
        """
        reasons = []
        if decision == "WATCH":
            return self.build_rejection_report(False, ["No active signal to validate (WATCH)."])
            
        checks = [
            self.check_trend_alignment(data, decision),
            self.check_volume_confirmation(data),
            self.check_market_regime(data),
            self.check_sector_strength(data, decision),
            self.check_relative_strength(data, decision),
            self.check_option_chain_confirmation(data, decision)
        ]
        
        for passed, reason in checks:
            if not passed:
                reasons.append(reason)
                
        is_approved = len(reasons) == 0
        return self.build_rejection_report(is_approved, reasons)
