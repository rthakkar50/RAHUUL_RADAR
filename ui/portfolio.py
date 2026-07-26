import logging
import sqlite3
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QGroupBox, QGridLayout, QMessageBox, QTabWidget, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from application.paper_trading_service import PaperTradingEngine
from application.data_manager import DataManager

logger = logging.getLogger("PortfolioPage")

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
        layout.setSpacing(15)
        
        title = QLabel("💼 LIVE PORTFOLIO & TRADING ANALYTICS")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2196F3;")
        layout.addWidget(title)
        
        # --- TOP SECTION: PORTFOLIO & RISK SUMMARY ---
        top_layout = QHBoxLayout()
        
        # 1. PORTFOLIO SUMMARY (7 required metrics + styling)
        self.group_summary = QGroupBox("Portfolio Summary")
        self.group_summary.setStyleSheet("QGroupBox { border: 1px solid #2196F3; border-radius: 6px; margin-top: 10px; font-weight: bold; color: #FFF; padding: 10px; }")
        grid = QGridLayout()
        grid.setSpacing(12)
        
        self.lbl_total_cap = self._create_summary_item(grid, "Total Capital:", 0, 0)
        self.lbl_invested = self._create_summary_item(grid, "Invested Amount:", 0, 2)
        self.lbl_avail_cash = self._create_summary_item(grid, "Available Cash:", 0, 4)
        self.lbl_curr_val = self._create_summary_item(grid, "Current Portfolio Value:", 1, 0)
        self.lbl_today_pnl = self._create_summary_item(grid, "Today's P&L:", 1, 2)
        self.lbl_overall_pnl = self._create_summary_item(grid, "Overall P&L:", 2, 0)
        self.lbl_overall_ret = self._create_summary_item(grid, "Overall Return %:", 2, 2)
        
        self.group_summary.setLayout(grid)
        top_layout.addWidget(self.group_summary, stretch=2)
        
        # SPRINT-75 LIVE RISK MANAGER
        self.group_risk = QGroupBox("Live Risk Summary")
        self.group_risk.setStyleSheet("QGroupBox { border: 1px solid #FF9800; border-radius: 6px; margin-top: 10px; font-weight: bold; color: #FFF; padding: 10px; }")
        risk_grid = QGridLayout()
        risk_grid.setSpacing(12)
        
        self.lbl_risk_cap = self._create_summary_item(risk_grid, "Max Daily Loss:", 0, 0)
        self.lbl_risk_used = self._create_summary_item(risk_grid, "Current Open Risk:", 0, 2)
        self.lbl_risk_remain = self._create_summary_item(risk_grid, "Remaining Risk:", 1, 0)
        self.lbl_risk_expo = self._create_summary_item(risk_grid, "Open Exposure:", 1, 2)
        
        self.group_risk.setLayout(risk_grid)
        top_layout.addWidget(self.group_risk, stretch=1)
        
        layout.addLayout(top_layout)
        
        # --- TAB SECTION: OPEN, CLOSED, AND ANALYTICS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3D4047; border-radius: 6px; background-color: #1E2028; }
            QTabBar::tab { background-color: #2A2D35; color: #BBB; padding: 8px 18px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #2196F3; color: white; }
        """)
        
        # TAB 1: OPEN POSITIONS
        tab_pos = QWidget()
        pos_layout = QVBoxLayout(tab_pos)
        
        self.lbl_no_open = QLabel("No Data - No Open Positions Currently Available")
        self.lbl_no_open.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; padding: 30px;")
        self.lbl_no_open.setAlignment(Qt.AlignCenter)
        
        self.table_pos = QTableWidget()
        open_cols = ["Symbol", "Direction", "Qty", "Entry Price", "CMP", "Unrealized P/L", "Stop Loss", "Target", "R:R", "Status"]
        self.table_pos.setColumnCount(len(open_cols))
        self.table_pos.setHorizontalHeaderLabels(open_cols)
        self.table_pos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_pos.verticalHeader().setVisible(False)
        self.table_pos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_pos.setStyleSheet("QTableWidget { background-color: #1A1C20; color: #FFF; border: none; gridline-color: #2D3038; } QHeaderView::section { background-color: #252832; color: #A0AAB5; font-weight: bold; border: none; padding: 6px; }")
        
        pos_layout.addWidget(self.lbl_no_open)
        pos_layout.addWidget(self.table_pos)
        
        btn_exit = QPushButton("Close All Positions")
        btn_exit.setCursor(Qt.PointingHandCursor)
        btn_exit.setStyleSheet("background-color: #F44336; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        btn_exit.clicked.connect(self.close_all_positions)
        pos_layout.addWidget(btn_exit)
        
        self.tabs.addTab(tab_pos, "Open Positions")
        
        # TAB 2: CLOSED POSITIONS
        tab_closed = QWidget()
        closed_layout = QVBoxLayout(tab_closed)
        
        self.lbl_no_closed = QLabel("No Data - No Closed Positions Recorded")
        self.lbl_no_closed.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; padding: 30px;")
        self.lbl_no_closed.setAlignment(Qt.AlignCenter)
        
        self.table_closed = QTableWidget()
        closed_cols = ["Symbol", "Direction", "Entry", "Exit", "Profit/Loss", "Holding Days", "Return %", "Exit Reason"]
        self.table_closed.setColumnCount(len(closed_cols))
        self.table_closed.setHorizontalHeaderLabels(closed_cols)
        self.table_closed.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_closed.verticalHeader().setVisible(False)
        self.table_closed.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_closed.setStyleSheet("QTableWidget { background-color: #1A1C20; color: #FFF; border: none; gridline-color: #2D3038; } QHeaderView::section { background-color: #252832; color: #A0AAB5; font-weight: bold; border: none; padding: 6px; }")
        
        closed_layout.addWidget(self.lbl_no_closed)
        closed_layout.addWidget(self.table_closed)
        
        self.tabs.addTab(tab_closed, "Closed Positions")
        
        # TAB 3: PERFORMANCE ANALYTICS
        tab_stats = QWidget()
        stats_layout = QVBoxLayout(tab_stats)
        stats_layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_no_stats = QLabel("No Data - Complete at least one trade to generate performance analytics")
        self.lbl_no_stats.setStyleSheet("font-size: 16px; color: #888; font-weight: bold; padding: 30px;")
        self.lbl_no_stats.setAlignment(Qt.AlignCenter)
        stats_layout.addWidget(self.lbl_no_stats)
        
        self.grid_stats = QGridLayout()
        self.grid_stats.setSpacing(15)
        
        self.card_total_trades = self._create_stat_card(self.grid_stats, "Total Trades", 0, 0)
        self.card_win_rate = self._create_stat_card(self.grid_stats, "Win Rate", 0, 1)
        self.card_loss_rate = self._create_stat_card(self.grid_stats, "Loss Rate", 0, 2)
        
        self.card_avg_win = self._create_stat_card(self.grid_stats, "Average Winner", 1, 0)
        self.card_avg_loss = self._create_stat_card(self.grid_stats, "Average Loser", 1, 1)
        self.card_profit_factor = self._create_stat_card(self.grid_stats, "Profit Factor", 1, 2)
        
        self.card_avg_rr = self._create_stat_card(self.grid_stats, "Average Risk Reward", 2, 0)
        self.card_largest_win = self._create_stat_card(self.grid_stats, "Largest Win", 2, 1)
        self.card_largest_loss = self._create_stat_card(self.grid_stats, "Largest Loss", 2, 2)
        
        stats_layout.addLayout(self.grid_stats)
        stats_layout.addStretch()
        self.tabs.addTab(tab_stats, "Performance Analytics")
        
        layout.addWidget(self.tabs)

    def _create_summary_item(self, grid, title, row, col):
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #A0AAB5; font-size: 13px; font-weight: normal;")
        lbl_val = QLabel("No Data")
        lbl_val.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: bold;")
        grid.addWidget(lbl_title, row, col)
        grid.addWidget(lbl_val, row, col + 1)
        return lbl_val

    def _create_stat_card(self, grid, title, row, col):
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #252832; border: 1px solid #3D4047; border-radius: 8px; padding: 15px; }")
        l = QVBoxLayout(card)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #A0AAB5; font-size: 13px; border: none;")
        t_lbl.setAlignment(Qt.AlignCenter)
        v_lbl = QLabel("No Data")
        v_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFF; border: none; margin-top: 8px;")
        v_lbl.setAlignment(Qt.AlignCenter)
        l.addWidget(t_lbl)
        l.addWidget(v_lbl)
        grid.addWidget(card, row, col)
        return v_lbl

    def connect_signals(self):
        self.engine.signals.portfolio_updated.connect(self.on_portfolio_update)
        self.engine.signals.position_updated.connect(self.refresh_ui)
        self.engine.signals.order_executed.connect(self.refresh_ui)

    def update_live_prices(self):
        for pid, p in list(self.engine.engine.open_positions.items()):
            sym = p.symbol
            df = self.data_manager.get_stock_data(sym)
            if df is not None and not df.empty:
                cmp = df.iloc[-1]['Close']
                self.engine.update_market_price(sym, cmp)

    def on_portfolio_update(self, data):
        self._update_summary_labels(data)

    def _update_summary_labels(self, data):
        if not data:
            for lbl in [self.lbl_total_cap, self.lbl_invested, self.lbl_avail_cash, self.lbl_curr_val, self.lbl_today_pnl, self.lbl_overall_pnl, self.lbl_overall_ret]:
                lbl.setText("No Data")
                lbl.setStyleSheet("color: #A0AAB5; font-size: 15px; font-weight: bold;")
            return
            
        def fmt_money(lbl, val, colorize=False):
            if val is None or val == "No Data":
                lbl.setText("No Data")
                lbl.setStyleSheet("color: #A0AAB5; font-size: 15px; font-weight: bold;")
            else:
                lbl.setText(f"₹ {float(val):,.2f}")
                if colorize:
                    if float(val) > 0: lbl.setStyleSheet("color: #4CAF50; font-size: 15px; font-weight: bold;")
                    elif float(val) < 0: lbl.setStyleSheet("color: #F44336; font-size: 15px; font-weight: bold;")
                    else: lbl.setStyleSheet("color: #FFF; font-size: 15px; font-weight: bold;")
                else:
                    lbl.setStyleSheet("color: #FFF; font-size: 15px; font-weight: bold;")

        total_cap = data.get("capital", 100000.0)
        invested = data.get("margin", 0.0)
        avail = total_cap - invested if total_cap is not None and invested is not None else None
        open_pnl = data.get("open_pnl", 0.0)
        closed_pnl = data.get("closed_pnl", 0.0)
        overall_pnl = (open_pnl + closed_pnl) if open_pnl is not None and closed_pnl is not None else None
        today_pnl = data.get("today_pnl", 0.0)
        curr_val = (total_cap + open_pnl) if total_cap is not None and open_pnl is not None else None
        
        overall_ret = None
        start_cap = getattr(self.engine.engine, "starting_capital", 100000.0)
        if start_cap > 0 and overall_pnl is not None:
            overall_ret = (overall_pnl / start_cap) * 100.0

        fmt_money(self.lbl_total_cap, total_cap)
        fmt_money(self.lbl_invested, invested)
        fmt_money(self.lbl_avail_cash, avail)
        fmt_money(self.lbl_curr_val, curr_val, colorize=True)
        fmt_money(self.lbl_today_pnl, today_pnl, colorize=True)
        fmt_money(self.lbl_overall_pnl, overall_pnl, colorize=True)
        
        if overall_ret is None:
            self.lbl_overall_ret.setText("No Data")
            self.lbl_overall_ret.setStyleSheet("color: #A0AAB5; font-size: 15px; font-weight: bold;")
        else:
            self.lbl_overall_ret.setText(f"{overall_ret:+.2f}%")
            col = "#4CAF50" if overall_ret > 0 else ("#F44336" if overall_ret < 0 else "#FFF")
            self.lbl_overall_ret.setStyleSheet(f"color: {col}; font-size: 15px; font-weight: bold;")

    def refresh_ui(self):
        # 1. Update Open Positions
        open_positions = list(self.engine.engine.open_positions.values())
        if not open_positions:
            self.lbl_no_open.show()
            self.table_pos.hide()
        else:
            self.lbl_no_open.hide()
            self.table_pos.show()
            self.table_pos.setRowCount(len(open_positions))
            
            for i, p in enumerate(open_positions):
                def c(val, color=None):
                    s = str(val) if not isinstance(val, float) else f"{val:,.2f}"
                    it = QTableWidgetItem(s)
                    it.setTextAlignment(Qt.AlignCenter)
                    if color: it.setForeground(QColor(color))
                    return it
                    
                dir_col = "#4CAF50" if p.direction=="BUY" else "#F44336"
                pnl_col = "#4CAF50" if p.unrealized_pnl > 0 else ("#F44336" if p.unrealized_pnl < 0 else "#FFF")
                
                # Compute R:R
                rr_str = "No Data"
                try:
                    if p.direction == "BUY" and p.sl and p.target:
                        risk = abs(p.entry_price - p.sl)
                        reward = abs(p.target - p.entry_price)
                        if risk > 0 and reward > 0:
                            rr_str = f"1 : {reward/risk:.2f}"
                    elif p.direction in ["SELL", "SHORT"] and p.sl and p.target:
                        risk = abs(p.sl - p.entry_price)
                        reward = abs(p.entry_price - p.target)
                        if risk > 0 and reward > 0:
                            rr_str = f"1 : {reward/risk:.2f}"
                except Exception:
                    rr_str = "No Data"

                self.table_pos.setItem(i, 0, c(p.symbol))
                self.table_pos.setItem(i, 1, c(p.direction, dir_col))
                self.table_pos.setItem(i, 2, c(p.qty))
                self.table_pos.setItem(i, 3, c(p.entry_price))
                self.table_pos.setItem(i, 4, c(p.current_price))
                self.table_pos.setItem(i, 5, c(p.unrealized_pnl, pnl_col))
                self.table_pos.setItem(i, 6, c(p.sl, "#F44336"))
                self.table_pos.setItem(i, 7, c(p.target, "#4CAF50"))
                self.table_pos.setItem(i, 8, QTableWidgetItem(rr_str))
                self.table_pos.item(i, 8).setTextAlignment(Qt.AlignCenter)
                self.table_pos.setItem(i, 9, c(p.status, "#2196F3"))

        # 2. Update Closed Positions
        closed_positions = list(self.engine.engine.closed_positions)
        if not closed_positions and os.path.exists(self.engine.db_path):
            try:
                conn = sqlite3.connect(self.engine.db_path)
                cur = conn.cursor()
                cur.execute("SELECT symbol, direction, entry_price, exit_price, net_pnl, entry_time, exit_time, status FROM positions WHERE status='CLOSED'")
                rows = cur.fetchall()
                conn.close()
                closed_positions = []
                for r in rows:
                    closed_positions.append({
                        "symbol": r[0], "direction": r[1], "entry_price": r[2],
                        "exit_price": r[3], "pnl": r[4], "entry_time": r[5], "exit_time": r[6], "reason": "Target/SL Executed"
                    })
            except Exception as _e:
                logger.debug("Suppressed exception loading closed trades: %s", _e)

        if not closed_positions:
            self.lbl_no_closed.show()
            self.table_closed.hide()
        else:
            self.lbl_no_closed.hide()
            self.table_closed.show()
            self.table_closed.setRowCount(len(closed_positions))
            for i, p in enumerate(closed_positions):
                def c_cl(val, color=None):
                    s = str(val) if not isinstance(val, float) else f"{val:,.2f}"
                    it = QTableWidgetItem(s)
                    it.setTextAlignment(Qt.AlignCenter)
                    if color: it.setForeground(QColor(color))
                    return it

                is_dict = isinstance(p, dict)
                sym = p.get("symbol") if is_dict else p.symbol
                direction = p.get("direction") if is_dict else p.direction
                entry = float(p.get("entry_price") if is_dict else p.entry_price)
                exit_p = float(p.get("exit_price") if is_dict else (getattr(p, "exit_price", entry) or entry))
                pnl = float(p.get("pnl") if is_dict else getattr(p, "realized_pnl", 0.0))
                entry_t = p.get("entry_time") if is_dict else getattr(p, "entry_time", "")
                exit_t = p.get("exit_time") if is_dict else getattr(p, "exit_time", "")
                reason = p.get("reason") if is_dict else "Closed"

                # Holding days
                holding_str = "No Data"
                try:
                    if entry_t and exit_t and str(entry_t) != "None" and str(exit_t) != "None":
                        dt1 = datetime.fromisoformat(str(entry_t).split(".")[0])
                        dt2 = datetime.fromisoformat(str(exit_t).split(".")[0])
                        days = (dt2 - dt1).total_seconds() / 86400.0
                        if days < 1:
                            holding_str = "0 Days (Intraday)"
                        else:
                            holding_str = f"{int(days)} Days"
                except Exception:
                    holding_str = "No Data"

                # Return %
                ret_str = "No Data"
                if entry > 0:
                    ret_val = ((exit_p - entry) / entry * 100.0) * (1 if direction=="BUY" else -1)
                    ret_str = f"{ret_val:+.2f}%"

                dir_col = "#4CAF50" if direction=="BUY" else "#F44336"
                pnl_col = "#4CAF50" if pnl > 0 else ("#F44336" if pnl < 0 else "#FFF")

                self.table_closed.setItem(i, 0, c_cl(sym))
                self.table_closed.setItem(i, 1, c_cl(direction, dir_col))
                self.table_closed.setItem(i, 2, c_cl(entry))
                self.table_closed.setItem(i, 3, c_cl(exit_p))
                self.table_closed.setItem(i, 4, c_cl(pnl, pnl_col))
                self.table_closed.setItem(i, 5, QTableWidgetItem(holding_str))
                self.table_closed.item(i, 5).setTextAlignment(Qt.AlignCenter)
                self.table_closed.setItem(i, 6, c_cl(ret_str, pnl_col))
                self.table_closed.setItem(i, 7, c_cl(reason, "#A0AAB5"))

        # 3. Update Performance Analytics
        self._update_analytics_cards(closed_positions)

        # 4. Update Sprint 75 Risk Panel
        try:
            from core.risk_manager import RiskManager
            rm = RiskManager.get_instance()
            risk_summary = rm.get_live_risk_summary()
            
            self.lbl_risk_cap.setText(f"₹ {risk_summary.get('max_daily_loss', 0):,.2f}")
            self.lbl_risk_used.setText(f"₹ {risk_summary.get('open_risk', 0):,.2f}")
            
            rem = risk_summary.get('remaining_risk', 0)
            self.lbl_risk_remain.setText(f"₹ {rem:,.2f}")
            if rem < 0:
                self.lbl_risk_remain.setStyleSheet("color: #F44336; font-size: 15px; font-weight: bold;")
            else:
                self.lbl_risk_remain.setStyleSheet("color: #4CAF50; font-size: 15px; font-weight: bold;")
                
            self.lbl_risk_expo.setText(f"₹ {risk_summary.get('open_exposure', 0):,.2f}")
        except Exception as _e:
            logger.debug("Suppressed exception in portfolio.py: %s", _e)

    def _update_analytics_cards(self, closed_positions):
        stats = self.engine.get_statistics()
        total_trades = len(closed_positions)
        
        if total_trades == 0:
            self.lbl_no_stats.show()
            for card_lbl in [self.card_total_trades, self.card_win_rate, self.card_loss_rate, self.card_avg_win, self.card_avg_loss, self.card_profit_factor, self.card_avg_rr, self.card_largest_win, self.card_largest_loss]:
                card_lbl.setText("No Data")
                card_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #A0AAB5; border: none; margin-top: 8px;")
            return

        self.lbl_no_stats.hide()
        self.card_total_trades.setText(str(total_trades))
        self.card_total_trades.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFF; border: none; margin-top: 8px;")
        
        win_rate = stats.get("win_rate", 0.0) if stats else 0.0
        loss_rate = stats.get("loss_rate", 0.0) if stats else 0.0
        avg_win = stats.get("avg_win", 0.0) if stats else 0.0
        avg_loss = stats.get("avg_loss", 0.0) if stats else 0.0
        profit_fac = stats.get("profit_factor", 0.0) if stats else 0.0

        self.card_win_rate.setText(f"{win_rate:.1f}%")
        self.card_win_rate.setStyleSheet("font-size: 22px; font-weight: bold; color: #4CAF50; border: none; margin-top: 8px;")
        self.card_loss_rate.setText(f"{loss_rate:.1f}%")
        self.card_loss_rate.setStyleSheet("font-size: 22px; font-weight: bold; color: #F44336; border: none; margin-top: 8px;")
        
        self.card_avg_win.setText(f"₹ {avg_win:,.2f}" if avg_win > 0 else "No Data")
        self.card_avg_win.setStyleSheet("font-size: 22px; font-weight: bold; color: #4CAF50; border: none; margin-top: 8px;")
        
        self.card_avg_loss.setText(f"₹ {avg_loss:,.2f}" if avg_loss > 0 else "No Data")
        self.card_avg_loss.setStyleSheet("font-size: 22px; font-weight: bold; color: #F44336; border: none; margin-top: 8px;")
        
        self.card_profit_factor.setText(f"{profit_fac:.2f}" if profit_fac > 0 else "No Data")
        self.card_profit_factor.setStyleSheet("font-size: 22px; font-weight: bold; color: #2196F3; border: none; margin-top: 8px;")

        # Calculate Largest Win, Largest Loss, and Average R:R from closed positions
        wins = []
        losses = []
        rr_vals = []
        
        for p in closed_positions:
            is_dict = isinstance(p, dict)
            pnl = float(p.get("pnl") if is_dict else getattr(p, "realized_pnl", 0.0))
            if pnl > 0: wins.append(pnl)
            elif pnl < 0: losses.append(abs(pnl))

            # R:R if available
            try:
                entry = float(p.get("entry_price") if is_dict else p.entry_price)
                sl_val = float(p.get("sl", 0.0) if is_dict else getattr(p, "sl", 0.0))
                target_val = float(p.get("target", 0.0) if is_dict else getattr(p, "target", 0.0))
                direction = p.get("direction", "BUY") if is_dict else getattr(p, "direction", "BUY")
                if direction == "BUY" and sl_val > 0 and target_val > 0:
                    risk = abs(entry - sl_val)
                    reward = abs(target_val - entry)
                    if risk > 0: rr_vals.append(reward / risk)
                elif direction in ["SELL", "SHORT"] and sl_val > 0 and target_val > 0:
                    risk = abs(sl_val - entry)
                    reward = abs(entry - target_val)
                    if risk > 0: rr_vals.append(reward / risk)
            except Exception:
                pass

        if rr_vals:
            self.card_avg_rr.setText(f"1 : {sum(rr_vals)/len(rr_vals):.2f}")
            self.card_avg_rr.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF9800; border: none; margin-top: 8px;")
        elif avg_win > 0 and avg_loss > 0:
            self.card_avg_rr.setText(f"1 : {avg_win/avg_loss:.2f}")
            self.card_avg_rr.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF9800; border: none; margin-top: 8px;")
        else:
            self.card_avg_rr.setText("No Data")
            self.card_avg_rr.setStyleSheet("font-size: 22px; font-weight: bold; color: #A0AAB5; border: none; margin-top: 8px;")

        if wins:
            self.card_largest_win.setText(f"₹ {max(wins):,.2f}")
            self.card_largest_win.setStyleSheet("font-size: 22px; font-weight: bold; color: #4CAF50; border: none; margin-top: 8px;")
        else:
            self.card_largest_win.setText("No Data")
            self.card_largest_win.setStyleSheet("font-size: 22px; font-weight: bold; color: #A0AAB5; border: none; margin-top: 8px;")

        if losses:
            self.card_largest_loss.setText(f"₹ {max(losses):,.2f}")
            self.card_largest_loss.setStyleSheet("font-size: 22px; font-weight: bold; color: #F44336; border: none; margin-top: 8px;")
        else:
            self.card_largest_loss.setText("No Data")
            self.card_largest_loss.setStyleSheet("font-size: 22px; font-weight: bold; color: #A0AAB5; border: none; margin-top: 8px;")

    def close_all_positions(self):
        for pid, p in list(self.engine.engine.open_positions.items()):
            self.engine.close_position(pid, p.current_price, "Manual Close")
        self.refresh_ui()
        QMessageBox.information(self, "Success", "All open positions have been closed.")
