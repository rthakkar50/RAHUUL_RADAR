import json
from typing import Dict, Any

class SignalExplainer:
    """
    Generates human-readable explanations and summaries for trade signals
    based on the outputs collected from the Master Signal Pipeline.
    """
    
    def __init__(self) -> None:
        pass
        
    def build_positive_reasons(self, data: Dict[str, Any]) -> list:
        """
        Extracts and builds a list of positive reasons for the trade.
        """
        reasons = []
        
        trend = data.get("Trend")
        if trend == "BULL" or (isinstance(trend, (int, float)) and trend >= 70):
            reasons.append("Trend is Bullish")
        elif trend == "BEAR" or (isinstance(trend, (int, float)) and trend <= 30):
            reasons.append("Trend is Bearish")

        vol = data.get("Volume")
        if vol == "HIGH" or (isinstance(vol, (int, float)) and vol >= 70):
            reasons.append("Volume Above Average")

        sec = data.get("Sector Rotation")
        if sec in ("STRONG", "LEADING") or (isinstance(sec, (int, float)) and sec >= 70):
            reasons.append("Sector Strong")

        oc = data.get("Option Chain")
        if oc in ("BULLISH", "BEARISH", "CONFIRMED") or (isinstance(oc, (int, float)) and oc >= 70):
            reasons.append("Option Chain Confirmed")
            
        return reasons
        
    def build_negative_reasons(self, data: Dict[str, Any]) -> list:
        """
        Extracts and builds a list of negative reasons or risks for the trade.
        """
        reasons = []
        
        mom = data.get("Momentum")
        if mom == "OVERBOUGHT" or (isinstance(mom, (int, float)) and mom >= 80):
            reasons.append("RSI slightly overbought")
        elif mom == "OVERSOLD" or (isinstance(mom, (int, float)) and mom <= 20):
            reasons.append("RSI slightly oversold")
            
        return reasons

    def build_summary(self, data: Dict[str, Any]) -> str:
        """
        Builds a high-level summary string based on the indicators and score.
        """
        decision = data.get("decision", "WATCH")
        score = data.get("Weighted Score", 0)
        
        if decision == "BUY" and score >= 80:
            return "High probability trend continuation."
        elif decision == "SELL" and score >= 80:
            return "High probability breakdown."
            
        return "Standard setup."

    def build_explanation(self, data: Dict[str, Any]) -> str:
        """
        Builds the final JSON explanation payload.
        
        Args:
            data: Dictionary containing indicator states and scores.
            
        Returns:
            JSON formatted string containing decision, score, confidence, and reasons.
        """
        payload = {
            "decision": data.get("decision", "WATCH"),
            "score": data.get("Weighted Score", 0),
            "confidence": data.get("confidence", 0),
            "positive": self.build_positive_reasons(data),
            "negative": self.build_negative_reasons(data),
            "summary": self.build_summary(data)
        }
        
        return json.dumps(payload, indent=2)
