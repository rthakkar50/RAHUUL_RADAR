import os
import sys
import time

# Ensure we can import from the root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.project_audit import ProjectAudit
from reports.health_report_generator import HealthReportGenerator

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Starting Enterprise Health Analyzer on {root}...")
    
    start_t = time.time()
    audit = ProjectAudit(root)
    results = audit.run_audit()
    exec_t = time.time() - start_t
    
    issues_count = len(results["issues"])
    score = max(0, 100 - (issues_count * 2))
    
    final_payload = {
        "summary": {
            "execution_time_seconds": round(exec_t, 2),
            "total_python_files": results["stats"]["total_files"],
            "total_lines_of_code": results["stats"]["total_lines"],
            "total_issues_found": issues_count
        },
        "scores": {
            "architecture_score": score,
            "performance_score": score,
            "maintainability_score": score,
            "readiness_score": score
        },
        "issues": results["issues"]
    }
    
    print(f"Audit Complete! Readiness Score: {score}/100")
    
    generator = HealthReportGenerator(os.path.join(root, "reports"))
    j_path = generator.generate_json(final_payload)
    h_path = generator.generate_html(final_payload)
    
    print(f"Generated JSON: {j_path}")
    print(f"Generated HTML: {h_path}")

if __name__ == "__main__":
    main()
