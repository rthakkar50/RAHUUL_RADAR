import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DecisionExplanationService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_decision_data(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses raw scanner data into structured sections for the AI Decision Panel.
        Implements the final AI TRADE DECISION ENGINE (v1.0).
        """
        if not scan_data:
            return {"error": "Not Available"}
            
        raw = scan_data.get("_raw_data", {})
        data_block = raw.get("data", {})
        scores = raw.get("confidence_calibration", {}).get("Engine Contributions", {})
        
        # 1. Determine Base Signal
        original_signal = str(scan_data.get("Signal", "WAIT")).upper()
        confidence = float(scan_data.get("Confidence", 0.0))
        overall_score = float(scan_data.get("Score", 0.0))
        
        # 2. Calculate Trade Grade
        # ELITE (A+, 5 stars): Score >= 90 or Confidence >= 90
        # HIGH (A, 4 stars): Score >= 80 or Confidence >= 80
        # GOOD (B, 3 stars): Score >= 70 or Confidence >= 70
        # Reject everything below (NO TRADE)
        
        trade_grade = ""
        stars = ""
        
        if "BUY" in original_signal or "SELL" in original_signal:
            if overall_score >= 90 or confidence >= 90:
                trade_grade = "★★★★★ Elite"
            elif overall_score >= 80 or confidence >= 80:
                trade_grade = "★★★★ Strong"
            elif overall_score >= 70 or confidence >= 70:
                trade_grade = "★★★ Good"
            else:
                trade_grade = "★★ Watch"
        else:
            trade_grade = "★ Weak"
            
        if "WAIT" in original_signal or "AVOID" in original_signal or "WATCH" in original_signal:
            final_signal = "WATCH"
        else:
            if "BUY" in original_signal:
                final_signal = "BULLISH"
            elif "SELL" in original_signal:
                final_signal = "BEARISH"
            else:
                final_signal = "WATCH"

        # 4. Calculate Risk Level
        risk_map = {
            "LOW": "LOW", "MEDIUM": "MEDIUM", "HIGH": "HIGH",
            "Low": "LOW", "Medium": "MEDIUM", "High": "HIGH"
        }
        risk_level = risk_map.get(str(raw.get("risk_level", "Medium")), "MEDIUM")
        
        # 5. Calculate Holding Period (Based on Momentum and Trend)
        trend_score = scores.get("trend_score", {}).get("raw_value", 0)
        momentum_score = scores.get("momentum_score", {}).get("raw_value", 0)
        if momentum_score > 80:
            holding_period = "2-5 Days"
        elif momentum_score > 60:
            holding_period = "5-10 Days"
        elif trend_score > 70:
            holding_period = "10-20 Days"
        else:
            holding_period = "20+ Days"
            
        # 6. Generate "Why Selected" (Max 5 bullet points based on underlying engines)
        bullets = []
        if trend_score > 80: bullets.append("Strong Trend Strength")
        elif trend_score < 30: bullets.append("Weak Trend")
        
        if momentum_score > 80: bullets.append("High Momentum Breakout")
        elif momentum_score < 30: bullets.append("Low Momentum / Choppy")
        
        vol_score = scores.get("volume_score", {}).get("raw_value", 0)
        if vol_score > 75: bullets.append("Significant Volume Accumulation")
        elif vol_score < 40: bullets.append("Low Volume / Indecision")
        
        inst_grade = raw.get("institution_grade", "")
        if inst_grade in ["A", "A+", "B+"]: bullets.append("Institution Accumulation Detected")
        
        rr_str = scan_data.get("Risk Reward", "")
        try:
            if rr_str.startswith("1:"):
                rr_val = float(rr_str.split(":")[1])
                if rr_val >= 2.5: bullets.append("Excellent Risk Reward Profile")
                elif rr_val < 1.5: bullets.append("Poor Risk Reward Profile")
        except:
            pass
            
        conf_score = scan_data.get("Confidence", 0.0)
        if conf_score > 85: bullets.append("High Confluence Across Engines")
        elif conf_score < 50: bullets.append("Low Engine Agreement / Conflicting Signals")
        
        structure_score = scores.get("structure_score", {}).get("raw_value", 0)
        if structure_score > 80: bullets.append("Clean Market Structure")
        elif structure_score < 40: bullets.append("Messy / Sideways Structure")
        
        # Prioritize positive bullets for BUY/SELL, negative bullets for NO TRADE
        if final_signal == "NO TRADE":
            # Extract negative sounding bullets
            why_trade = [b for b in bullets if "Weak" in b or "Low" in b or "Poor" in b or "Messy" in b]
        else:
            # Extract positive sounding bullets
            why_trade = [b for b in bullets if "Strong" in b or "High" in b or "Significant" in b or "Institution" in b or "Excellent" in b or "Clean" in b]
                
        # Limit to 5 max
        why_trade = why_trade[:5]
        
        # 7. Construct Checklist
        checklist = {
            "trend": trend_score > 60,
            "momentum": momentum_score > 60,
            "volume": vol_score > 60,
            "structure": structure_score > 60,
            "risk": risk_level != "HIGH",
            "confidence": conf_score >= 70,
            "institution": inst_grade in ["A+", "A", "B+", "B"]
        }
        
        # 8. Warnings Panel
        warnings = data_block.get("Warnings", [])
        if not warnings:
            warnings = ["None"]
            
        # 9. Construct Final Response
        return {
            "decision": final_signal,
            "trade_grade": trade_grade.strip(),
            "opportunity_score": overall_score,
            "ai_confidence": confidence,
            "risk_level": risk_level,
            "holding_period": holding_period,
            "why_selected": why_trade,
            "risk_reward": rr_str,
            "checklist": checklist,
            "warnings": warnings,
            "trade_details": {
                "entry": scan_data.get("Entry", 0.0),
                "sl": scan_data.get("Stop Loss", 0.0),
                "target1": scan_data.get("Target 1", 0.0),
                "target2": scan_data.get("Target 2", 0.0),
                "target3": raw.get("target_3", 0.0)
            },
            "Company": scan_data.get("Company", "Not Available"),
            "Sector": scan_data.get("Sector", "Not Available"),
            "Trend": scan_data.get("Trend", "Neutral"),
            "Momentum": scan_data.get("Momentum", "Neutral"),
            "Volume": scan_data.get("Volume", "Not Available"),
            "VWAP": scan_data.get("VWAP", "Not Available"),
            "ICT": scan_data.get("ICT", "Not Available"),
            "no_trade_reason": "Failed to meet strict quality guidelines."
        }
