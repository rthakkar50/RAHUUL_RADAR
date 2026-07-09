from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QGroupBox, QGridLayout, QMessageBox, QSystemTrayIcon, QTabWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from application.paper_trading_service import PaperTradingEngine
from application.data_manager import DataManager

class PortfolioPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.engine = PaperTradingEngine.get_instance()
        self.data_manager = DataManager.get_instance()
        
        self.setup_ui()
        self.connect_signals()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_live_prices)
        self.timer.start(5000)
        
        self.refresh_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("💼 LIVE PORTFOLIO & PAPER TRADING")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2196F3;")
        layout.addWidget(title)
        
        # --- TOP SECTION (Account & Risk) ---
        top_layout = QHBoxLayout()
        
        # --- PORTFOLIO SUMMARY ---
        self.group_summary = QGroupBox("Account Summary (₹)")
        self.group_summary.setStyleSheet("QGroupBox { border: 1px solid #2196F3; border-radius: 5px; margin-top: 10px; font-weight: bold; }")
        grid = QGridLayout()
        
        self.lbl_cap = QLabel("0.00")
        self.lbl_margin = QLabel("0.00")
        self.lbl_today_pnl = QLabel("0.00")
        self.lbl_open_pnl = QLabel("0.00")
        self.lbl_closed_pnl = QLabel("0.00")
        self.lbl_total_ret = QLabel("0.00")
        
        grid.addWidget(QLabel("Available Capital:"), 0, 0)
        grid.addWidget(self.lbl_cap, 0, 1)
        grid.addWidget(QLabel("Used Margin:"), 0, 2)
        grid.addWidget(self.lbl_margin, 0, 3)
        grid.addWidget(QLabel("Today's P&L:"), 0, 4)
        grid.addWidget(self.lbl_today_pnl, 0, 5)
        
        grid.addWidget(QLabel("Open P&L:"), 1, 0)
        grid.addWidget(self.lbl_open_pnl, 1, 1)
        grid.addWidget(QLabel("Closed P&L:"), 1, 2)
        grid.addWidget(self.lbl_closed_pnl, 1, 3)
        grid.addWidget(QLabel("Total Return:"), 1, 4)
        grid.addWidget(self.lbl_total_ret, 1, 5)
        
        self.group_summary.setLayout(grid)
        top_layout.addWidget(self.group_summary)
        
        # --- SPRINT-75 LIVE RISK MANAGER ---
        self.group_risk = QGroupBox("Live Risk Summary (Sprint 75)")
        self.group_risk.setStyleSheet("QGroupBox { border: 1px solid #FF9800; border-radius: 5px; margin-top: 10px; font-weight: bold; }")
        risk_grid = QGridLayout()
        
        self.lbl_risk_cap = QLabel("0.00")
        self.lbl_risk_used = QLabel("0.00")
        self.lbl_risk_remain = QLabel("0.00")
        self.lbl_risk_expo = QLabel("0.00")
        
        risk_grid.addWidget(QLabel("Max Daily Loss:"), 0, 0)
        risk_grid.addWidget(self.lbl_risk_cap, 0, 1)
        risk_grid.addWidget(QLabel("Current Open Risk:"), 0, 2)
        risk_grid.addWidget(self.lbl_risk_used, 0, 3)
        
        risk_grid.addWidget(QLabel("Remaining Risk:"), 1, 0)
        risk_grid.addWidget(self.lbl_risk_remain, 1, 1)
        risk_grid.addWidget(QLabel("Open Exposure:"), 1, 2)
        risk_grid.addWidget(self.lbl_risk_expo, 1, 3)
        
        self.group_risk.setLayout(risk_grid)
        top_layout.addWidget(self.group_risk)
        
        layout.addLayout(top_layout)
        
        # --- TABS ---
        tabs = QTabWidget()
        
        # POSITIONS TAB
        tab_pos = QWidget()
        pos_layout = QVBoxLayout(tab_pos)
        self.table_pos = QTableWidget()
        cols = ["Symbol", "Dir", "Qty", "Entry", "CMP", "Target", "SL", "P/L", "Charges", "Net P/L", "Status"]
        self.table_pos.setColumnCount(len(cols))
        self.table_pos.setHorizontalHeaderLabels(cols)
        self.table_pos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_pos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_pos.setStyleSheet("QTableWidget { background-color: #1E2028; color: #FFF; border: none; }")
        pos_layout.addWidget(self.table_pos)
        
        # EXIT ALL BTN
        btn_exit = QPushButton("Close All Positions")
        btn_exit.setStyleSheet("background-color: #F44336; color: white; padding: 5px;")
        btn_exit.clicked.connect(self.close_all_positions)
        pos_layout.addWidget(btn_exit)
        
        tabs.addTab(tab_pos, "Open Positions")
        
        # STATS TAB
        tab_stats = QWidget()
        stats_layout = QVBoxLayout(tab_stats)
        self.lbl_stats = QLabel("Loading statistics...")
        self.lbl_stats.setStyleSheet("font-size: 14px; line-height: 1.5;")
        stats_layout.addWidget(self.lbl_stats)
        tabs.addTab(tab_stats, "Performance Statistics")
        
        layout.addWidget(tabs)

    def connect_signals(self):
        self.engine.signals.portfolio_updated.connect(self.on_portfolio_update)
        self.engine.signals.position_updated.connect(self.refresh_ui)
        self.engine.signals.order_executed.connect(self.refresh_ui)

    def update_live_prices(self):
        for pid, p in self.engine.active_positions.items():
            sym = p['symbol']
            df = self.data_manager.get_stock_data(sym)
            if df is not None and not df.empty:
                cmp = df.iloc[-1]['Close']
                self.engine.update_market_price(sym, cmp)

    def on_portfolio_update(self, data):
        def format_lbl(lbl, val, colorize=False):
            lbl.setText(f"₹ {val:,.2f}")
            if colorize:
                if val > 0: lbl.setStyleSheet("color: #4CAF50;")
                elif val < 0: lbl.setStyleSheet("color: #F44336;")
                else: lbl.setStyleSheet("color: #FFF;")
                
        format_lbl(self.lbl_cap, data['capital'])
        format_lbl(self.lbl_margin, data['margin'])
        format_lbl(self.lbl_today_pnl, data['today_pnl'], True)
        format_lbl(self.lbl_open_pnl, data['open_pnl'], True)
        format_lbl(self.lbl_closed_pnl, data['closed_pnl'], True)
        format_lbl(self.lbl_total_ret, data['total_return'], True)

    def refresh_ui(self):
        # Update Table
        positions = list(self.engine.active_positions.values())
        self.table_pos.setRowCount(len(positions))
        
        for i, p in enumerate(positions):
            def c(val, color=None):
                s = str(val) if not isinstance(val, float) else f"{val:.2f}"
                it = QTableWidgetItem(s)
                it.setTextAlignment(Qt.AlignCenter)
                if color: it.setForeground(QColor(color))
                return it
                
            dir_col = "#4CAF50" if p['direction']=="BUY" else "#F44336"
            pnl_col = "#4CAF50" if p['net_pnl'] > 0 else "#F44336"
            
            self.table_pos.setItem(i, 0, c(p['symbol']))
            self.table_pos.setItem(i, 1, c(p['direction'], dir_col))
            self.table_pos.setItem(i, 2, c(p['qty']))
            self.table_pos.setItem(i, 3, c(p['entry_price']))
            self.table_pos.setItem(i, 4, c(p.get('cmp', 0.0)))
            self.table_pos.setItem(i, 5, c(p['target'], "#4CAF50"))
            self.table_pos.setItem(i, 6, c(p['sl'], "#F44336"))
            self.table_pos.setItem(i, 7, c(p.get('pnl', 0.0), pnl_col))
            self.table_pos.setItem(i, 8, c(p.get('charges', 0.0), "#FF9800"))
            self.table_pos.setItem(i, 9, c(p.get('net_pnl', 0.0), pnl_col))
            self.table_pos.setItem(i, 10, c(p['status'], "#2196F3"))
            
        # Update Stats
        stats = self.engine.get_statistics()
        if stats:
            text = f"""
            <b>Win Rate:</b> {stats.get('win_rate', 0)}%<br>
            <b>Loss Rate:</b> {stats.get('loss_rate', 0)}%<br>
            <b>Average Win:</b> ₹{stats.get('avg_win', 0)}<br>
            <b>Average Loss:</b> ₹{stats.get('avg_loss', 0)}<br>
            <b>Profit Factor:</b> {stats.get('profit_factor', 0)}<br>
            <b>Maximum Drawdown:</b> {stats.get('max_drawdown', 0)}%
            """
            self.lbl_stats.setText(text)
            
        # Update Sprint 75 Risk Panel
        try:
            from core.risk_manager import RiskManager
            rm = RiskManager.get_instance()
            risk_summary = rm.get_live_risk_summary()
            
            self.lbl_risk_cap.setText(f"₹ {risk_summary.get('max_daily_loss', 0):,.0f}")
            self.lbl_risk_used.setText(f"₹ {risk_summary.get('open_risk', 0):,.0f}")
            
            rem = risk_summary.get('remaining_risk', 0)
            self.lbl_risk_remain.setText(f"₹ {rem:,.0f}")
            if rem < 0:
                self.lbl_risk_remain.setStyleSheet("color: #F44336;")
            else:
                self.lbl_risk_remain.setStyleSheet("color: #4CAF50;")
                
            self.lbl_risk_expo.setText(f"₹ {risk_summary.get('open_exposure', 0):,.0f}")
        except Exception:
            pass

    def close_all_positions(self):
        for pid, p in list(self.engine.active_positions.items()):
            self.engine.close_position(pid, p['cmp'], "Manual Exit")
        QMessageBox.information(self, "Success", "All open positions have been closed.")
