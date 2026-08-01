"""
RAHUUL RADAR — Enterprise Governance: Role & Permission Engine (Task 1 & Task 2)
=================================================================================
Role-Based Access Control (RBAC) supporting Admin, Trader, Viewer, Researcher, Operator, and Guest.
"""

from typing import Dict, List, Set


class RolePermissionManager:
    """
    Enterprise RBAC Permission Matrix.
    """

    ROLE_PERMISSIONS: Dict[str, Set[str]] = {
        "ADMIN": {
            "api:all", "trade:all", "paper:all", "quant:all", "ai:all", "ops:all",
            "user:manage", "org:manage", "license:manage", "audit:view"
        },
        "TRADER": {
            "api:trade", "trade:execute", "paper:execute", "dashboard:view",
            "portfolio:view", "reports:view"
        },
        "OPERATOR": {
            "api:ops", "ops:health", "ops:metrics", "ops:logs", "paper:execute",
            "dashboard:view"
        },
        "RESEARCHER": {
            "quant:analyze", "quant:reports", "ai:evaluate", "dashboard:view",
            "paper:view"
        },
        "VIEWER": {
            "dashboard:view", "portfolio:view", "reports:view"
        },
        "GUEST": {
            "dashboard:view_limited"
        }
    }

    def has_permission(self, role: str, required_permission: str) -> bool:
        """Checks if a user role possesses the required permission."""
        role_upper = role.upper()
        if role_upper not in self.ROLE_PERMISSIONS:
            return False

        perms = self.ROLE_PERMISSIONS[role_upper]
        if "api:all" in perms:
            return True

        return required_permission in perms
