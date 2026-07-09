from typing import Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedScoringEngine:
    """
    MASTER-09: UNIFIED AI SCORING & DECISION ENGINE (UASDE) V2.0
    The final consensus mechanism. No single engine can approve a trade.
    """
    
    def __init__(self):
        # Configurable weights
        self.weights = {
            "MIE": 0.20,
            "TQE": 0.20,
            "EVE": 0.15,
            "FBDE": 0.15,
            "CPE": 0.15,
            "TREND": 0.05,
            "MOMENTUM": 0.05,
            "VOLUME": 0.05
        }
        
    def generate_final_decision(self, engine_results: Dict) -> Dict:
        """
        Takes a master dictionary of all individual engine results and returns the final decision.
        """
        # Hard Fail Conditions
        mie_mode = engine_results.get("mie", {}).get("mie_mode", "NORMAL")
        cpe_status = engine_results.get("cpe", {}).get("cpe_status", "ACTIVE")
        fbde_status = engine_results.get("fbde", {}).get("status", "PASS")
        tqe_liquidity = engine_results.get("tqe", {}).get("liquidity_pass", True)
        risk_reward_pass = engine_results.get("risk", {}).get("rr_pass", True)
        
        reasons = []
        is_hard_fail = False
        
        if mie_mode == "NO TRADE":
            is_hard_fail = True
            reasons.append("Market Intelligence NO TRADE")
        if cpe_status in ["BLOCK TRADE", "STOP TRADING TODAY"]:
            is_hard_fail = True
            reasons.append(f"Capital Protection Block: {engine_results.get('cpe', {}).get('cpe_reason', '')}")
        if fbde_status == "REJECT":
            is_hard_fail = True
            reasons.append("False Breakout Detected")
        if not tqe_liquidity:
            is_hard_fail = True
            reasons.append("Liquidity Below Minimum")
        if not risk_reward_pass:
            is_hard_fail = True
            reasons.append("Risk/Reward Below Minimum")
            
        if is_hard_fail:
            return self._reject_trade(reasons, "Hard Fail Condition Met", engine_results)
            
        # Calculate Weighted Score
        score = 0.0
        
        # Normalize scores to 0-100 where possible, else assume 100 for PASS.
        mie_score = engine_results.get("mie", {}).get("mie_score", 100)
        cpe_score = engine_results.get("cpe", {}).get("safety_score", 100)
        
        # TQE, EVE, FBDE usually return PASS/FAIL or confidence. Assuming 100 for PASS.
        tqe_score = engine_results.get("tqe", {}).get("confidence", 90)
        eve_score = engine_results.get("eve", {}).get("confidence", 90)
        fbde_score = 100 if fbde_status == "PASS" else 0
        
        trend_score = engine_results.get("trend", {}).get("strength", 80)
        mom_score = engine_results.get("momentum", {}).get("strength", 80)
        vol_score = engine_results.get("volume", {}).get("score", 80)
        
        score += mie_score * self.weights["MIE"]
        score += tqe_score * self.weights["TQE"]
        score += eve_score * self.weights["EVE"]
        score += fbde_score * self.weights["FBDE"]
        score += cpe_score * self.weights["CPE"]
        score += trend_score * self.weights["TREND"]
        score += mom_score * self.weights["MOMENTUM"]
        score += vol_score * self.weights["VOLUME"]
        
        score = max(0, min(100, int(score)))
        
        # Classification & Stars
        if score >= 95:
            classification = "Institutional Grade"
            stars = "★★★★★"
            conviction = "Very High"
        elif score >= 90:
            classification = "Elite"
            stars = "★★★★☆"
            conviction = "High"
        elif score >= 85:
            classification = "High Probability"
            stars = "★★★☆☆"
            conviction = "High"
        elif score >= 80:
            classification = "Tradable"
            stars = "★★☆☆☆"
            conviction = "Medium"
        else:
            classification = "Reject"
            stars = "★☆☆☆☆"
            conviction = "Low"
            
        if score < 80:
            return self._reject_trade([f"Score below threshold ({score}/100)"], "Low Probability", engine_results)
            
        # Compile Top 5 Reasons
        top_reasons = []
        if mie_score >= 90: top_reasons.append("Market Environment Excellent")
        elif mie_score >= 80: top_reasons.append("Market Trend Confirmed")
        
        if cpe_score >= 90: top_reasons.append("High Capital Safety")
        if tqe_score >= 90: top_reasons.append("Strong Trade Qualification")
        if trend_score >= 80: top_reasons.append("Trend Alignment Strong")
        if vol_score >= 80: top_reasons.append("Volume Profile Confirmed")
        if fbde_status == "PASS": top_reasons.append("Clean Structure (FBDE Pass)")
        
        # Ensure we have max 5
        top_reasons = top_reasons[:5]
        
        # Base direction from Trend or MIE (placeholder logic if not passed)
        direction = engine_results.get("direction", "WAIT")
        
        decision = {
            "signal": direction,
            "score": score,
            "classification": classification,
            "stars": stars,
            "conviction": conviction,
            "reasons": top_reasons,
            "raw_audit": engine_results,
            "timestamp": datetime.now().isoformat()
        }
        
        self._audit_log(decision)
        return decision
        
    def _reject_trade(self, reasons: List[str], primary_reason: str, audit: Dict) -> Dict:
        decision = {
            "signal": "WAIT",
            "score": 0,
            "classification": "Reject",
            "stars": "★☆☆☆☆",
            "conviction": "Very Low",
            "reasons": reasons[:5],
            "reject_reason": primary_reason,
            "raw_audit": audit,
            "timestamp": datetime.now().isoformat()
        }
        self._audit_log(decision)
        return decision
        
    def _audit_log(self, decision: Dict):
        # AI AUDIT LOGGING
        logger.debug(f"UASDE Audit Log: Signal={decision['signal']} Score={decision['score']} Reasons={decision['reasons']}")
