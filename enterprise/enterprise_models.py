"""
RAHUUL RADAR — Enterprise Governance Platform: Domain Models
==============================================================
Data contracts for User Management, RBAC, Organizations, Licenses, API Keys, Sessions, and Governance Audit.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class UserProfile:
    user_id: str
    username: str
    email: str
    role: str  # ADMIN, TRADER, VIEWER, RESEARCHER, OPERATOR, GUEST
    org_id: str
    is_active: bool = True
    two_factor_enabled: bool = False
    created_at: str = ""


@dataclass
class Organization:
    org_id: str
    org_name: str
    license_tier: str  # FREE, PRO, ENTERPRISE, INSTITUTIONAL
    max_users: int
    created_at: str = ""


@dataclass
class UserSession:
    session_id: str
    user_id: str
    token: str
    ip_address: str
    created_at: str
    expires_at: str
    is_valid: bool = True


@dataclass
class APIKeyRecord:
    key_id: str
    user_id: str
    org_id: str
    api_key: str
    key_secret_hash: str
    name: str
    is_active: bool = True
    created_at: str = ""
    last_used_at: str = ""


@dataclass
class LicenseRecord:
    license_id: str
    org_id: str
    tier: str
    max_users: int
    features_allowed: List[str]
    expires_at: str
    is_active: bool = True


@dataclass
class GovernanceAuditEntry:
    audit_id: str
    actor_user_id: str
    org_id: str
    action_type: str  # LOGIN, LOGOUT, ORDER_APPROVAL, CONFIG_CHANGE, AI_PROMOTION, PERMISSION_CHANGE
    details: Dict[str, Any]
    timestamp: str = ""
    ip_address: str = "127.0.0.1"


@dataclass
class EnterpriseGovernanceSummary:
    total_users: int
    total_organizations: int
    active_sessions_count: int
    active_api_keys_count: int
    license_tier: str
    audit_entries_count: int
    security_incidents_count: int
    compliance_status: str
