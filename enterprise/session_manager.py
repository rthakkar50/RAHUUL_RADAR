"""
RAHUUL RADAR — Enterprise Governance: Session Manager & Security (Task 3 & Task 8)
===================================================================================
Manages secure user sessions, session timeouts, rate limiting, and brute-force protection.
"""

import uuid
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enterprise.enterprise_models import UserSession


class EnterpriseSessionManager:
    """
    Session Lifecycle & Rate Limiter Manager.
    """

    def __init__(self, session_timeout_mins: int = 60):
        self.session_timeout_mins = session_timeout_mins
        self._sessions: Dict[str, UserSession] = {}
        self._login_attempts: Dict[str, int] = {}
        self._rate_limits: Dict[str, float] = {}

    def create_session(self, user_id: str, ip_address: str = "127.0.0.1") -> UserSession:
        """Creates a secure session token."""
        session_id = f"SES-{uuid.uuid4().hex[:12].upper()}"
        token = hashlib.sha256(f"{session_id}:{user_id}:{time.time()}".encode()).hexdigest()

        now = datetime.now()
        expires = now + timedelta(minutes=self.session_timeout_mins)

        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            token=token,
            ip_address=ip_address,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            is_valid=True
        )

        self._sessions[token] = session
        return session

    def validate_session(self, token: str) -> bool:
        """Validates session token and checks timeout."""
        if token not in self._sessions:
            return False

        sess = self._sessions[token]
        if not sess.is_valid:
            return False

        if datetime.fromisoformat(sess.expires_at) < datetime.now():
            sess.is_valid = False
            return False

        return True

    def check_brute_force_lock(self, username: str) -> bool:
        """Brute Force Protection: Locks out if > 5 failed attempts."""
        attempts = self._login_attempts.get(username, 0)
        return attempts >= 5

    def record_login_attempt(self, username: str, success: bool):
        """Records login attempt for brute force tracking."""
        if success:
            self._login_attempts[username] = 0
        else:
            self._login_attempts[username] = self._login_attempts.get(username, 0) + 1

    def check_rate_limit(self, client_id: str, limit_seconds: float = 0.05) -> bool:
        """Rate Limiting: Enforces minimum time between API requests."""
        now = time.time()
        last_time = self._rate_limits.get(client_id, 0.0)
        if now - last_time < limit_seconds:
            return False  # Rate limit exceeded

        self._rate_limits[client_id] = now
        return True
