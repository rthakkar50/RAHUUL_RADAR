from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGridLayout
from PySide6.QtGui import QFont

class PortfolioSummary(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        
        self.metrics = {}
        labels = [
            ("Total Capital", 0, 0),
            ("Invested Amount", 0, 1),
            ("Available Cash", 0, 2),
            ("Current Portfolio Value", 0, 3),
            ("Today's P&L", 1, 0),
            ("Overall P&L", 1, 1),
            ("Overall Return %", 1, 2)
        ]
        
        for lbl_text, r, c in labels:
            vbox = QVBoxLayout()
            title = QLabel(lbl_text)
            title.setStyleSheet("color: #A0AAB5; font-size: 12px;")
            val = QLabel("No Data")
            val.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
            vbox.addWidget(title)
            vbox.addWidget(val)
            self.layout.addLayout(vbox, r, c)
            self.metrics[lbl_text] = val
            
    def update_summary(self, data: dict):
        if not data:
            for lbl, val_widget in self.metrics.items():
                val_widget.setText("No Data")
                val_widget.setStyleSheet("color: #A0AAB5; font-size: 16px; font-weight: bold;")
            return
            
        total_cap = data.get('total_capital', data.get('capital'))
        invested = data.get('invested_capital', data.get('margin'))
        avail_cash = data.get('available_cash')
        if avail_cash is None and total_cap is not None and invested is not None:
            avail_cash = total_cap - invested

        today_pnl = data.get('today_pnl')
        overall_pnl = data.get('overall_pnl')
        if overall_pnl is None and 'open_pnl' in data and 'closed_pnl' in data:
            overall_pnl = data.get('open_pnl', 0.0) + data.get('closed_pnl', 0.0)
            
        curr_val = total_cap + overall_pnl if total_cap is not None and overall_pnl is not None else None
        overall_ret = (overall_pnl / total_cap) * 100.0 if total_cap and total_cap > 0 and overall_pnl is not None else None

        self.metrics["Total Capital"].setText(f"₹ {total_cap:,.2f}" if total_cap is not None else "No Data")
        self.metrics["Invested Amount"].setText(f"₹ {invested:,.2f}" if invested is not None else "No Data")
        self.metrics["Available Cash"].setText(f"₹ {avail_cash:,.2f}" if avail_cash is not None else "No Data")
        
        if curr_val is not None:
            self.metrics["Current Portfolio Value"].setText(f"₹ {curr_val:,.2f}")
            self.metrics["Current Portfolio Value"].setStyleSheet(f"color: {'#4CAF50' if curr_val >= (total_cap or 0) else '#F44336'}; font-size: 16px; font-weight: bold;")
        else:
            self.metrics["Current Portfolio Value"].setText("No Data")
            self.metrics["Current Portfolio Value"].setStyleSheet("color: #A0AAB5; font-size: 16px; font-weight: bold;")
        
        if today_pnl is not None:
            self.metrics["Today's P&L"].setText(f"₹ {today_pnl:,.2f}")
            self.metrics["Today's P&L"].setStyleSheet(f"color: {'#4CAF50' if today_pnl > 0 else ('#F44336' if today_pnl < 0 else '#FFF')}; font-size: 16px; font-weight: bold;")
        else:
            self.metrics["Today's P&L"].setText("No Data")
            self.metrics["Today's P&L"].setStyleSheet("color: #A0AAB5; font-size: 16px; font-weight: bold;")
            
        if overall_pnl is not None:
            self.metrics["Overall P&L"].setText(f"₹ {overall_pnl:,.2f}")
            self.metrics["Overall P&L"].setStyleSheet(f"color: {'#4CAF50' if overall_pnl > 0 else ('#F44336' if overall_pnl < 0 else '#FFF')}; font-size: 16px; font-weight: bold;")
        else:
            self.metrics["Overall P&L"].setText("No Data")
            self.metrics["Overall P&L"].setStyleSheet("color: #A0AAB5; font-size: 16px; font-weight: bold;")

        if overall_ret is not None:
            self.metrics["Overall Return %"].setText(f"{overall_ret:+.2f}%")
            self.metrics["Overall Return %"].setStyleSheet(f"color: {'#4CAF50' if overall_ret > 0 else ('#F44336' if overall_ret < 0 else '#FFF')}; font-size: 16px; font-weight: bold;")
        else:
            self.metrics["Overall Return %"].setText("No Data")
            self.metrics["Overall Return %"].setStyleSheet("color: #A0AAB5; font-size: 16px; font-weight: bold;")
