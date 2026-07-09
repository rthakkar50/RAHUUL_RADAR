from typing import List, Dict, Any

class FalseSignalReport:
    """
    Formatter for rejected signals blocked by the FalseSignalDetector.
    Transforms raw detection payloads into human-readable text and dictionary formats.
    """
    
    def __init__(self, status: str, reasons: List[str], confidence: float, score: float) -> None:
        self.status = status
        self.reasons = reasons
        self.confidence = confidence
        self.score = score
        
    def build_report(self) -> 'FalseSignalReport':
        """
        Standardizes the report generation. Can be used for internal state updates 
        before format conversion.
        """
        return self
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Returns the constructed report data in a dictionary format.
        """
        return {
            "status": self.status,
            "reasons": self.reasons,
            "confidence": self.confidence,
            "weighted_score": self.score
        }
        
    def to_text(self) -> str:
        """
        Translates the rejection parameters into a highly readable human text block.
        
        Example:
        Signal Rejected
        Reasons
        - Weak Trend
        - Low Volume
        Confidence
        48%
        Weighted Score
        52.40
        """
        lines = []
        
        if self.status.upper() == "REJECTED":
            lines.append("Signal Rejected")
        else:
            # Fallback for unexpected statuses
            lines.append(f"Signal {self.status.capitalize()}")
            
        lines.append("Reasons")
        if self.reasons:
            for reason in self.reasons:
                lines.append(f"- {reason}")
        else:
            lines.append("- No specific reasons provided")
            
        lines.append("Confidence")
        lines.append(f"{self.confidence}%")
        
        lines.append("Weighted Score")
        lines.append(f"{self.score:.2f}")
        
        return "\n".join(lines)
