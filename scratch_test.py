import sys
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from application.swing_scanner_service import SwingScannerService

svc = SwingScannerService()
try:
    svc.execute_swing_scan()
except Exception as e:
    import traceback
    traceback.print_exc()
