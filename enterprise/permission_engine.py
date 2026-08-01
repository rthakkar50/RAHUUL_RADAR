"""
RAHUUL RADAR — Enterprise Governance: Permission Engine (Task 2)
================================================================
Enforces permission checks across APIs, Dashboards, and Subsystems.
"""

from typing import Dict, Any, Optional
from enterprise.role_manager import RolePermissionManager


class PermissionEngine:
    """
    Enforces Fine-Grained Module & Endpoint Permissions.
    """

    def __init__(self):
        self.role_manager = RolePermissionManager()

    def authorize_request(self, user_role: str, endpoint_action: str) -> bool:
        """Evaluates whether the given user role is authorized for the endpoint/action."""
        return self.role_manager.has_permission(user_role, endpoint_action)
