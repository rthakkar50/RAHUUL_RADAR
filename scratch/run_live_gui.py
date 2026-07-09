import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.main_window import MainWindow

def run_debug():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    window = MainWindow()
    window.show()
    
    def click_scan():
        print("\nDEBUG: Automatically clicking Intraday Scan Button...", flush=True)
        window.tabs.setCurrentIndex(1)
        intraday_page = window.intraday_scanner
        
        # Override scan_finished locally to force the app to close immediately when done
        original_scan_finished = intraday_page.scan_finished
        def wrapped_scan_finished(top_buys, top_sells, top_watch, stats):
            original_scan_finished(top_buys, top_sells, top_watch, stats)
            print("\nDEBUG: Intraday scan fully completed. Closing app.", flush=True)
            window.close()
            app.quit()
            
        intraday_page.scan_finished = wrapped_scan_finished
        
        # Click the button
        intraday_page.btn_scan.click()
        print("DEBUG: Button clicked.", flush=True)
        
    # Wait 2 seconds for app to open, then click
    QTimer.singleShot(2000, click_scan)
    
    # Absolute failsafe timeout (10 minutes)
    QTimer.singleShot(600000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run_debug()
