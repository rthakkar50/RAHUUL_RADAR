import logging
logging.basicConfig(level=logging.WARNING)

from application.swing_scanner_service import SwingScannerService

# Patch get_all_symbols to ONLY return these stocks
import application.swing_scanner_service as sss
sss.get_all_symbols = lambda: [
    {"symbol": "PEL.NS", "sector": "FINANCIAL SERVICES", "company_name": "Piramal"},
    {"symbol": "GMRINFRA.NS", "sector": "INFRASTRUCTURE", "company_name": "GMR"},
    {"symbol": "LTIM.NS", "sector": "IT", "company_name": "LTIM"},
    {"symbol": "GUJGASLTD.NS", "sector": "ENERGY", "company_name": "GujGas"},
    {"symbol": "TATAMOTORS.NS", "sector": "AUTO", "company_name": "Tata Motors"}
]

service = SwingScannerService()
results = service.execute_swing_scan()
print(f"Scan complete. {len(results)} results found.")
