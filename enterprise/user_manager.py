"""
RAHUUL RADAR — Enterprise Governance: User Manager (Task 1)
============================================================
Manages Enterprise User Profiles across Admin, Trader, Viewer, Researcher, Operator, and Guest roles.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enterprise.enterprise_models import UserProfile


class EnterpriseUserManager:
    """
    Enterprise User Profile Manager.
    """

    def __init__(self):
        self._users: Dict[str, UserProfile] = {}

    def create_user(
        self,
        username: str,
        email: str,
        role: str = "TRADER",
        org_id: str = "ORG-DEFAULT"
    ) -> UserProfile:
        """Creates a new enterprise user profile."""
        user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
        user = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            role=role.upper(),
            org_id=org_id,
            is_active=True,
            created_at=datetime.now().isoformat()
        )
        self._users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        return self._users.get(user_id)

    def list_users(self) -> List[UserProfile]:
        return list(self._users.values())
