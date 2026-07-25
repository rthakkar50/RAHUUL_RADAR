from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import BG_COLOR, CARD_BG, TEXT_PRIMARY, COLOR_BUY, COLOR_SELL
from application.paper_trading_service import PaperTradingEngine
from ui.widgets.equity_curve_chart import EquityCurveChart
from application.paper_market_updater import PaperMarketUpdater

class KPICard(QFrame):
    def __init__(self, title, initial_value, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; opacity: 0.7;")
        
        self.val_label = QLabel(initial_value)
        self.val_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.val_label)
        
    def set_value(self, value, color=TEXT_PRIMARY):
        self.val_label.setText(value)
        self.val_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")

class PaperTradingDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_PRIMARY};")
        self.service = PaperTradingEngine.get_instance()
        self.market_updater = PaperMarketUpdater()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("Professional Trading Dashboard")
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # 1. Top KPI Cards
        kpi_layout = QHBoxLayout()
        self.kpi_equity = KPICard("Total Equity", "₹0.00")
        self.kpi_mtm = KPICard("Live MTM", "₹0.00")
        self.kpi_win_rate = KPICard("Win Rate", "0.00%")
        self.kpi_profit_factor = KPICard("Profit Factor", "0.00")
        self.kpi_max_dd = KPICard("Max Drawdown", "0.00%")
        
        for kpi in [self.kpi_equity, self.kpi_mtm, self.kpi_win_rate, self.kpi_profit_factor, self.kpi_max_dd]:
            kpi_layout.addWidget(kpi)
            
        main_layout.addLayout(kpi_layout)
        
        # 2. Middle Section (Equity Curve)
        self.equity_chart = EquityCurveChart()
        self.equity_chart.setMinimumHeight(300)
        main_layout.addWidget(self.equity_chart)
        
        # 3. Bottom Section (Position Tabs)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {CARD_BG}; border-radius: 4px; }}
            QTabBar::tab {{ background: {CARD_BG}; color: {TEXT_PRIMARY}; padding: 8px 16px; margin-right: 2px; }}
            QTabBar::tab:selected {{ background: {COLOR_BUY}; font-weight: bold; }}
        """)
        
        # Open Positions Table
        self.open_table = QTableWidget(0, 7)
        self.open_table.setHorizontalHeaderLabels(["Symbol", "Direction", "Qty", "Entry", "CMP", "Targets", "Live P&L"])
        self.open_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.open_table.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_PRIMARY}; border: none;")
        self.tabs.addTab(self.open_table, "Open Positions")
        
        # Closed Positions Table
        self.closed_table = QTableWidget(0, 6)
        self.closed_table.setHorizontalHeaderLabels(["Symbol", "Direction", "Qty", "Entry", "Exit", "Net P&L"])
        self.closed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.closed_table.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_PRIMARY}; border: none;")
        self.tabs.addTab(self.closed_table, "Closed Positions")
        
        main_layout.addWidget(self.tabs)
        
        self._init_data()
        self._connect_signals()
        self.market_updater.start()
        
    def closeEvent(self, event):
        self.market_updater.stop()
        super().closeEvent(event)
        
    def _connect_signals(self):
        self.service.signals.portfolio_updated.connect(self._on_portfolio_update)
        self.service.signals.position_updated.connect(self._on_position_update)
        self.service.signals.order_executed.connect(self._on_order_executed)
        
    def _init_data(self):
        self._on_portfolio_update()
        self.refresh_closed_table()
        self.refresh_open_table()
        
        # Draw initial equity curve
        df = self.service.get_portfolio_history()
        self.equity_chart.update_data(df)
        
    def _on_portfolio_update(self):
        state = self.service.engine.get_portfolio_state()
        
        self.kpi_equity.set_value(f"₹{state.virtual_capital:,.2f}")
        
        mtm_color = COLOR_BUY if state.unrealized_pnl >= 0 else COLOR_SELL
        self.kpi_mtm.set_value(f"₹{state.unrealized_pnl:,.2f}", mtm_color)
        
        # Stats
        stats = self.service.get_statistics()
        if stats:
            self.kpi_win_rate.set_value(f"{stats.get('win_rate', 0)}%")
            self.kpi_profit_factor.set_value(f"{stats.get('profit_factor', 0)}")
            self.kpi_max_dd.set_value(f"{stats.get('max_drawdown', 0)}%")
            
    def _on_position_update(self, pos_dict):
        # We can optimize this by updating the specific row, but for simplicity we reload
        self.refresh_open_table()
        
    def _on_order_executed(self, pos_dict):
        self.refresh_closed_table()
        self.refresh_open_table()
        
        # Refresh chart
        df = self.service.get_portfolio_history()
        self.equity_chart.update_data(df)

    def refresh_open_table(self):
        self.open_table.setRowCount(0)
        positions = self.service.engine.open_positions.values()
        
        for p in positions:
            row = self.open_table.rowCount()
            self.open_table.insertRow(row)
            
            self.open_table.setItem(row, 0, QTableWidgetItem(p.symbol))
            
            dir_item = QTableWidgetItem(p.direction)
            dir_item.setForeground(Qt.green if p.direction == 'BUY' else Qt.red)
            self.open_table.setItem(row, 1, dir_item)
            
            self.open_table.setItem(row, 2, QTableWidgetItem(str(p.qty)))
            entry_price = float(p.entry_price) if p.entry_price is not None else 0.0
            curr_price = float(p.current_price) if p.current_price is not None else 0.0
            pnl = float(p.unrealized_pnl) if p.unrealized_pnl is not None else 0.0
            
            self.open_table.setItem(row, 3, QTableWidgetItem(f"{entry_price:.2f}"))
            self.open_table.setItem(row, 4, QTableWidgetItem(f"{curr_price:.2f}"))
            self.open_table.setItem(row, 5, QTableWidgetItem(f"{p.target_1}/{p.target_2}/{p.target_3}"))
            
            pnl_item = QTableWidgetItem(f"{pnl:.2f}")
            pnl_item.setForeground(Qt.green if pnl >= 0 else Qt.red)
            self.open_table.setItem(row, 6, pnl_item)
            
    def refresh_closed_table(self):
        self.closed_table.setRowCount(0)
        positions = reversed(self.service.engine.closed_positions) # Newest first
        
        for p in positions:
            row = self.closed_table.rowCount()
            self.closed_table.insertRow(row)
            
            self.closed_table.setItem(row, 0, QTableWidgetItem(p.symbol))
            
            dir_item = QTableWidgetItem(p.direction)
            dir_item.setForeground(Qt.green if p.direction == 'BUY' else Qt.red)
            self.closed_table.setItem(row, 1, dir_item)
            
            self.closed_table.setItem(row, 2, QTableWidgetItem(str(p.qty)))
            entry_price = float(p.entry_price) if p.entry_price is not None else 0.0
            exit_price = float(p.exit_price) if p.exit_price is not None else 0.0
            pnl = float(p.realized_pnl) if p.realized_pnl is not None else 0.0
            
            self.closed_table.setItem(row, 3, QTableWidgetItem(f"{entry_price:.2f}"))
            self.closed_table.setItem(row, 4, QTableWidgetItem(f"{exit_price:.2f}"))
            
            pnl_item = QTableWidgetItem(f"{pnl:.2f}")
            pnl_item.setForeground(Qt.green if pnl >= 0 else Qt.red)
            self.closed_table.setItem(row, 5, pnl_item)
