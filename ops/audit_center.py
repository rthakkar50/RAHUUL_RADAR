"""
RAHUUL RADAR — Operations Platform: Audit Center (Task 4)
=========================================================
Central audit logging center for Orders, AI Decisions, Risk Decisions, System Events, and User Actions.
Enforces automatic sensitive data redaction.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any
from ops.ops_models import AuditLogEntry

logger = logging.getLogger("AuditCenter")


class AuditCenter:
    """
    Enterprise Centralized Audit Center.
    """

    def __init__(self):
        self._audit_logs: List[AuditLogEntry] = []

    def record_audit_event(
        self,
        event_type: str,
        source_module: str,
        action: str,
        details: Dict[str, Any]
    ) -> AuditLogEntry:
        """Records an audit event with sensitive credential redaction."""
        sanitized_details = self._sanitize_dict(details)
        audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

        entry = AuditLogEntry(
            audit_id=audit_id,
            event_type=event_type.upper(),
            source_module=source_module,
            action=action,
            details=sanitized_details,
            timestamp=datetime.now().isoformat(),
            sensitive_redacted=True
        )

        self._audit_logs.append(entry)
        logger.info(f"Audit Event Recorded: {audit_id} | {event_type} | {source_module} | {action}")
        return entry

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redacts API keys, tokens, passwords, and secrets."""
        if not isinstance(data, dict):
            return {}

        sanitized = {}
        sensitive_keys = ["api_key", "api_secret", "token", "access_token", "password", "secret"]

        for k, v in data.items():
            if any(sk in k.lower() for sk in sensitive_keys):
                sanitized[k] = "[REDACTED_CREDENTIAL]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    def get_audit_trail(self, limit: int = 50) -> List[AuditLogEntry]:
        return self._audit_logs[-limit:]
