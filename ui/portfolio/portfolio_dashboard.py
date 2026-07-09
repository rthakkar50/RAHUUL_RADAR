from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt

class PortfolioDashboard(QWidget):
    def __init__(self, portfolio_manager, parent=None):
        super().__init__(parent)
        self.portfolio_manager = portfolio_manager
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Top Banner
        banner_layout = QHBoxLayout()
        self.lbl_capital = QLabel("Total Capital: 0.00")
        self.lbl_invested = QLabel("Invested: 0.00")
        self.lbl_cash = QLabel("Cash: 0.00")
        self.lbl_mtm = QLabel("MTM: 0.00")
        
        for lbl in [self.lbl_capital, self.lbl_invested, self.lbl_cash, self.lbl_mtm]:
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #222; color: #fff;")
            banner_layout.addWidget(lbl)
        
        layout.addLayout(banner_layout)
        
        # Sector Allocation
        self.lbl_sectors = QLabel("Sector Allocation: None")
        self.lbl_sectors.setStyleSheet("font-size: 14px; padding: 5px;")
        layout.addWidget(self.lbl_sectors)
        
        # Holdings Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Symbol", "Qty", "Avg Price", "LTP", "P&L"])
        layout.addWidget(self.table)
        
    def refresh(self):
        stats = self.portfolio_manager.get_portfolio_stats()
        self.lbl_capital.setText(f"Total Capital: {stats.total_capital:,.2f}")
        self.lbl_invested.setText(f"Invested: {stats.invested_capital:,.2f}")
        self.lbl_cash.setText(f"Cash: {stats.available_cash:,.2f}")
        self.lbl_mtm.setText(f"MTM: {stats.total_mtm:,.2f}")
        
        if stats.total_mtm >= 0:
            self.lbl_mtm.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #222; color: #00ff00;")
        else:
            self.lbl_mtm.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #222; color: #ff0000;")
            
        alloc = self.portfolio_manager.get_sector_allocation()
        sector_str = " | ".join([f"{k}: {v}%" for k, v in alloc.allocation_pct.items()])
        if not sector_str:
            sector_str = "None"
        self.lbl_sectors.setText(f"Sector Allocation: {sector_str}")
        
        broker = self.portfolio_manager.broker_manager.get_broker()
        if broker:
            positions = broker.get_positions()
            self.table.setRowCount(len(positions))
            for i, p in enumerate(positions):
                self.table.setItem(i, 0, QTableWidgetItem(p.symbol))
                self.table.setItem(i, 1, QTableWidgetItem(str(p.qty)))
                self.table.setItem(i, 2, QTableWidgetItem(f"{p.avg_price:.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{p.ltp:.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{p.total_pnl:.2f}"))
        else:
            self.table.setRowCount(0)
