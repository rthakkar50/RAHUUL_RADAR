from ui.intraday_scanner import IntradayScanThread
from PySide6.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)
thread = IntradayScanThread("5m")
thread.run()
