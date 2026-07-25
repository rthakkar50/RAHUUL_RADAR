from application.swing_scanner_service import SwingScannerService
from core.config_manager import ConfigManager

cm = ConfigManager()
cm.settings['market_provider'] = 'paytm'
cm.save_config(cm.settings)

svc = SwingScannerService()
print("Starting scanner...")
res = svc.execute_swing_scan()
print("Total Scanned:", res["total_scanned"])
print("Total Universe:", res["total_universe"])
print("Errors:", res["error_count"])
