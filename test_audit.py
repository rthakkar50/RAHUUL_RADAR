import time
import json
import sys
from datetime import datetime
from collections.abc import Iterable, Mapping

from application.swing_scanner_service import SwingScannerService

def analyze_types(obj, path="root", type_report=None):
    if type_report is None:
        type_report = {}
        
    obj_type = type(obj)
    
    # Check if type is built-in
    if obj is None or isinstance(obj, (str, int, float, bool)):
        pass # Built-in primitives
    elif isinstance(obj, Mapping):
        for k, v in obj.items():
            analyze_types(v, f"{path}.{k}", type_report)
    elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
        for i, item in enumerate(obj):
            analyze_types(item, f"{path}[{i}]", type_report)
    else:
        # Non-standard or custom type
        type_name = obj_type.__name__
        if type_name not in type_report:
            type_report[type_name] = []
        type_report[type_name].append(path)
        
    return type_report


def run_audit():
    service = SwingScannerService()
    
    start = time.time()
    results = service.execute_swing_scan()
    exec_time = time.time() - start
    
    # Type Analysis
    type_report = analyze_types(results)
    
    # Get Sample (first qualified trade)
    sample_trade = results.get("qualified_results", [])[0] if results.get("qualified_results") else None
    
    # Check serialization
    try:
        # FastAPI's recommended approach (using standard json but we need to see what fails)
        import json
        raw_json = json.dumps(sample_trade)
        serialization_risk = "None, completely JSON serializable natively."
    except TypeError as e:
        serialization_risk = f"Failed native JSON serialization: {e}"
        # Fallback to default=str to see output
        raw_json = json.dumps(sample_trade, default=str)
        
    # Full response size
    full_json = json.dumps(results, default=str)
    size_kb = len(full_json.encode('utf-8')) / 1024
    
    output = {
        "exec_time_seconds": exec_time,
        "type_report": type_report,
        "sample_trade": sample_trade,
        "serialization_risk": serialization_risk,
        "size_kb": size_kb
    }
    
    with open("audit_results.json", "w") as f:
        json.dump(output, f, default=str, indent=4)
        
if __name__ == "__main__":
    run_audit()
