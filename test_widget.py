import sys
from PySide6.QtWidgets import QApplication
from ui.pages.paper_trading_dashboard import PaperTradingDashboard
import pyqtgraph as pg

app = QApplication(sys.argv)
widget = PaperTradingDashboard()
print("Dashboard instantiated successfully")
