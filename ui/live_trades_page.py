from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QGroupBox, QGridLayout, QMessageBox, QFileDialog, QSystemTrayIcon, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
import pandas as pd
import sqlite3

from application.paper_trading_service import PaperTradingEngine
from application.data_manager import DataManager
from strategy.ltme_engine import LiveTradeMonitoringEngine

class LiveTradesPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.trade_manager = PaperTradingEngine.get_instance()
        self.data_manager = DataManager.get_instance()
        self.ltme = LiveTradeMonitoringEngine()
        
        self.setup_ui()
        self.connect_signals()
        
        # 5 sec auto refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_prices)
        self.timer.start(5000)
        
        self.refresh_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("⚡ LIVE TRADES & POSITIONS")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title)
        
        # Refresh Configurator
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("LTME Refresh Rate:"))
        self.combo_refresh = QComboBox()
        self.combo_refresh.addItems(["5 Seconds", "30 Seconds", "1 Minute", "2 Minutes", "5 Minutes"])
        self.combo_refresh.currentTextChanged.connect(self.change_refresh_rate)
        refresh_layout.addWidget(self.combo_refresh)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        # Stats Panel
        self.group_stats = QGroupBox("Performance Statistics")
        self.group_stats.setStyleSheet("QGroupBox { border: 1px solid #4CAF50; border-radius: 5px; margin-top: 10px; font-weight: bold; }")
        grid = QGridLayout()
        self.lbl_today = QLabel("0")
        self.lbl_open = QLabel("0")
        self.lbl_closed = QLabel("0")
        self.lbl_winrate = QLabel("0%")
        self.lbl_pnl = QLabel("0.00")
        
        grid.addWidget(QLabel("Today's Trades:"), 0, 0)
        grid.addWidget(self.lbl_today, 0, 1)
        grid.addWidget(QLabel("Open Trades:"), 0, 2)
        grid.addWidget(self.lbl_open, 0, 3)
        grid.addWidget(QLabel("Closed Trades:"), 0, 4)
        grid.addWidget(self.lbl_closed, 0, 5)
        grid.addWidget(QLabel("Win Rate:"), 1, 0)
        grid.addWidget(self.lbl_winrate, 1, 1)
        grid.addWidget(QLabel("Total P/L:"), 1, 2)
        grid.addWidget(self.lbl_pnl, 1, 3)
        
        self.group_stats.setLayout(grid)
        layout.addWidget(self.group_stats)
        
        # Live Trades Table
        layout.addWidget(QLabel("<b>Active Positions (LTME Monitored)</b>"))
        self.table_active = QTableWidget()
        cols = ["Signal", "Symbol", "LTME Status", "Health Score", "Conf", "Entry", "CMP", "Profit", "Risk", "Trail SL", "Mkt", "Sec", "LTME Alerts"]
        self.table_active.setColumnCount(len(cols))
        self.table_active.setHorizontalHeaderLabels(cols)
        self.table_active.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_active.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_active.setStyleSheet("""
            QTableWidget { background-color: #1E2028; color: #FFF; border: none; }
            QHeaderView::section { background-color: #2D3039; color: #888; padding: 4px; }
        """)
        self.table_active.cellClicked.connect(self.on_trade_clicked)
        layout.addWidget(self.table_active)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_export = QPushButton("📥 Export CSV")
        self.btn_export.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        self.btn_export.clicked.connect(self.export_csv)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_export)
        layout.addLayout(btn_layout)

    def connect_signals(self):
        self.trade_manager.signals.position_updated.connect(self.refresh_ui)
        self.trade_manager.signals.order_executed.connect(self.refresh_ui)
        self.trade_manager.signals.notification.connect(self.show_notification)

    def show_notification(self, title, msg):
        QMessageBox.information(self, title, msg)

    def change_refresh_rate(self, text):
        rates = {"5 Seconds": 5000, "30 Seconds": 30000, "1 Minute": 60000, "2 Minutes": 120000, "5 Minutes": 300000}
        self.timer.setInterval(rates.get(text, 5000))
        
    def refresh_prices(self):
        # Background fetch to update cmp and run LTME for all active trades
        for pid, pos in self.trade_manager.engine.open_positions.items():
            sym = pos.symbol
            df = self.data_manager.get_stock_data(sym)
            if df is not None and not df.empty:
                cmp = df.iloc[-1]['Close']
                self.trade_manager.update_market_price(sym, cmp)
                
                # LTME evaluation
                t_dict = {
                    'symbol': sym,
                    'entry_price': pos.entry_price,
                    'sl': pos.sl,
                    'target': pos.target,
                    'direction': pos.direction,
                    'pnl': pos.unrealized_pnl
                }
                ltme_res = self.ltme.monitor_trade(t_dict, df, "UPTREND", "UPTREND")
                pos.ltme_status = ltme_res['ltme_status']
                pos.ltme_health = ltme_res['ltme_health']
                pos.ltme_alerts = ltme_res['ltme_alerts']
                pos.ltme_market = ltme_res['ltme_market']
                pos.ltme_sector = ltme_res['ltme_sector']
                pos.ltme_conf = ltme_res['ltme_conf']
                
                pos.eme_new_sl = ltme_res['new_sl']
                pos.eme_profit = ltme_res['profit']
                pos.eme_risk = ltme_res['risk']
                
        # Force UI update if there are trades
        if self.trade_manager.engine.open_positions:
            self.refresh_ui()

    def refresh_ui(self, *args, **kwargs):
        # Update Stats
        stats = self.trade_manager.engine.get_portfolio_state()
        
        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_trades = sum(1 for p in stats.open_positions.values() if p.entry_time.startswith(today_str))
        
        closed_trades = len(stats.closed_positions)
        win_trades = sum(1 for p in stats.closed_positions if p.realized_pnl > 0)
        win_rate = (win_trades / closed_trades * 100) if closed_trades > 0 else 0.0
        
        self.lbl_today.setText(str(today_trades))
        self.lbl_open.setText(str(len(stats.open_positions)))
        self.lbl_closed.setText(str(closed_trades))
        self.lbl_winrate.setText(f"{win_rate:.2f}%")
        
        total_pnl = stats.realized_pnl + stats.unrealized_pnl
        self.lbl_pnl.setText(f"{total_pnl:.2f}")
        if total_pnl > 0: self.lbl_pnl.setStyleSheet("color: #4CAF50;")
        elif total_pnl < 0: self.lbl_pnl.setStyleSheet("color: #F44336;")
        
        # Update Table
        positions = list(self.trade_manager.engine.open_positions.values())
        self.table_active.setRowCount(len(positions))
        
        for i, pos in enumerate(positions):
            def c(val, color=None):
                s = str(val) if not isinstance(val, float) else f"{val:.2f}"
                it = QTableWidgetItem(s)
                it.setTextAlignment(Qt.AlignCenter)
                if color: it.setForeground(QColor(color))
                return it
                
            status = getattr(pos, 'ltme_status', pos.status)
            status_color = "#FF9800" # Orange for Wait/Hold/Caution
            if status in ["BOOK PARTIAL", "MOVE SL", "HOLD"]: status_color = "#2196F3"
            elif status == "FULL EXIT": status_color = "#4CAF50"
            elif "EXIT" in status: status_color = "#F44336"
            
            pnl = getattr(pos, 'eme_profit', pos.unrealized_pnl)
            pnl_color = "#FFF"
            if pnl > 0: pnl_color = "#4CAF50"
            elif pnl < 0: pnl_color = "#F44336"
            
            alerts = getattr(pos, 'ltme_alerts', '')
            warn_color = "#F44336" if alerts != "Trade Healthy" else "#4CAF50"

            self.table_active.setItem(i, 0, c(pos.direction, "#4CAF50" if pos.direction=="BUY" else "#F44336"))
            self.table_active.setItem(i, 1, c(pos.symbol))
            self.table_active.setItem(i, 2, c(status, status_color))
            self.table_active.setItem(i, 3, c(getattr(pos, 'ltme_health', 'N/A')))
            self.table_active.setItem(i, 4, c(getattr(pos, 'ltme_conf', '85%')))
            self.table_active.setItem(i, 5, c(pos.entry_price))
            self.table_active.setItem(i, 6, c(pos.current_price))
            self.table_active.setItem(i, 7, c(pnl, pnl_color))
            self.table_active.setItem(i, 8, c(getattr(pos, 'eme_risk', 0.0), "#F44336"))
            self.table_active.setItem(i, 9, c(getattr(pos, 'eme_new_sl', pos.sl), "#FF9800"))
            self.table_active.setItem(i, 10, c(getattr(pos, 'ltme_market', '')))
            self.table_active.setItem(i, 11, c(getattr(pos, 'ltme_sector', '')))
            self.table_active.setItem(i, 12, c(alerts, warn_color))
            
    def on_trade_clicked(self, row, col):
        sym = self.table_active.item(row, 1).text()
        self.main_window.navigate_to_chart(sym)
        
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Trades", "trade_history.csv", "CSV Files (*.csv)")
        if path:
            conn = sqlite3.connect("data/paper_trading.db")
            df = pd.read_sql("SELECT * FROM positions", conn)
            df.to_csv(path, index=False)
            conn.close()
            QMessageBox.information(self, "Exported", f"Successfully exported to {path}")
