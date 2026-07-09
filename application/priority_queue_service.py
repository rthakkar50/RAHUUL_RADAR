import logging
from typing import Dict, List, Any
import json
import os

logger = logging.getLogger(__name__)

class PriorityQueueService:
    def __init__(self):
        self.max_top_opportunities = 5
        
    def _calculate_priority_score(self, result: Dict[str, Any]) -> int:
        score = 0
        try:
            # Base logic for rating (0-100) -> Star scale (1-5)
            conf = float(result.get("Confidence", 0))
            overall = float(result.get("Score", 0))
            signal = result.get("Signal", "WAIT")
            
            if signal in ["BUY", "SELL"]:
                score += 40
            
            if conf >= 80: score += 30
            elif conf >= 60: score += 15
            
            if overall >= 80: score += 30
            elif overall >= 60: score += 15
            
            # Map score to 1-5 stars
            if score >= 90: return 5
            if score >= 70: return 4
            if score >= 50: return 3
            if score >= 30: return 2
            return 1
            
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return 1

    def process_queue(self, scan_results: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Ranks scanner results into strict priority queues."""
        ranked_results = []
        for r in scan_results:
            p_score = self._calculate_priority_score(r)
            
            if p_score == 5: level, color, stars = "Critical", "Purple", "★★★★★"
            elif p_score == 4: level, color, stars = "High", "Green", "★★★★☆"
            elif p_score == 3: level, color, stars = "Medium", "Blue", "★★★☆☆"
            elif p_score == 2: level, color, stars = "Low", "Orange", "★★☆☆☆"
            else: level, color, stars = "Ignore", "Gray", "★☆☆☆☆"
            
            ranked_results.append({
                **r,
                "_priority_score": p_score,
                "PriorityLevel": level,
                "PriorityColor": color,
                "Stars": stars
            })
            
        # Sort by strict score then confidence
        ranked_results.sort(key=lambda x: (x.get("_priority_score", 0), float(x.get("Confidence", 0))), reverse=True)
        
        queues = {
            "Highest Priority": [r for r in ranked_results if r["_priority_score"] == 5],
            "High": [r for r in ranked_results if r["_priority_score"] == 4],
            "Medium": [r for r in ranked_results if r["_priority_score"] == 3],
            "Low": [r for r in ranked_results if r["_priority_score"] == 2],
            "Ignore": [r for r in ranked_results if r["_priority_score"] <= 1]
        }
        
        return queues
