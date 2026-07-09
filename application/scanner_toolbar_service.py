import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ScannerToolbarService:
    @staticmethod
    def filter_results(results: List[Dict[str, Any]], search_text: str, quick_filter: str) -> List[Dict[str, Any]]:
        filtered = results
        
        # 1. Search (Symbol, Company, Sector)
        if search_text:
            st = search_text.lower()
            filtered = [
                r for r in filtered 
                if st in r.get("Symbol", "").lower() 
                or st in r.get("Company", "").lower() 
                or st in r.get("Sector", "").lower()
            ]
            
        # 2. Quick Filter
        if quick_filter and quick_filter != "ALL":
            qf = quick_filter.upper()
            if qf in ["BUY", "SELL", "WATCH"]:
                filtered = [r for r in filtered if r.get("Signal", "").upper() == qf]
            elif qf == "HIGH CONFIDENCE":
                filtered = [r for r in filtered if r.get("Confidence", 0.0) >= 80.0]
            elif qf == "TOP SCORE":
                filtered = [r for r in filtered if r.get("Score", 0.0) >= 70.0]
            elif qf == "LOW RISK":
                # Check nested raw_data risk_level if available
                def is_low_risk(r):
                    raw = r.get("_raw_data", {})
                    return "LOW" in str(raw.get("risk_level", "")).upper()
                filtered = [r for r in filtered if is_low_risk(r)]
            elif qf == "TODAY":
                # Assuming all current scan results are today's
                pass
                
        return filtered

    @staticmethod
    def sort_results(results: List[Dict[str, Any]], sort_mode: str) -> List[Dict[str, Any]]:
        if not results:
            return results
            
        if sort_mode == "Highest Score":
            return sorted(results, key=lambda x: (
                x.get("Score", 0),
                x.get("Confidence", 0),
                {"A+": 5, "A": 4, "B": 3, "C": 2, "D": 1, "N/A": 0}.get(x.get("_raw_data", {}).get("institution_grade", "N/A"), 0),
                {"LOW": 3, "MEDIUM": 2, "HIGH": 1}.get(str(x.get("_raw_data", {}).get("risk_level", "")).upper(), 0)
            ), reverse=True)
        elif sort_mode == "Highest Confidence":
            return sorted(results, key=lambda x: x.get("Confidence", 0), reverse=True)
        elif sort_mode == "Highest Volume":
            return sorted(results, key=lambda x: float(x.get("Volume", 0) or 0), reverse=True)
        elif sort_mode == "Highest Momentum":
            def get_mom(r):
                raw = r.get("_raw_data", {})
                scores = raw.get("confidence_calibration", {}).get("Engine Contributions", {})
                return scores.get("momentum_score", {}).get("raw_value", 0)
            return sorted(results, key=get_mom, reverse=True)
        elif sort_mode == "Alphabetical":
            return sorted(results, key=lambda x: x.get("Symbol", ""))
        elif sort_mode == "Price":
            return sorted(results, key=lambda x: x.get("Price", 0), reverse=True)
            
        return results
