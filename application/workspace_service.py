import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)
WORKSPACE_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "workspaces.json")

class WorkspaceService:
    def __init__(self):
        self.data = self._load()
        self._ensure_defaults()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(WORKSPACE_FILE):
            os.makedirs(os.path.dirname(WORKSPACE_FILE), exist_ok=True)
            return {"workspaces": {}, "active": "Swing Trading"}
        try:
            with open(WORKSPACE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workspaces: {e}")
            return {"workspaces": {}, "active": "Swing Trading"}

    def _save(self):
        try:
            with open(WORKSPACE_FILE, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save workspaces: {e}")

    def _ensure_defaults(self):
        defaults = ["Swing Trading", "Intraday Trading", "Scalping", "Options", "Portfolio Analysis", "Research Mode", "Paper Trading"]
        for d in defaults:
            if d not in self.data["workspaces"]:
                self.data["workspaces"][d] = {
                    "panels": {"left": True, "right": True, "bottom": False},
                    "geometry": {},
                    "scanner": d.replace(" Trading", ""),
                    "theme": "dark"
                }
        self._save()

    def save_workspace(self, name: str, layout_state: Dict[str, Any]):
        self.data["workspaces"][name] = layout_state
        self.data["active"] = name
        self._save()

    def load_workspace(self, name: str) -> Dict[str, Any]:
        if name in self.data["workspaces"]:
            self.data["active"] = name
            self._save()
            return self.data["workspaces"][name]
        return self.data["workspaces"].get("Swing Trading", {})

    def get_all_workspaces(self) -> List[str]:
        return list(self.data["workspaces"].keys())
        
    def get_active_workspace(self) -> str:
        return self.data.get("active", "Swing Trading")
        
    def delete_workspace(self, name: str):
        if name in self.data["workspaces"] and len(self.data["workspaces"]) > 1:
            del self.data["workspaces"][name]
            if self.data["active"] == name:
                self.data["active"] = list(self.data["workspaces"].keys())[0]
            self._save()
