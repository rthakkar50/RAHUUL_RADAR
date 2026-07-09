from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtGui import QFont

class PortfolioSummary(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.metrics = {}
        labels = ["Total Capital", "Available Cash", "Invested", "Today P&L", "Overall P&L", "Open", "Win Rate"]
        
        for lbl in labels:
            vbox = QVBoxLayout()
            title = QLabel(lbl)
            title.setStyleSheet("color: #A0AAB5; font-size: 12px;")
            val = QLabel("0.00")
            val.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
            vbox.addWidget(title)
            vbox.addWidget(val)
            self.layout.addLayout(vbox)
            self.metrics[lbl] = val
            
    def update_summary(self, data: dict):
        self.metrics["Total Capital"].setText(f"${data.get('total_capital', 0):,.2f}")
        self.metrics["Available Cash"].setText(f"${data.get('available_cash', 0):,.2f}")
        self.metrics["Invested"].setText(f"${data.get('invested_capital', 0):,.2f}")
        
        today_pnl = data.get('today_pnl', 0)
        self.metrics["Today P&L"].setText(f"${today_pnl:,.2f}")
        self.metrics["Today P&L"].setStyleSheet(f"color: {'#4CAF50' if today_pnl >= 0 else '#F44336'}; font-size: 16px; font-weight: bold;")
        
        overall_pnl = data.get('overall_pnl', 0)
        self.metrics["Overall P&L"].setText(f"${overall_pnl:,.2f}")
        self.metrics["Overall P&L"].setStyleSheet(f"color: {'#4CAF50' if overall_pnl >= 0 else '#F44336'}; font-size: 16px; font-weight: bold;")
        
        self.metrics["Open"].setText(str(data.get('open_positions', 0)))
        self.metrics["Win Rate"].setText(f"{data.get('win_rate', 0)}%")
