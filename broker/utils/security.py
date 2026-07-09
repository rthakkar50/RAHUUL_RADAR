import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    """Manages encrypted storage of broker tokens and secrets."""
    
    def __init__(self, storage_path: str = "config/broker_tokens.enc"):
        self.storage_path = Path(storage_path)
        self.fernet = self._derive_key()
        
    def _derive_key(self) -> Fernet:
        # Bind the key to a local environment variable or hardware ID in production
        # Using a fallback static salt for development
        salt = b'rahuul_radar_secure_salt_2026'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        # We would typically use a user password or OS keyring
        machine_secret = os.environ.get("RADAR_MASTER_KEY", "default_dev_key").encode()
        key = base64.urlsafe_b64encode(kdf.derive(machine_secret))
        return Fernet(key)
        
    def store_token(self, broker_name: str, payload: dict):
        current_data = self._read_all()
        current_data[broker_name] = payload
        
        encrypted = self.fernet.encrypt(json.dumps(current_data).encode())
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_bytes(encrypted)
        
    def retrieve_token(self, broker_name: str) -> dict:
        current_data = self._read_all()
        return current_data.get(broker_name, {})
        
    def _read_all(self) -> dict:
        if not self.storage_path.exists():
            return {}
        try:
            encrypted = self.storage_path.read_bytes()
            decrypted = self.fernet.decrypt(encrypted)
            return json.loads(decrypted)
        except Exception:
            # Corrupt or invalid key, return empty
            return {}
