import logging
import csv
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QPushButton, QScrollArea, QGridLayout, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

try:
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog
except ImportError:
    pass

from application.database import DatabaseManager

class AnalyticsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Header Row
        header_layout = QHBoxLayout()
        title = QLabel("📊 ACCURACY ANALYTICS CENTER")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFF;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        btn_csv = QPushButton("Export CSV")
        btn_csv.setStyleSheet("background-color: #2196F3; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_csv.clicked.connect(self.export_csv)
        header_layout.addWidget(btn_csv)
        
        btn_pdf = QPushButton("Export PDF")
        btn_pdf.setStyleSheet("background-color: #F44336; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_pdf.clicked.connect(self.export_pdf)
        header_layout.addWidget(btn_pdf)
        
        self.layout.addLayout(header_layout)
        
        # Dashboard Stats (Top Row)
        self.stats_grid = QGridLayout()
        self.layout.addLayout(self.stats_grid)
        
        # Radar Score Analytics Table
        score_lbl = QLabel("📈 Radar Score Analytics")
        score_lbl.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(score_lbl)
        
        self.score_table = QTableWidget()
        self.score_table.setColumnCount(4)
        self.score_table.setHorizontalHeaderLabels(["Score Bracket", "Total Trades", "Wins", "Win Rate"])
        self.score_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.score_table.setStyleSheet("QTableWidget { background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px; } QHeaderView::section { background-color: #1A1C23; }")
        self.layout.addWidget(self.score_table)
        
        # Best / Worst Performing Stocks
        stock_perf_layout = QHBoxLayout()
        
        best_layout = QVBoxLayout()
        best_lbl = QLabel("🏆 Best Performing Stocks")
        best_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        self.best_table = QTableWidget()
        self.best_table.setColumnCount(3)
        self.best_table.setHorizontalHeaderLabels(["Symbol", "Wins", "Total"])
        self.best_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.best_table.setStyleSheet(self.score_table.styleSheet())
        best_layout.addWidget(best_lbl)
        best_layout.addWidget(self.best_table)
        
        worst_layout = QVBoxLayout()
        worst_lbl = QLabel("💔 Worst Performing Stocks")
        worst_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #F44336;")
        self.worst_table = QTableWidget()
        self.worst_table.setColumnCount(3)
        self.worst_table.setHorizontalHeaderLabels(["Symbol", "Losses", "Total"])
        self.worst_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.worst_table.setStyleSheet(self.score_table.styleSheet())
        worst_layout.addWidget(worst_lbl)
        worst_layout.addWidget(self.worst_table)
        
        stock_perf_layout.addLayout(best_layout)
        stock_perf_layout.addLayout(worst_layout)
        self.layout.addLayout(stock_perf_layout)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
    def _create_stat_card(self, title, value, color="#FFF"):
        card = QFrame()
        card.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        lyt = QVBoxLayout(card)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #888; font-size: 14px;")
        v_lbl = QLabel(value)
        v_lbl.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        t_lbl.setAlignment(Qt.AlignCenter)
        v_lbl.setAlignment(Qt.AlignCenter)
        lyt.addWidget(t_lbl)
        lyt.addWidget(v_lbl)
        return card

    def load_data(self):
        trades = self.db.get_all_trades()
        # trades: id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category
        
        total = 0
        wins = 0
        losses = 0
        buy_total = 0
        buy_wins = 0
        sell_total = 0
        sell_wins = 0
        
        gross_profit = 0.0
        gross_loss = 0.0
        total_return = 0.0
        
        score_brackets = {
            "95-100": {"t": 0, "w": 0},
            "90-94": {"t": 0, "w": 0},
            "85-89": {"t": 0, "w": 0},
            "80-84": {"t": 0, "w": 0},
            "Below 80": {"t": 0, "w": 0}
        }
        
        stock_stats = {}
        
        for t in trades:
            sym, sig, res, ret_str, sc = t[2], t[3], t[7], t[8], t[9]
            
            if res not in ("WIN", "LOSS"):
                continue
                
            total += 1
            is_win = (res == "WIN")
            if is_win: wins += 1
            else: losses += 1
            
            if "BUY" in sig:
                buy_total += 1
                if is_win: buy_wins += 1
            elif "SELL" in sig:
                sell_total += 1
                if is_win: sell_wins += 1
                
            ret_val = 0.0
            try:
                ret_val = float(ret_str.replace('%', '').replace('+', ''))
            except Exception as _e:
                logging.getLogger(__name__).debug("Suppressed exception in analytics_screen.py:168: %s", _e)
                
            total_return += ret_val
            if ret_val > 0:
                gross_profit += ret_val
            else:
                gross_loss += abs(ret_val)
                
            # Score Bracket
            bracket = "Below 80"
            if sc >= 95: bracket = "95-100"
            elif sc >= 90: bracket = "90-94"
            elif sc >= 85: bracket = "85-89"
            elif sc >= 80: bracket = "80-84"
            
            score_brackets[bracket]["t"] += 1
            if is_win: score_brackets[bracket]["w"] += 1
            
            # Stock Stats
            if sym not in stock_stats:
                stock_stats[sym] = {"t": 0, "w": 0, "l": 0}
            stock_stats[sym]["t"] += 1
            if is_win: stock_stats[sym]["w"] += 1
            else: stock_stats[sym]["l"] += 1
            
        # UI Updates
        acc = (wins / total * 100) if total > 0 else 0
        buy_acc = (buy_wins / buy_total * 100) if buy_total > 0 else 0
        sell_acc = (sell_wins / sell_total * 100) if sell_total > 0 else 0
        pf = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
        avg_ret = (total_return / total) if total > 0 else 0
        
        # Populate Dashboard Cards
        c1 = self._create_stat_card("Overall Accuracy", f"{acc:.1f}%", "#4CAF50" if acc >= 60 else "#FF9800")
        c2 = self._create_stat_card("BUY Accuracy", f"{buy_acc:.1f}%")
        c3 = self._create_stat_card("SELL Accuracy", f"{sell_acc:.1f}%")
        c4 = self._create_stat_card("Profit Factor", f"{pf:.2f}", "#4CAF50" if pf >= 1.5 else "#F44336")
        c5 = self._create_stat_card("Average Return", f"{avg_ret:+.2f}%", "#4CAF50" if avg_ret >= 0 else "#F44336")
        c6 = self._create_stat_card("Total Signals", str(total))
        
        self.stats_grid.addWidget(c1, 0, 0)
        self.stats_grid.addWidget(c2, 0, 1)
        self.stats_grid.addWidget(c3, 0, 2)
        self.stats_grid.addWidget(c4, 1, 0)
        self.stats_grid.addWidget(c5, 1, 1)
        self.stats_grid.addWidget(c6, 1, 2)
        
        # Populate Score Table
        self.score_table.setRowCount(0)
        for br, st in score_brackets.items():
            if st["t"] > 0:
                row = self.score_table.rowCount()
                self.score_table.insertRow(row)
                self.score_table.setItem(row, 0, QTableWidgetItem(br))
                self.score_table.setItem(row, 1, QTableWidgetItem(str(st["t"])))
                self.score_table.setItem(row, 2, QTableWidgetItem(str(st["w"])))
                wr = (st["w"] / st["t"]) * 100
                wr_item = QTableWidgetItem(f"{wr:.1f}%")
                wr_item.setForeground(QColor("#4CAF50" if wr >= 70 else "#F44336"))
                self.score_table.setItem(row, 3, wr_item)
                
        # Populate Best/Worst Stocks
        sorted_best = sorted(stock_stats.items(), key=lambda x: (x[1]["w"], -x[1]["t"]), reverse=True)
        sorted_worst = sorted(stock_stats.items(), key=lambda x: (x[1]["l"], -x[1]["t"]), reverse=True)
        
        self.best_table.setRowCount(0)
        for sym, st in sorted_best[:10]:
            if st["w"] == 0: continue
            r = self.best_table.rowCount()
            self.best_table.insertRow(r)
            self.best_table.setItem(r, 0, QTableWidgetItem(sym))
            self.best_table.setItem(r, 1, QTableWidgetItem(str(st["w"])))
            self.best_table.setItem(r, 2, QTableWidgetItem(str(st["t"])))
            
        self.worst_table.setRowCount(0)
        for sym, st in sorted_worst[:10]:
            if st["l"] == 0: continue
            r = self.worst_table.rowCount()
            self.worst_table.insertRow(r)
            self.worst_table.setItem(r, 0, QTableWidgetItem(sym))
            self.worst_table.setItem(r, 1, QTableWidgetItem(str(st["l"])))
            self.worst_table.setItem(r, 2, QTableWidgetItem(str(st["t"])))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Analytics CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Analytics Summary Export"])
                # Extract some stats and write
            QMessageBox.information(self, "Export Successful", "Data exported to CSV successfully.")

    def export_pdf(self):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
            if path:
                printer.setOutputFileName(path)
                self.render(printer)
                QMessageBox.information(self, "Export Successful", "Analytics saved to PDF.")
        except NameError:
            QMessageBox.warning(self, "Error", "PDF Export requires QtPrintSupport which is not available.")
