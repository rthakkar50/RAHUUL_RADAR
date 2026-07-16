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

    def _extract_component_scores(self, raw_reasons: List[str], raw_data: Dict = None) -> Dict[str, Any]:
        scores = {
            "Trend": "N/A", "Mom": "N/A", "Struct": "N/A", 
            "Vol": "N/A", "ADX": "N/A", "MTF": "N/A",
            "trend_is_100_scale": False
        }
        
        # 1. Prefer structured values available from raw_data
        if raw_data:
            try:
                if "trend" in raw_data and "score" in raw_data["trend"]:
                    scores["Trend"] = f"{raw_data['trend']['score']:.1f}"
                    scores["trend_is_100_scale"] = True
                if "momentum" in raw_data and "score" in raw_data["momentum"]:
                    scores["Mom"] = f"{raw_data['momentum']['score']:.1f}"
                if "structure" in raw_data and "score" in raw_data["structure"]:
                    scores["Struct"] = f"{raw_data['structure']['score']:.1f}"
                if "volume" in raw_data and "score" in raw_data["volume"]:
                    scores["Vol"] = f"{raw_data['volume']['score']:.1f}"
            except Exception:
                pass
            
        # 2. String parsing as fallback
        for r in raw_reasons:
            if scores["Trend"] == "N/A" and "Trend Weight" in r and "Score:" in r:
                scores["Trend"] = r.split("Score:")[1].strip()
            elif scores["Mom"] == "N/A" and "Momentum Weight" in r and "Score:" in r:
                scores["Mom"] = r.split("Score:")[1].strip()
            elif scores["Struct"] == "N/A" and "Structure Weight" in r and "Score:" in r:
                scores["Struct"] = r.split("Score:")[1].strip()
            elif "ADX Adjusted Confidence:" in r:
                scores["ADX"] = "Yes"
            elif "ADX < 20 Sideways Filter" in r:
                scores["ADX"] = "Weak"
            elif "ADX Engine: Failed" in r:
                scores["ADX"] = "Fail"
            elif "MTCE: Perfect Alignment" in r:
                scores["MTF"] = "Align"
            elif "MTCE: Major Conflict" in r:
                scores["MTF"] = "Conflict"
            elif "MTCE: Partial Alignment" in r:
                scores["MTF"] = "Partial"
            elif "MTCE: No Alignment" in r:
                scores["MTF"] = "None"
            elif scores["Vol"] == "N/A" and ("Volume confirmation missing" in r or "Volume penalty" in r):
                scores["Vol"] = "Weak"
            elif scores["Vol"] == "N/A" and "Volume Surge" in r:
                scores["Vol"] = "Strong"
        return scores

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

    def explain(self, signal: str, confidence: float, elite_score: float, raw_reasons: List[str], raw_data: Dict = None) -> Dict:
        trade_grade = self._get_trade_grade(elite_score, confidence)
        risk_grade = self._get_risk_grade(raw_reasons)
        
        sorted_reasons = self._prioritize_and_clean_reasons(raw_reasons, signal)
        
        component_scores = self._extract_component_scores(raw_reasons, raw_data)
        
        # Determine prefix
        prefix = "•"
        if signal in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
            prefix = "✓"
        elif signal in ["REJECT"]:
            prefix = "⛔"
            
        formatted_reasons = []
        for r in sorted_reasons:
            if "Weight (Max" in r or "ADX Adjusted Confidence" in r or "MTCE:" in r:
                continue # Skip raw scoring logs since they are in breakdown
                
            if "rejected" in r.lower() or "warning" in r.lower() or "penalty" in r.lower():
                formatted_reasons.append(f"⛔ {r}")
            else:
                formatted_reasons.append(f"{prefix} {r}")
                
        if len(formatted_reasons) < 3:
            try:
                t_score = float(component_scores["Trend"]) if component_scores["Trend"] != "N/A" else None
            except ValueError:
                t_score = None
                
            is_strong_bullish = False
            is_strong_bearish = False
            if t_score is not None:
                if component_scores.get("trend_is_100_scale"):
                    is_strong_bullish = t_score >= 65
                    is_strong_bearish = t_score <= 35
                else:
                    is_strong_bullish = t_score >= 20
                    is_strong_bearish = t_score <= 10
                    
            if signal in ["BUY", "STRONG_BUY"]:
                if is_strong_bullish:
                    formatted_reasons.append("✓ Strong Bullish Trend Continuity")
                else:
                    formatted_reasons.append("✓ Standard breakout logic")
                    
                if component_scores["MTF"] == "Align":
                    formatted_reasons.append("✓ Multi-Timeframe Alignment Confirmed")
                elif component_scores["ADX"] == "Yes":
                    formatted_reasons.append("✓ ADX Confirms Directional Strength")
                else:
                    formatted_reasons.append("✓ Quantitative metrics aligned")
            elif signal in ["SELL", "STRONG_SELL"]:
                if is_strong_bearish:
                    formatted_reasons.append("✓ Strong Bearish Trend Continuity")
                else:
                    formatted_reasons.append("✓ Standard breakdown logic")
                    
                if component_scores["MTF"] == "Align":
                    formatted_reasons.append("✓ Multi-Timeframe Alignment Confirmed")
                elif component_scores["ADX"] == "Yes":
                    formatted_reasons.append("✓ ADX Confirms Directional Strength")
                else:
                    formatted_reasons.append("✓ Quantitative metrics aligned")
            else:
                formatted_reasons.extend([f"• Waiting for better setup", f"• Consolidation phase"])
            formatted_reasons = formatted_reasons[:max(3, len(formatted_reasons))]

        # Enforce Min 3, Max 7 (leaving room for breakdown)
        if len(formatted_reasons) > 7:
            formatted_reasons = formatted_reasons[:7]
            
        breakdown_str = (
            "📊 Breakdown\n"
            f"Trend: {component_scores['Trend']}\n"
            f"Momentum: {component_scores['Mom']}\n"
            f"Structure: {component_scores['Struct']}\n"
            f"Volume: {component_scores['Vol']}\n"
            f"ADX: {component_scores['ADX']}\n"
            f"MTF: {component_scores['MTF']}\n"
            f"Confidence: {confidence:.1f}%"
        )
        formatted_reasons.append(breakdown_str)
            
        return {
            "Signal": signal,
            "Confidence": f"{confidence:.1f}%" if isinstance(confidence, (int, float)) else confidence,
            "Elite Score": f"{elite_score:.1f}" if isinstance(elite_score, (int, float)) else elite_score,
            "Trade Grade": trade_grade,
            "Risk Grade": risk_grade,
            "Top Reasons": formatted_reasons
        }
