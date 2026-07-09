import json
import base64
from typing import List, Optional
from .filters.models import ScannerProfile, FilterCondition, FilterOperator
import os

class ScannerProfileManager:
    def __init__(self, profiles_dir: str = "config/profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(self.profiles_dir, exist_ok=True)
        
    def save_scanner(self, profile: ScannerProfile):
        path = os.path.join(self.profiles_dir, f"{profile.name}.json")
        data = {
            "name": profile.name,
            "description": profile.description,
            "conditions": [
                {"field": c.field, "operator": c.operator.value, "value": c.value}
                for c in profile.conditions
            ]
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
            
    def load_scanner(self, name: str) -> Optional[ScannerProfile]:
        path = os.path.join(self.profiles_dir, f"{name}.json")
        if not os.path.exists(path):
            return None
            
        with open(path, "r") as f:
            data = json.load(f)
            
        conditions = []
        for c in data.get("conditions", []):
            try:
                op = FilterOperator(c["operator"])
                conditions.append(FilterCondition(field=c["field"], operator=op, value=c["value"]))
            except ValueError:
                continue
                
        return ScannerProfile(name=data.get("name", name), description=data.get("description", ""), conditions=conditions)
        
    def export_scanner(self, profile: ScannerProfile) -> str:
        data = {
            "name": profile.name,
            "description": profile.description,
            "conditions": [
                {"field": c.field, "operator": c.operator.value, "value": c.value}
                for c in profile.conditions
            ]
        }
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode('utf-8')
        
    def import_scanner(self, payload: str) -> Optional[ScannerProfile]:
        try:
            json_str = base64.b64decode(payload).decode('utf-8')
            data = json.load(json_str)
            conditions = []
            for c in data.get("conditions", []):
                op = FilterOperator(c["operator"])
                conditions.append(FilterCondition(field=c["field"], operator=op, value=c["value"]))
            
            profile = ScannerProfile(name=data.get("name", "Imported"), description=data.get("description", ""), conditions=conditions)
            self.save_scanner(profile)
            return profile
        except Exception:
            return None
