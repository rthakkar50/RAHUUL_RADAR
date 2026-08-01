"""
RAHUUL RADAR — Operations Platform: Alert Manager (Task 3)
==========================================================
Generates & dispatches alerts for API Down, DB Errors, Broker Errors, High Memory/CPU, Model Drift, etc.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any
from ops.ops_models import AlertItem, SystemHealthStatus


class AlertManager:
    """
    SRE Incident & Alert Manager.
    """

    def __init__(self):
        self._alerts: List[AlertItem] = []

    def evaluate_health_alerts(self, health: SystemHealthStatus) -> List[AlertItem]:
        """Evaluates health status and triggers alerts for threshold breaches."""
        new_alerts = []
        now_str = datetime.now().isoformat()

        if health.memory_pct > 85.0:
            new_alerts.append(AlertItem(
                alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
                severity="WARNING",
                source="SYSTEM",
                title="High Memory Usage",
                message=f"System memory usage at {health.memory_pct}%",
                timestamp=now_str
            ))

        if health.cpu_pct > 85.0:
            new_alerts.append(AlertItem(
                alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
                severity="WARNING",
                source="SYSTEM",
                title="High CPU Usage",
                message=f"System CPU usage at {health.cpu_pct}%",
                timestamp=now_str
            ))

        self._alerts.extend(new_alerts)
        return new_alerts

    def create_custom_alert(self, severity: str, source: str, title: str, message: str) -> AlertItem:
        """Creates a custom operational alert (e.g. Model Drift, Broker Error)."""
        alert = AlertItem(
            alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
            severity=severity.upper(),
            source=source.upper(),
            title=title,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        self._alerts.append(alert)
        return alert

    def get_active_alerts(self) -> List[AlertItem]:
        return [a for a in self._alerts if not a.resolved]
