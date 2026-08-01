"""
RAHUUL RADAR — Enterprise Governance: Organization Manager (Task 4)
====================================================================
Manages Multi-Tenant Organizations, Users, Accounts, and Data Isolation boundaries.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enterprise.enterprise_models import Organization


class OrganizationManager:
    """
    Multi-Tenant Organization & Data Isolation Manager.
    """

    def __init__(self):
        self._orgs: Dict[str, Organization] = {}
        self._init_default_org()

    def _init_default_org(self):
        default_org = Organization(
            org_id="ORG-DEFAULT",
            org_name="RAHUUL_RADAR Enterprise Default",
            license_tier="PRO",
            max_users=10,
            created_at=datetime.now().isoformat()
        )
        self._orgs["ORG-DEFAULT"] = default_org

    def create_organization(self, org_name: str, license_tier: str = "ENTERPRISE", max_users: int = 50) -> Organization:
        """Creates a new multi-tenant organization."""
        org_id = f"ORG-{uuid.uuid4().hex[:8].upper()}"
        org = Organization(
            org_id=org_id,
            org_name=org_name,
            license_tier=license_tier.upper(),
            max_users=max_users,
            created_at=datetime.now().isoformat()
        )
        self._orgs[org_id] = org
        return org

    def get_organization(self, org_id: str) -> Optional[Organization]:
        return self._orgs.get(org_id)
