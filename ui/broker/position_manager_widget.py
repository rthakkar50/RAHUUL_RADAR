from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
from PySide6.QtCore import Qt

class PositionManagerWidget(QWidget):
    def __init__(self, broker_manager, parent=None):
        super().__init__(parent)
        self.broker_manager = broker_manager
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Broker: Disconnected | Total MTM: 0.0")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Symbol", "Qty", "Avg Price", "LTP", "Realized P&L", "Unrealized P&L", "Total P&L"
        ])
        layout.addWidget(self.table)
        
    def refresh_positions(self):
        broker = self.broker_manager.get_broker()
        if not broker:
            self.status_label.setText("Broker: Disconnected | Total MTM: 0.0")
            self.table.setRowCount(0)
            return
            
        positions = broker.get_positions()
        self.table.setRowCount(len(positions))
        
        total_mtm = 0.0
        for i, pos in enumerate(positions):
            self.table.setItem(i, 0, QTableWidgetItem(pos.symbol))
            self.table.setItem(i, 1, QTableWidgetItem(str(pos.qty)))
            self.table.setItem(i, 2, QTableWidgetItem(f"{pos.avg_price:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{pos.ltp:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{pos.realized_pnl:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{pos.unrealized_pnl:.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{pos.total_pnl:.2f}"))
            total_mtm += pos.total_pnl
            
        profile = broker.get_profile()
        broker_name = profile.get("broker", "Connected")
        self.status_label.setText(f"Broker: {broker_name} | Total MTM: {total_mtm:.2f}")
