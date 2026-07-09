from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import Qt

class PortfolioTable(QTableWidget):
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

    def populate(self, positions):
        self.setSortingEnabled(False)
        self.setRowCount(len(positions))
        
        headers = [
            "Symbol", "Company", "Quantity", "Avg Entry", "Current Price", 
            "Market Value", "Today's P&L", "Overall P&L", "Stop Loss", 
            "Target", "Status", "Last Updated"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        for row, p in enumerate(positions):
            self.setItem(row, 0, QTableWidgetItem(str(p.get("symbol", ""))))
            self.setItem(row, 1, QTableWidgetItem(str(p.get("company", ""))))
            
            qty = int(p.get("quantity", 0))
            item_qty = QTableWidgetItem()
            item_qty.setData(Qt.EditRole, qty)
            self.setItem(row, 2, item_qty)
            
            entry = float(p.get("avg_entry", 0.0))
            item_entry = QTableWidgetItem()
            item_entry.setData(Qt.EditRole, entry)
            item_entry.setText(f"{entry:.2f}")
            self.setItem(row, 3, item_entry)
            
            price = float(p.get("current_price", 0.0))
            item_price = QTableWidgetItem()
            item_price.setData(Qt.EditRole, price)
            item_price.setText(f"{price:.2f}")
            self.setItem(row, 4, item_price)
            
            mv = float(p.get("market_value", 0.0))
            item_mv = QTableWidgetItem()
            item_mv.setData(Qt.EditRole, mv)
            item_mv.setText(f"{mv:,.2f}")
            self.setItem(row, 5, item_mv)
            
            # Today P&L
            today_pnl = float(p.get("today_pnl", 0.0))
            item_today = QTableWidgetItem()
            item_today.setData(Qt.EditRole, today_pnl)
            item_today.setText(f"{today_pnl:,.2f}")
            item_today.setForeground(QBrush(QColor("#4CAF50" if today_pnl >= 0 else "#F44336")))
            self.setItem(row, 6, item_today)
            
            # Overall P&L
            overall_pnl = float(p.get("overall_pnl", 0.0))
            item_overall = QTableWidgetItem()
            item_overall.setData(Qt.EditRole, overall_pnl)
            item_overall.setText(f"{overall_pnl:,.2f}")
            item_overall.setForeground(QBrush(QColor("#4CAF50" if overall_pnl >= 0 else "#F44336")))
            self.setItem(row, 7, item_overall)
            
            self.setItem(row, 8, QTableWidgetItem(str(p.get("stop_loss", ""))))
            self.setItem(row, 9, QTableWidgetItem(str(p.get("target", ""))))
            
            status = str(p.get("status", "OPEN"))
            item_status = QTableWidgetItem(status)
            if status == "OPEN": item_status.setForeground(QBrush(QColor("#FF9800")))
            elif status == "CLOSED": item_status.setForeground(QBrush(QColor("#9E9E9E")))
            self.setItem(row, 10, item_status)
            
            self.setItem(row, 11, QTableWidgetItem(str(p.get("last_updated", ""))))
            
        self.resizeColumnsToContents()
        self.setSortingEnabled(True)
