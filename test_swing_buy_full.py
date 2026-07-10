import sys
import os
import time

from application.swing_scanner_service import SwingScannerService
import application.swing_scanner_service as svc

service = SwingScannerService()

# I will patch svc.safe_float
original_safe_float = svc.safe_float

def patched_safe_float(val, fallback=0.0):
    if str(val) == '91.3' or val == 91.3:
        pass
    return original_safe_float(val, fallback)

# Wait, better, I will run the real scanner but read the file and insert a print!
