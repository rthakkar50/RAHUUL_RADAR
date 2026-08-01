"""
RAHUUL RADAR — Enterprise Governance: API Key Manager (Task 5)
===============================================================
Manages API Keys: Create, Rotate, Disable, Revoke, and Audit.
"""

import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from enterprise.enterprise_models import APIKeyRecord


class APIKeyManager:
    """
    API Key Lifecycle & Rotation Manager.
    """

    def __init__(self):
        self._keys: Dict[str, APIKeyRecord] = {}

    def create_api_key(self, user_id: str, org_id: str, name: str) -> APIKeyRecord:
        """Generates a new secure API Key and Secret."""
        key_id = f"KEY-{uuid.uuid4().hex[:8].upper()}"
        api_key = f"RR-LIVE-{uuid.uuid4().hex}"
        secret_hash = hashlib.sha256(f"{api_key}:secret".encode()).hexdigest()

        rec = APIKeyRecord(
            key_id=key_id,
            user_id=user_id,
            org_id=org_id,
            api_key=api_key,
            key_secret_hash=secret_hash,
            name=name,
            is_active=True,
            created_at=datetime.now().isoformat()
        )
        self._keys[key_id] = rec
        return rec

    def rotate_api_key(self, key_id: str) -> Optional[APIKeyRecord]:
        """Rotates an existing API key, revoking the old string."""
        if key_id in self._keys:
            old = self._keys[key_id]
            old.is_active = False
            return self.create_api_key(old.user_id, old.org_id, f"{old.name}_rotated")
        return None

    def revoke_api_key(self, key_id: str) -> bool:
        """Revokes an API key."""
        if key_id in self._keys:
            self._keys[key_id].is_active = False
            return True
        return False
