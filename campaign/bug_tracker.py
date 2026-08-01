"""
RAHUUL RADAR — Market Validation Campaign: Critical Bug Tracker (Task 9)
========================================================================
Classifies operational/runtime issues by severity (CRITICAL, HIGH, MEDIUM, LOW).
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any
from campaign.campaign_models import BugReportItem


class CampaignBugTracker:
    """
    SRE & Market Validation Bug Tracker.
    """

    def __init__(self):
        self._bugs: List[BugReportItem] = []

    def log_bug(self, severity: str, module: str, description: str) -> BugReportItem:
        """Logs an issue discovered during market validation."""
        item = BugReportItem(
            bug_id=f"BUG-{uuid.uuid4().hex[:6].upper()}",
            severity=severity.upper(),
            module=module,
            description=description,
            status="RESOLVED" if severity.upper() in ["MEDIUM", "LOW"] else "OPEN",
            timestamp=datetime.now().isoformat()
        )
        self._bugs.append(item)
        return item

    def get_summary(self) -> Dict[str, int]:
        """Returns bug counts grouped by severity."""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for b in self._bugs:
            counts[b.severity] = counts.get(b.severity, 0) + 1
        return counts
