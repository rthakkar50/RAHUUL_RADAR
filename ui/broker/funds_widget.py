from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class FundsWidget(QWidget):
    def __init__(self, broker_manager, parent=None):
        super().__init__(parent)
        self.broker_manager = broker_manager
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        
        self.lbl_available = QLabel("Available Margin: ₹0.00")
        self.lbl_used = QLabel("Used Margin: ₹0.00")
        self.lbl_cash = QLabel("Cash: ₹0.00")
        self.lbl_collateral = QLabel("Collateral: ₹0.00")
        
        for lbl in [self.lbl_available, self.lbl_used, self.lbl_cash, self.lbl_collateral]:
            lbl.setStyleSheet("font-size: 14px; padding: 5px;")
            layout.addWidget(lbl)
            
    def refresh_funds(self):
        broker = self.broker_manager.get_broker()
        if not broker:
            self._reset_labels()
            return
            
        funds = broker.get_funds()
        self.lbl_available.setText(f"Available Margin: ₹{funds.available_margin:,.2f}")
        self.lbl_used.setText(f"Used Margin: ₹{funds.used_margin:,.2f}")
        self.lbl_cash.setText(f"Cash: ₹{funds.available_cash:,.2f}")
        self.lbl_collateral.setText(f"Collateral: ₹{funds.collateral:,.2f}")
        
    def _reset_labels(self):
        self.lbl_available.setText("Available Margin: ₹0.00")
        self.lbl_used.setText("Used Margin: ₹0.00")
        self.lbl_cash.setText("Cash: ₹0.00")
        self.lbl_collateral.setText("Collateral: ₹0.00")
