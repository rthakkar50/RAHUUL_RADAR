"""
RAHUUL RADAR — Enterprise Governance: Governance Audit Center (Task 7)
========================================================================
Tracks Logins, Logouts, Order Approvals, Configuration Changes, AI Promotion Approvals, and Permission Changes.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any
from enterprise.enterprise_models import GovernanceAuditEntry

logger = logging.getLogger("GovernanceAudit")


class GovernanceAuditCenter:
    """
    Enterprise Governance Audit Trail Logger.
    """

    def __init__(self):
        self._audit_trail: List[GovernanceAuditEntry] = []

    def record_governance_event(
        self,
        actor_user_id: str,
        org_id: str,
        action_type: str,
        details: Dict[str, Any],
        ip_address: str = "127.0.0.1"
    ) -> GovernanceAuditEntry:
        """Records a compliance audit event."""
        audit_id = f"GOV-{uuid.uuid4().hex[:8].upper()}"
        entry = GovernanceAuditEntry(
            audit_id=audit_id,
            actor_user_id=actor_user_id,
            org_id=org_id,
            action_type=action_type.upper(),
            details=details,
            timestamp=datetime.now().isoformat(),
            ip_address=ip_address
        )
        self._audit_trail.append(entry)
        logger.info(f"Governance Audit Event: {audit_id} | {action_type} by {actor_user_id}")
        return entry

    def get_audit_records(self, limit: int = 100) -> List[GovernanceAuditEntry]:
        return self._audit_trail[-limit:]
