import os
import ast
from typing import Dict, Any, List

class ProjectAudit:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.issues = []
        
    def run_audit(self) -> Dict[str, Any]:
        stats = {"total_files": 0, "total_lines": 0}
        
        for root, _, files in os.walk(self.root_dir):
            if "venv" in root or ".git" in root or "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    stats["total_files"] += 1
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            stats["total_lines"] += len(content.splitlines())
                            self._analyze_ast(content, path)
                    except Exception as e:
                        self.issues.append({"level": "ERROR", "file": path, "msg": f"Parse error: {e}"})
                        
        return {
            "stats": stats,
            "issues": self.issues
        }
        
    def _analyze_ast(self, content: str, path: str):
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        self.issues.append({"level": "WARNING", "file": path, "msg": "Bare except block found (silent failure risk)"})
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "print":
                        self.issues.append({"level": "WARNING", "file": path, "msg": "print() found (use proper logging)"})
        except:
            pass
