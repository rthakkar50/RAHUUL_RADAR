"""
MASTER-28: Trade Priority Engine (TPE)
Ranks and prioritizes all approved trades from highest quality to lowest quality.
Ensures that the best setups (Quality + Confidence + RR) bubble to the top.
Capped at MAX_PER_CATEGORY per category (BUY, SELL, WATCH).
"""
from typing import List, Dict

MAX_PER_CATEGORY = 10

class TradePriorityEngine:
    def __init__(self):
        pass
        
    def _parse_rr(self, rr_str: str) -> float:
        """Parses a Risk Reward string '1:2.5' into a float 2.5"""
        try:
            return float(str(rr_str).replace("1:", "").strip())
        except Exception:
            return 1.0

    def _normalize_rr(self, rr: float) -> float:
        """Normalizes RR to a 0-100 scale for scoring. Maxes out around 1:4 (100)."""
        if rr < 1.0: return 0.0
        # Linear scale where 1.5 = 50, 4.0 = 100
        norm = ((rr - 1.0) / 3.0) * 100.0
        return max(0.0, min(100.0, norm))

    def _get_grade(self, score: float) -> str:
        if score >= 95: return "★★★★★"
        if score >= 90: return "★★★★☆"
        if score >= 85: return "★★★☆☆"
        if score >= 75: return "★★☆☆☆"
        return "★☆☆☆☆"
        
    def _get_reason(self, rank: int, score: float) -> str:
        if rank == 1:
            return "Absolute Highest Quality Setup"
        elif rank <= 3:
            return "Top Tier Setup (Strong Consensus & R/R)"
        elif score >= 90:
            return "Very High Priority Opportunity"
        elif score >= 85:
            return "High Priority Opportunity"
        return "Standard Approved Setup"

    def rank_trades(self, trades: List[Dict]) -> List[Dict]:
        """
        Takes a list of Elite-approved trades and ranks them.
        Limits the output to MAX_PER_CATEGORY per category.
        """
        if not trades:
            return []
            
        ranked_trades = []
        for trade in trades:
            try:
                # 1. Extract base metrics
                elite_score = float(trade.get("Score", 0.0))
                conf_str = str(trade.get("Confidence", "0%")).replace("%", "")
                confidence = float(conf_str)
                
                rr_val = self._parse_rr(trade.get("Risk Reward", "1:1"))
                rr_score = self._normalize_rr(rr_val)
                
                # 2. Calculate True Priority Score (0-100)
                # Elite Score (Consensus) is 70%
                # Risk Reward is 15%
                # Confidence is 15%
                priority_score = (elite_score * 0.70) + (rr_score * 0.15) + (confidence * 0.15)
                priority_score = max(0.0, min(100.0, priority_score))
                
                trade["_Priority_Score"] = priority_score
                ranked_trades.append(trade)
                
            except Exception as e:
                # Fallback if something fails
                trade["_Priority_Score"] = float(trade.get("Score", 0.0))
                ranked_trades.append(trade)
                
        # 3. Group by Category
        grouped_trades = {}
        for trade in ranked_trades:
            sig = str(trade.get("Signal", "UNKNOWN")).upper()
            # Normalize signals to robust standard names
            if "BUY" in sig: sig_key = "BUY"
            elif "SELL" in sig: sig_key = "SELL"
            elif "READY" in sig or "SETUP" in sig: sig_key = "READY"
            elif "WATCH" in sig: sig_key = "WATCH"
            else: sig_key = "OTHER"
            
            if sig_key not in grouped_trades:
                grouped_trades[sig_key] = []
            grouped_trades[sig_key].append(trade)
            
        final_ranked_trades = []
        
        # 4. Sort, Limit, and Format per category
        for sig_key, group in grouped_trades.items():
            # Sort by True Priority Score descending
            group.sort(key=lambda x: x.get("_Priority_Score", 0.0), reverse=True)
            
            # Enforce Maximum limitation per category
            group = group[:MAX_PER_CATEGORY]
            
            # Inject display fields
            for i, trade in enumerate(group):
                rank = i + 1
                score = trade.get("_Priority_Score", 0.0)
                
                trade["Priority Rank"] = f"#{rank}"
                trade["Priority Score"] = f"{score:.1f}"
                trade["Priority Grade"] = self._get_grade(score)
                trade["Priority Reason"] = self._get_reason(rank, score)
                
                final_ranked_trades.append(trade)
                
        return final_ranked_trades
