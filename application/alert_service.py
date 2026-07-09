import json
import os
import logging
from typing import Dict, List, Any
import datetime
import uuid

logger = logging.getLogger(__name__)

ALERTS_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "alerts.json")

class AlertService:
    def __init__(self):
        self.data = self._load()
        self.max_age_days = 7

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(ALERTS_FILE):
            os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
            return {"alerts": []}
        try:
            with open(ALERTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
            return {"alerts": []}

    def _save(self):
        try:
            with open(ALERTS_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")

    def create_alert(self, alert_type: str, symbol: str, signal: str, confidence: str, priority: str, reason: str, color: str):
        alert = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": alert_type,
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence,
            "priority": priority,
            "reason": reason,
            "color": color,
            "unread": True
        }
        # Insert at top
        self.data["alerts"].insert(0, alert)
        self._cleanup_old_alerts()
        self._save()
        return alert

    def _cleanup_old_alerts(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(days=self.max_age_days)
        valid = []
        for a in self.data["alerts"]:
            try:
                dt = datetime.datetime.strptime(a["timestamp"], "%Y-%m-%d %H:%M:%S")
                if dt >= cutoff:
                    valid.append(a)
            except:
                valid.append(a)
        self.data["alerts"] = valid

    def process_scan_completion(self, scan_results: List[Dict[str, Any]]) -> List[Dict]:
        """Analyzes scan results and spawns alerts only for meaningful state changes"""
        new_alerts = []
        for r in scan_results:
            signal = r.get("Signal", "WAIT")
            symbol = r.get("Symbol", "N/A")
            conf = str(r.get("Confidence", 0))
            
            # Simple thresholding to mimic intelligent state change detection
            if signal == "BUY" and float(conf) >= 80.0:
                alert = self.create_alert("BUY Signal", symbol, signal, conf, "Critical", "High confidence BUY signal detected", "Green")
                new_alerts.append(alert)
            elif signal == "SELL" and float(conf) >= 80.0:
                alert = self.create_alert("SELL Signal", symbol, signal, conf, "Critical", "High confidence SELL signal detected", "Red")
                new_alerts.append(alert)
                
        # Also log scanner completed
        if scan_results:
            alert = self.create_alert("Scanner Completed", "SYSTEM", "INFO", "-", "Low", f"Scan finished processing {len(scan_results)} symbols", "Blue")
            new_alerts.append(alert)
            
        return new_alerts

    def mark_all_read(self):
        for a in self.data["alerts"]:
            a["unread"] = False
        self._save()
        
    def dismiss_all(self):
        self.data["alerts"] = []
        self._save()

    def get_alerts(self) -> List[Dict]:
        return self.data["alerts"]
