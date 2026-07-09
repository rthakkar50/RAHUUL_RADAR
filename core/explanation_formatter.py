import json
from typing import Union, Dict, Any

class ExplanationFormatter:
    """
    Formats structured signal explanation payloads (either dictionaries or JSON strings)
    into a clean, human-readable plain text format.
    """
    
    @staticmethod
    def format_text(explanation: Union[str, Dict[str, Any]]) -> str:
        """
        Formats an explanation payload into human-readable text.
        
        Args:
            explanation: A JSON string or python dict containing signal details.
            
        Returns:
            str: Human readable plain text representation.
        """
        if isinstance(explanation, str):
            try:
                data = json.loads(explanation)
            except json.JSONDecodeError:
                return "Invalid explanation format."
        elif isinstance(explanation, dict):
            data = explanation
        else:
            return "Unsupported explanation data type."

        decision = str(data.get("decision", "WATCH")).upper()
        confidence = data.get("confidence", 0)
        positive = data.get("positive", [])
        negative = data.get("negative", [])
        
        lines = [
            decision,
            f"Confidence {confidence}%",
            "Reasons"
        ]
        
        # Positive reasons
        if positive:
            for reason in positive:
                lines.append(f"✓ {reason}")
        else:
            lines.append("✓ Standard Market Conditions")
            
        # Negative reasons / Risks
        lines.append("Risk")
        if negative:
            for risk in negative:
                lines.append(f"✗ {risk}")
        else:
            lines.append("Low")
            
        return "\n".join(lines)
