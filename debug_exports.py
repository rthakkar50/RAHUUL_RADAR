import os
import json
import csv
import pandas as pd
from application.swing_scanner_service import SwingScannerService
from utils.logger import get_logger

logger = get_logger("ExportTest")

def test_exports():
    service = SwingScannerService()
    # Mocking a small scan result
    sample_data = [
        {
            "Symbol": "RELIANCE.NS",
            "Company": "Reliance Industries",
            "Sector": "ENERGY",
            "Price": 3000.0,
            "Signal": "BUY",
            "Score": 85.0,
            "Raw Score": 85.0,
            "Confidence": 90.0,
            "Trend": "Bullish",
            "Volume": "100000",
            "Risk Reward": "1:2.5",
            "Entry": 3000.0,
            "Stop Loss": 2900.0,
            "Target 1": 3250.0,
            "Target 2": 3500.0,
            "Timestamp": "2026-07-09 21:00:00",
            "_raw_data": {"hidden": True}
        }
    ]
    
    os.makedirs("exports", exist_ok=True)
    
    # 1. CSV
    csv_path = "exports/test.csv"
    res_csv = service.export_csv(sample_data, csv_path)
    if res_csv and os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if len(rows) == 1 and rows[0]["Symbol"] == "RELIANCE.NS" and "_raw_data" not in rows[0]:
                print("CSV Export: PASS")
            else:
                print("CSV Export: FAIL - Data mismatch or hidden keys present")
    else:
        print("CSV Export: FAIL - File not created")
        
    # 2. JSON
    json_path = "exports/test.json"
    res_json = service.export_json(sample_data, json_path)
    if res_json and os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
            if len(data) == 1 and data[0]["Symbol"] == "RELIANCE.NS" and "_raw_data" not in data[0]:
                print("JSON Export: PASS")
            else:
                print("JSON Export: FAIL - Data mismatch or hidden keys present")
    else:
        print("JSON Export: FAIL - File not created")
        
    # 3. Excel
    excel_path = "exports/test.xlsx"
    res_excel = service.export_excel(sample_data, excel_path)
    if res_excel and os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        if len(df) == 1 and df.iloc[0]["Symbol"] == "RELIANCE.NS" and "_raw_data" not in df.columns:
            print("Excel Export: PASS")
        else:
            print("Excel Export: FAIL - Data mismatch or hidden keys present")
    else:
        print("Excel Export: FAIL - File not created or pandas missing")

if __name__ == "__main__":
    test_exports()
