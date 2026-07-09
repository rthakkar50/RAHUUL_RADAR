from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtCore import Qt

class ScalpingResultsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1A1C20;
                gridline-color: #3D4047;
                color: #FFFFFF;
                selection-background-color: #2D3A56;
                selection-color: #FFFFFF;
                border: 1px solid #3D4047;
            }
            QHeaderView::section {
                background-color: #2D2F34;
                color: #A0AAB5;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #3D4047;
            }
        """)

    def populate(self, results):
        self.setSortingEnabled(False)
        self.setRowCount(len(results))
        
        headers = [
            "Symbol", "Company", "Sector", "Price", "Signal", "Score", 
            "Confidence", "Trend", "Volume", "Risk Reward", "Entry", 
            "Stop Loss", "Target 1", "Target 2", "Target 3", "Timestamp"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        for row, r in enumerate(results):
            self.setItem(row, 0, QTableWidgetItem(str(r.get("Symbol", ""))))
            
            comp = QTableWidgetItem(str(r.get("Company", "")))
            comp.setToolTip(str(r.get("Company", "")))
            self.setItem(row, 1, comp)
            
            self.setItem(row, 2, QTableWidgetItem(str(r.get("Sector", ""))))
            
            try: price_val = float(r.get("Price", 0))
            except: price_val = 0.0
            item_price = QTableWidgetItem()
            item_price.setData(Qt.EditRole, price_val)
            item_price.setText(f"{price_val:.2f}")
            self.setItem(row, 3, item_price)
            
            sig = str(r.get("Signal", "WAIT"))
            item_sig = QTableWidgetItem(sig)
            if "BUY" in sig: item_sig.setForeground(QBrush(QColor("#4CAF50")))
            elif "SELL" in sig: item_sig.setForeground(QBrush(QColor("#F44336")))
            else: item_sig.setForeground(QBrush(QColor("#FF9800")))
            self.setItem(row, 4, item_sig)
            
            try: score_val = float(r.get("Score", 0))
            except: score_val = 0.0
            item_score = QTableWidgetItem()
            item_score.setData(Qt.EditRole, score_val)
            self.setItem(row, 5, item_score)
            
            try: conf_val = float(r.get("Confidence", 0))
            except: conf_val = 0.0
            item_conf = QTableWidgetItem()
            item_conf.setData(Qt.EditRole, conf_val)
            item_conf.setText(f"{conf_val}%")
            if conf_val >= 90: item_conf.setForeground(QBrush(QColor("#2E7D32")))
            elif conf_val >= 75: item_conf.setForeground(QBrush(QColor("#81C784")))
            elif conf_val >= 50: item_conf.setForeground(QBrush(QColor("#FF9800")))
            else: item_conf.setForeground(QBrush(QColor("#F44336")))
            self.setItem(row, 6, item_conf)
            
            trend = str(r.get("Trend", ""))
            item_trend = QTableWidgetItem(trend)
            item_trend.setToolTip(trend)
            self.setItem(row, 7, item_trend)
            
            try: vol_val = int(float(r.get("Volume", 0)))
            except: vol_val = 0
            item_vol = QTableWidgetItem()
            item_vol.setData(Qt.EditRole, vol_val)
            item_vol.setText(f"{vol_val:,}")
            self.setItem(row, 8, item_vol)
            
            self.setItem(row, 9, QTableWidgetItem(str(r.get("Risk Reward", ""))))
            self.setItem(row, 10, QTableWidgetItem(str(r.get("Entry", ""))))
            self.setItem(row, 11, QTableWidgetItem(str(r.get("Stop Loss", ""))))
            self.setItem(row, 12, QTableWidgetItem(str(r.get("Target 1", ""))))
            self.setItem(row, 13, QTableWidgetItem(str(r.get("Target 2", ""))))
            self.setItem(row, 14, QTableWidgetItem(str(r.get("Target 3", ""))))
            
            ts = str(r.get("Timestamp", ""))
            item_ts = QTableWidgetItem(ts)
            item_ts.setToolTip(ts)
            self.setItem(row, 15, item_ts)
            
        self.resizeColumnsToContents()
        self.setSortingEnabled(True)
