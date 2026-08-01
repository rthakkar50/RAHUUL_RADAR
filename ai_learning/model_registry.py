"""
RAHUUL RADAR — AI Learning Platform: Model Registry (Task 3)
============================================================
Tracks model artifacts, version lineage, checksums, champion designation,
and rollback history in JSON registry format.
"""

import os
import json
import logging
import threading
from typing import Dict, List, Any, Optional
from ai_learning.ai_learning_models import ModelArtifact

logger = logging.getLogger("ModelRegistry")


class ModelRegistry:
    """
    Enterprise MLOps Model Registry.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self, registry_file: str = "data/models/registry.json"):
        self.registry_file = registry_file
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        self._registry_lock = threading.Lock()
        self._init_registry()

    def _init_registry(self):
        with self._registry_lock:
            if not os.path.exists(self.registry_file):
                default_data = {
                    "champion_version": "AI_v2",
                    "registered_models": {
                        "AI_v1": {
                            "model_id": "MDL-V1-BASE",
                            "version": "AI_v1",
                            "model_type": "RANDOM_FOREST",
                            "created_at": "2026-07-01T00:00:00",
                            "checksum": "a1b2c3d4e5f67890",
                            "metrics": {"accuracy": 78.5, "profit_factor": 2.1, "max_drawdown": 4.5},
                            "artifact_path": "data/models/AI_v1.joblib",
                            "is_champion": False
                        },
                        "AI_v2": {
                            "model_id": "MDL-V2-PROD",
                            "version": "AI_v2",
                            "model_type": "RANDOM_FOREST",
                            "created_at": "2026-07-15T00:00:00",
                            "checksum": "f9e8d7c6b5a43210",
                            "metrics": {"accuracy": 82.5, "profit_factor": 2.8, "max_drawdown": 3.2},
                            "artifact_path": "data/models/AI_v2.joblib",
                            "is_champion": True
                        }
                    },
                    "rollback_history": ["AI_v1"]
                }
                with open(self.registry_file, "w") as f:
                    json.dump(default_data, f, indent=2)

    def register_model(self, artifact: ModelArtifact):
        """Registers a candidate model artifact in the registry."""
        with self._registry_lock:
            data = self._read_registry()
            data["registered_models"][artifact.version] = artifact.__dict__
            self._write_registry(data)

    def get_champion(self) -> Dict[str, Any]:
        """Returns metadata of the current champion model."""
        with self._registry_lock:
            data = self._read_registry()
            champ_ver = data.get("champion_version", "AI_v2")
            return data["registered_models"].get(champ_ver, {})

    def get_registered_model(self, version: str) -> Optional[Dict[str, Any]]:
        """Returns metadata for a specific registered version."""
        with self._registry_lock:
            data = self._read_registry()
            return data["registered_models"].get(version)

    def set_champion(self, version: str) -> bool:
        """Updates champion model designation and appends previous champion to rollback history."""
        with self._registry_lock:
            data = self._read_registry()
            if version not in data["registered_models"]:
                return False

            old_champ = data["champion_version"]
            data["champion_version"] = version

            for v, m in data["registered_models"].items():
                m["is_champion"] = (v == version)

            if old_champ not in data["rollback_history"]:
                data["rollback_history"].append(old_champ)

            self._write_registry(data)
            logger.info(f"Champion Model updated to: {version}")
            return True

    def _read_registry(self) -> Dict[str, Any]:
        with open(self.registry_file, "r") as f:
            return json.load(f)

    def _write_registry(self, data: Dict[str, Any]):
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)
