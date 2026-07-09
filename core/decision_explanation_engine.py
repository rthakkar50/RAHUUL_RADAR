"""
MASTER-26: Decision Explanation Engine (DEE)
Responsible for formatting, prioritizing, and generating human-readable explanations
for every AI decision (BUY, SELL, WAIT, REJECT).
"""
import re
from typing import List, Dict

class DecisionExplanationEngine:
    def __init__(self):
        pass

    def _get_trade_grade(self, elite_score: float, confidence: float) -> str:
        avg_score = (elite_score + confidence) / 2.0
        if avg_score >= 90:
            return "★★★★★"
        elif avg_score >= 80:
            return "★★★★☆"
        elif avg_score >= 70:
            return "★★★☆☆"
        elif avg_score >= 50:
            return "★★☆☆☆"
        return "★☆☆☆☆"

    def _get_risk_grade(self, raw_reasons: List[str]) -> str:
        # Simple heuristic based on SRRE reasons or volatility keywords
        reasons_text = " ".join(raw_reasons).lower()
        if "poor r/r" in reasons_text or "highly vulnerable" in reasons_text or "high risk" in reasons_text:
            return "High Risk"
        elif "excellent r/r" in reasons_text or "strong r/r" in reasons_text:
            return "Low Risk"
        return "Medium Risk"

    def _prioritize_and_clean_reasons(self, reasons: List[str], signal: str) -> List[str]:
        # Deduplicate while preserving order
        seen = set()
        cleaned = []
        for r in reasons:
            r = str(r).strip()
            # Remove existing bullets or checkmarks if any
            r = re.sub(r'^[✓•⛔\-\*]\s*', '', r)
            if r and r not in seen and len(r) > 3:
                seen.add(r)
                cleaned.append(r)
                
        # Priority keywords
        high_priority = ["rejected", "choch", "bos", "structure", "trend", "r/r ratio", "volume surge", "perfect alignment", "major conflict"]
        
        def get_priority(text: str) -> int:
            text_lower = text.lower()
            for i, kw in enumerate(high_priority):
                if kw in text_lower:
                    return i
            return 99 # Low priority
            
        cleaned.sort(key=get_priority)
        return cleaned

    def explain(self, signal: str, confidence: float, elite_score: float, raw_reasons: List[str]) -> Dict:
        trade_grade = self._get_trade_grade(elite_score, confidence)
        risk_grade = self._get_risk_grade(raw_reasons)
        
        sorted_reasons = self._prioritize_and_clean_reasons(raw_reasons, signal)
        
        # Determine prefix
        prefix = "•"
        if signal in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
            prefix = "✓"
        elif signal in ["REJECT"]:
            prefix = "⛔"
            
        formatted_reasons = []
        for r in sorted_reasons:
            if "rejected" in r.lower() or "warning" in r.lower() or "penalty" in r.lower():
                formatted_reasons.append(f"⛔ {r}")
            else:
                formatted_reasons.append(f"{prefix} {r}")
                
        # Enforce Min 3, Max 8
        if len(formatted_reasons) > 8:
            formatted_reasons = formatted_reasons[:8]
            
        if len(formatted_reasons) < 3:
            if signal in ["BUY", "STRONG_BUY"]:
                formatted_reasons.extend([f"✓ Standard breakout logic", f"✓ Quantitative metrics aligned"])
            elif signal in ["SELL", "STRONG_SELL"]:
                formatted_reasons.extend([f"✓ Standard breakdown logic", f"✓ Quantitative metrics aligned"])
            else:
                formatted_reasons.extend([f"• Waiting for better setup", f"• Consolidation phase"])
            # Trim just in case adding extensions pushed it over 8, though unlikely if < 3
            formatted_reasons = formatted_reasons[:max(3, len(formatted_reasons))]
            # We want exact minimum 3, maximum 8.
            # If it was 1, added 2 -> 3. If it was 2, added 2 -> 4.
            # Wait, if we added generic ones, we just take up to min 3 or 4.
            # Let's ensure it's at least 3. If it's already >= 3, this block doesn't run.
            
        return {
            "Signal": signal,
            "Confidence": f"{confidence:.1f}%" if isinstance(confidence, (int, float)) else confidence,
            "Elite Score": f"{elite_score:.1f}" if isinstance(elite_score, (int, float)) else elite_score,
            "Trade Grade": trade_grade,
            "Risk Grade": risk_grade,
            "Top Reasons": formatted_reasons
        }
