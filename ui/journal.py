from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QFrame, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from ui.styles import CARD_BG, BTN_BLUE, BG_COLOR
from application.database import DatabaseManager
import csv
from datetime import datetime

class JournalScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # TITLE ROW
        header_layout = QHBoxLayout()
        title = QLabel("TRADE JOURNAL")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold;")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold;")
        self.btn_export.clicked.connect(self.export_csv)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        header_layout.addWidget(self.btn_export)
        layout.addLayout(header_layout)
        
        # SUMMARY CARDS
        summary_layout = QHBoxLayout()
        self.lbl_total = self.create_summary_card("Total Trades", "0", summary_layout)
        self.lbl_wins = self.create_summary_card("Wins", "0", summary_layout)
        self.lbl_losses = self.create_summary_card("Losses", "0", summary_layout)
        self.lbl_winrate = self.create_summary_card("Win Rate", "0%", summary_layout)
        layout.addLayout(summary_layout)
        
        # FILTER
        filter_layout = QHBoxLayout()
        filter_lbl = QLabel("Filter by Status:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "WIN", "LOSS", "PENDING"])
        self.filter_combo.currentTextChanged.connect(self.filter_table)
        self.filter_combo.setStyleSheet(f"background-color: {CARD_BG}; padding: 5px; border: 1px solid #3D4047;")
        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # TABLE
        self.table = QTableWidget()
        self.headers = ["Date", "Symbol", "Signal", "Entry", "SL", "Target", "Exit", "P/L %", "Status"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; border: none;")
        
        layout.addWidget(self.table)
        self.load_data()
        
    def create_summary_card(self, title, value, parent_layout):
        card = QFrame()
        card.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px;")
        l = QVBoxLayout(card)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #A0AAB5; font-size: 12px;")
        t_lbl.setAlignment(Qt.AlignCenter)
        v_lbl = QLabel(value)
        v_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        v_lbl.setAlignment(Qt.AlignCenter)
        l.addWidget(t_lbl)
        l.addWidget(v_lbl)
        parent_layout.addWidget(card)
        return v_lbl

    def load_data(self):
        try:
            db = DatabaseManager()
            trades = db.get_all_trades()
            
            self.table.setRowCount(len(trades))
            
            total = len(trades)
            wins = 0
            losses = 0
            
            for row, t in enumerate(trades):
                # t = id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category
                _id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category = t
                
                if result == "WIN": wins += 1
                elif result == "LOSS": losses += 1
                
                # Mock exit
                exit_price = "--"
                if result == "WIN": exit_price = str(target)
                elif result == "LOSS": exit_price = str(sl)
                
                self.table.setItem(row, 0, QTableWidgetItem(str(date)))
                self.table.setItem(row, 1, QTableWidgetItem(str(symbol)))
                
                sig_item = QTableWidgetItem(str(signal))
                if signal == "BUY": sig_item.setForeground(QBrush(QColor("#4CAF50")))
                else: sig_item.setForeground(QBrush(QColor("#F44336")))
                self.table.setItem(row, 2, sig_item)
                
                self.table.setItem(row, 3, QTableWidgetItem(str(entry)))
                self.table.setItem(row, 4, QTableWidgetItem(str(sl)))
                self.table.setItem(row, 5, QTableWidgetItem(str(target)))
                self.table.setItem(row, 6, QTableWidgetItem(exit_price))
                
                ret_item = QTableWidgetItem(str(return_pct))
                if str(return_pct).startswith("+"): ret_item.setForeground(QBrush(QColor("#4CAF50")))
                elif str(return_pct).startswith("-"): ret_item.setForeground(QBrush(QColor("#F44336")))
                self.table.setItem(row, 7, ret_item)
                
                res_item = QTableWidgetItem(str(result))
                if result == "WIN": res_item.setForeground(QBrush(QColor("#4CAF50")))
                elif result == "LOSS": res_item.setForeground(QBrush(QColor("#F44336")))
                elif result == "PENDING": res_item.setForeground(QBrush(QColor("#FF9800")))
                self.table.setItem(row, 8, res_item)
                
            # Update summary
            self.lbl_total.setText(str(total))
            self.lbl_wins.setText(str(wins))
            self.lbl_losses.setText(str(losses))
            completed = wins + losses
            win_rate = (wins / completed * 100) if completed > 0 else 0
            self.lbl_winrate.setText(f"{win_rate:.1f}%")
            
            # Apply current filter
            self.filter_table(self.filter_combo.currentText())
            
        except Exception as e:
            print("Error loading journal:", e)

    def filter_table(self, status):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 8)
            if not item: continue
            
            if status == "All" or item.text() == status:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
                
    def export_csv(self):
        default_name = f"journal_{datetime.now().strftime('%d-%b-%Y')}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export Journal", default_name, "CSV Files (*.csv)")
        
        if not path:
            return
            
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                
                for row in range(self.table.rowCount()):
                    # Only export visible rows
                    if self.table.isRowHidden(row): continue
                    
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "Success", f"Journal exported to:\\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV:\\n{str(e)}")
