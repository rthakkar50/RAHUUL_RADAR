import os
import json
import csv
from datetime import datetime, date, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QFrame, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QLineEdit, QTextEdit, QDateEdit, QCheckBox, QSplitter
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QBrush, QFont, QDesktopServices
from PySide6.QtCore import QUrl
from ui.styles import CARD_BG, BTN_BLUE, BG_COLOR
from application.database import DatabaseManager

ANNOTATIONS_FILE = os.path.join("data", "journal_annotations.json")

class JournalScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.annotations = self._load_annotations()
        self.selected_trade_id = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- TITLE ROW ---
        header_layout = QHBoxLayout()
        title = QLabel("📓 TRADING JOURNAL & PERFORMANCE TRACKING")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2196F3;")
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; padding: 7px 18px; border-radius: 4px; font-weight: bold;")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.setStyleSheet("background-color: #4CAF50; color: white; padding: 7px 18px; border-radius: 4px; font-weight: bold;")
        self.btn_export.clicked.connect(self.export_csv)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        header_layout.addWidget(self.btn_export)
        layout.addLayout(header_layout)
        
        # --- SUMMARY CARDS ---
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        self.lbl_total = self.create_summary_card("Total Trades", "No Data", summary_layout)
        self.lbl_wins = self.create_summary_card("Wins", "No Data", summary_layout)
        self.lbl_losses = self.create_summary_card("Losses", "No Data", summary_layout)
        self.lbl_winrate = self.create_summary_card("Win Rate", "No Data", summary_layout)
        layout.addLayout(summary_layout)
        
        # --- FILTERS ROW ---
        filter_box = QGroupBox("Filter Journal Record")
        filter_box.setStyleSheet("QGroupBox { border: 1px solid #3D4047; border-radius: 6px; font-weight: bold; color: #BBB; padding: 10px; }")
        filter_layout = QHBoxLayout(filter_box)
        filter_layout.setSpacing(12)
        
        # 1. Win/Loss Result Filter
        filter_layout.addWidget(QLabel("Result:"))
        self.combo_result = QComboBox()
        self.combo_result.addItems(["All Results", "WIN", "LOSS", "PENDING"])
        self.combo_result.currentTextChanged.connect(self.filter_table)
        self.combo_result.setStyleSheet(f"background-color: {CARD_BG}; color: white; padding: 5px; border: 1px solid #3D4047; border-radius: 4px;")
        filter_layout.addWidget(self.combo_result)
        
        # 2. BUY/SELL Direction Filter
        filter_layout.addWidget(QLabel("Direction:"))
        self.combo_signal = QComboBox()
        self.combo_signal.addItems(["All Signals", "BUY", "SELL"])
        self.combo_signal.currentTextChanged.connect(self.filter_table)
        self.combo_signal.setStyleSheet(f"background-color: {CARD_BG}; color: white; padding: 5px; border: 1px solid #3D4047; border-radius: 4px;")
        filter_layout.addWidget(self.combo_signal)
        
        # 3. Strategy Filter
        filter_layout.addWidget(QLabel("Strategy:"))
        self.combo_strategy = QComboBox()
        self.combo_strategy.addItems(["All Strategies"])
        self.combo_strategy.currentTextChanged.connect(self.filter_table)
        self.combo_strategy.setStyleSheet(f"background-color: {CARD_BG}; color: white; padding: 5px; border: 1px solid #3D4047; border-radius: 4px;")
        filter_layout.addWidget(self.combo_strategy)
        
        # 4. Date Range Filter
        self.chk_date = QCheckBox("Date Range:")
        self.chk_date.setStyleSheet("color: #FFF; font-weight: bold;")
        self.chk_date.stateChanged.connect(self.filter_table)
        filter_layout.addWidget(self.chk_date)
        
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate().addDays(-30))
        self.date_start.setStyleSheet(f"background-color: {CARD_BG}; color: white; padding: 4px; border: 1px solid #3D4047; border-radius: 4px;")
        self.date_start.dateChanged.connect(self.filter_table)
        filter_layout.addWidget(self.date_start)
        
        filter_layout.addWidget(QLabel("to"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addDays(1))
        self.date_end.setStyleSheet(f"background-color: {CARD_BG}; color: white; padding: 4px; border: 1px solid #3D4047; border-radius: 4px;")
        self.date_end.dateChanged.connect(self.filter_table)
        filter_layout.addWidget(self.date_end)
        
        filter_layout.addStretch()
        layout.addWidget(filter_box)
        
        # --- SPLITTER: TABLE TOP, EDITOR BOTTOM ---
        splitter = QSplitter(Qt.Vertical)
        
        # TABLE PANEL
        table_container = QWidget()
        tc_layout = QVBoxLayout(table_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.headers = ["ID", "Date", "Symbol", "Signal", "Entry", "Exit", "P/L %", "Result", "Strategy", "Emotion Tag", "Trade Reason", "Notes", "Entry Screenshot", "Exit Screenshot"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 6px; border: 1px solid #3D4047; color: #FFF; gridline-color: #2E313A;")
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        tc_layout.addWidget(self.table)
        splitter.addWidget(table_container)
        
        # ANNOTATIONS & JOURNAL EDITOR PANEL
        self.editor_box = QGroupBox("Trade Journal Annotations (Select a completed trade above)")
        self.editor_box.setStyleSheet("QGroupBox { border: 1px solid #2196F3; border-radius: 6px; font-weight: bold; color: #FFF; padding: 12px; }")
        editor_layout = QVBoxLayout(self.editor_box)
        editor_layout.setSpacing(10)
        
        self.lbl_no_selection = QLabel("No Data - Please select a completed trade from the table above to view or modify journal annotations.")
        self.lbl_no_selection.setStyleSheet("color: #888; font-size: 15px; font-weight: bold; padding: 20px;")
        self.lbl_no_selection.setAlignment(Qt.AlignCenter)
        editor_layout.addWidget(self.lbl_no_selection)
        
        self.editor_widget = QWidget()
        ed_grid = QGridLayout(self.editor_widget)
        ed_grid.setSpacing(10)
        
        ed_grid.addWidget(QLabel("Selected Trade:"), 0, 0)
        self.lbl_editor_trade = QLabel("None")
        self.lbl_editor_trade.setStyleSheet("color: #2196F3; font-size: 15px; font-weight: bold;")
        ed_grid.addWidget(self.lbl_editor_trade, 0, 1)
        
        ed_grid.addWidget(QLabel("Strategy Tag:"), 0, 2)
        self.edit_strategy = QLineEdit()
        self.edit_strategy.setStyleSheet("background-color: #1A1C22; color: #FFF; border: 1px solid #3D4047; padding: 6px; border-radius: 4px;")
        self.edit_strategy.setPlaceholderText("e.g. SWING, INTRADAY, BREAKOUT (No Data)")
        ed_grid.addWidget(self.edit_strategy, 0, 3)
        
        ed_grid.addWidget(QLabel("Emotion Tag:"), 0, 4)
        self.combo_emotion = QComboBox()
        self.combo_emotion.addItems(["No Data", "Disciplined", "Confident", "Patient", "FOMO", "Hesitant", "Anxious", "Greedy", "Revenge Trade"])
        self.combo_emotion.setStyleSheet("background-color: #1A1C22; color: #FFF; border: 1px solid #3D4047; padding: 5px; border-radius: 4px;")
        ed_grid.addWidget(self.combo_emotion, 0, 5)
        
        ed_grid.addWidget(QLabel("Trade Reason:"), 1, 0)
        self.edit_reason = QLineEdit()
        self.edit_reason.setStyleSheet("background-color: #1A1C22; color: #FFF; border: 1px solid #3D4047; padding: 6px; border-radius: 4px;")
        self.edit_reason.setPlaceholderText("Enter the technical setup or rationale behind entering this trade (No Data)")
        ed_grid.addWidget(self.edit_reason, 1, 1, 1, 5)
        
        ed_grid.addWidget(QLabel("Notes / Review:"), 2, 0)
        self.edit_notes = QTextEdit()
        self.edit_notes.setMaximumHeight(70)
        self.edit_notes.setStyleSheet("background-color: #1A1C22; color: #FFF; border: 1px solid #3D4047; padding: 6px; border-radius: 4px;")
        self.edit_notes.setPlaceholderText("Record post-trade reflections, lessons learned, or management notes (No Data)")
        ed_grid.addWidget(self.edit_notes, 2, 1, 1, 5)
        
        # Screenshots row
        ed_grid.addWidget(QLabel("Entry Screenshot:"), 3, 0)
        self.edit_entry_img = QLineEdit()
        self.edit_entry_img.setReadOnly(True)
        self.edit_entry_img.setStyleSheet("background-color: #1A1C22; color: #AAA; border: 1px solid #3D4047; padding: 5px; border-radius: 4px;")
        self.edit_entry_img.setPlaceholderText("No Screenshot Available (No Data)")
        ed_grid.addWidget(self.edit_entry_img, 3, 1, 1, 2)
        
        btn_browse_entry = QPushButton("Browse...")
        btn_browse_entry.setStyleSheet("background-color: #2C303B; color: #FFF; padding: 5px; border: 1px solid #4E525E; border-radius: 4px;")
        btn_browse_entry.clicked.connect(lambda: self.browse_screenshot("entry"))
        ed_grid.addWidget(btn_browse_entry, 3, 3)
        
        btn_view_entry = QPushButton("View")
        btn_view_entry.setStyleSheet("background-color: #2196F3; color: #FFF; padding: 5px; border-radius: 4px;")
        btn_view_entry.clicked.connect(lambda: self.view_screenshot(self.edit_entry_img.text()))
        ed_grid.addWidget(btn_view_entry, 3, 4)
        
        ed_grid.addWidget(QLabel("Exit Screenshot:"), 4, 0)
        self.edit_exit_img = QLineEdit()
        self.edit_exit_img.setReadOnly(True)
        self.edit_exit_img.setStyleSheet("background-color: #1A1C22; color: #AAA; border: 1px solid #3D4047; padding: 5px; border-radius: 4px;")
        self.edit_exit_img.setPlaceholderText("No Screenshot Available (No Data)")
        ed_grid.addWidget(self.edit_exit_img, 4, 1, 1, 2)
        
        btn_browse_exit = QPushButton("Browse...")
        btn_browse_exit.setStyleSheet("background-color: #2C303B; color: #FFF; padding: 5px; border: 1px solid #4E525E; border-radius: 4px;")
        btn_browse_exit.clicked.connect(lambda: self.browse_screenshot("exit"))
        ed_grid.addWidget(btn_browse_exit, 4, 3)
        
        btn_view_exit = QPushButton("View")
        btn_view_exit.setStyleSheet("background-color: #2196F3; color: #FFF; padding: 5px; border-radius: 4px;")
        btn_view_exit.clicked.connect(lambda: self.view_screenshot(self.edit_exit_img.text()))
        ed_grid.addWidget(btn_view_exit, 4, 4)
        
        btn_save = QPushButton("Save Journal Annotations")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 20px; border-radius: 4px; font-size: 14px;")
        btn_save.clicked.connect(self.save_current_annotations)
        ed_grid.addWidget(btn_save, 5, 0, 1, 6, Qt.AlignRight)
        
        self.editor_widget.hide()
        editor_layout.addWidget(self.editor_widget)
        
        splitter.addWidget(self.editor_box)
        splitter.setSizes([450, 260])
        layout.addWidget(splitter)
        
        self.load_data()

    def _load_annotations(self):
        if not os.path.exists(ANNOTATIONS_FILE):
            os.makedirs(os.path.dirname(ANNOTATIONS_FILE), exist_ok=True)
            return {}
        try:
            with open(ANNOTATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_annotations_to_file(self):
        try:
            os.makedirs(os.path.dirname(ANNOTATIONS_FILE), exist_ok=True)
            with open(ANNOTATIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.annotations, f, indent=4)
        except Exception as e:
            print("Failed to save annotations:", e)

    def create_summary_card(self, title, value, parent_layout):
        card = QFrame()
        card.setStyleSheet(f"background-color: {CARD_BG}; border: 1px solid #3D4047; border-radius: 8px; padding: 8px;")
        l = QVBoxLayout(card)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #A0AAB5; font-size: 13px; border: none;")
        t_lbl.setAlignment(Qt.AlignCenter)
        v_lbl = QLabel(value)
        v_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFF; border: none; margin-top: 5px;")
        v_lbl.setAlignment(Qt.AlignCenter)
        l.addWidget(t_lbl)
        l.addWidget(v_lbl)
        parent_layout.addWidget(card, stretch=1)
        return v_lbl

    def load_data(self):
        try:
            db = DatabaseManager()
            trades = db.get_all_trades()
            self.annotations = self._load_annotations()
            
            self.table.setRowCount(len(trades))
            total = len(trades)
            wins = 0
            losses = 0
            
            unique_strategies = set()
            
            for row, t in enumerate(trades):
                # t = id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category
                _id, date_val, symbol, signal, entry, sl, target, result, return_pct, score, grade, category = t
                tid = str(_id)
                
                if result == "WIN": wins += 1
                elif result == "LOSS": losses += 1
                
                exit_price = "--"
                if result == "WIN": exit_price = str(target)
                elif result == "LOSS": exit_price = str(sl)
                
                ann = self.annotations.get(tid, {})
                strat_tag = ann.get("strategy", category if category and category != "N/A" else "No Data")
                emotion_tag = ann.get("emotion", "No Data")
                reason_tag = ann.get("reason", "No Data")
                notes_tag = ann.get("notes", "No Data")
                entry_img = ann.get("entry_screenshot", "No Data")
                exit_img = ann.get("exit_screenshot", "No Data")
                
                if strat_tag and strat_tag != "No Data":
                    unique_strategies.add(str(strat_tag))

                def mk(val, color=None, align=Qt.AlignCenter):
                    it = QTableWidgetItem(str(val))
                    it.setTextAlignment(align)
                    if color: it.setForeground(QBrush(QColor(color)))
                    return it

                self.table.setItem(row, 0, mk(tid, color="#888"))
                self.table.setItem(row, 1, mk(date_val))
                self.table.setItem(row, 2, mk(symbol, color="#FFF", align=Qt.AlignLeft|Qt.AlignVCenter))
                
                sig_col = "#4CAF50" if signal == "BUY" else "#F44336"
                self.table.setItem(row, 3, mk(signal, color=sig_col))
                self.table.setItem(row, 4, mk(entry))
                self.table.setItem(row, 5, mk(exit_price))
                
                ret_col = "#4CAF50" if str(return_pct).startswith("+") else ("#F44336" if str(return_pct).startswith("-") else "#FFF")
                self.table.setItem(row, 6, mk(return_pct, color=ret_col))
                
                res_col = "#4CAF50" if result=="WIN" else ("#F44336" if result=="LOSS" else "#FF9800")
                self.table.setItem(row, 7, mk(result, color=res_col))
                
                self.table.setItem(row, 8, mk(strat_tag, color="#2196F3" if strat_tag != "No Data" else "#A0AAB5"))
                self.table.setItem(row, 9, mk(emotion_tag, color="#FF9800" if emotion_tag != "No Data" else "#A0AAB5"))
                self.table.setItem(row, 10, mk(reason_tag, align=Qt.AlignLeft|Qt.AlignVCenter, color="#FFF" if reason_tag != "No Data" else "#A0AAB5"))
                self.table.setItem(row, 11, mk(notes_tag, align=Qt.AlignLeft|Qt.AlignVCenter, color="#FFF" if notes_tag != "No Data" else "#A0AAB5"))
                self.table.setItem(row, 12, mk(entry_img, align=Qt.AlignLeft|Qt.AlignVCenter, color="#AAA"))
                self.table.setItem(row, 13, mk(exit_img, align=Qt.AlignLeft|Qt.AlignVCenter, color="#AAA"))

            # Update strategy combo box items without losing current selection
            current_strat = self.combo_strategy.currentText()
            self.combo_strategy.blockSignals(True)
            self.combo_strategy.clear()
            self.combo_strategy.addItem("All Strategies")
            for st in sorted(unique_strategies):
                self.combo_strategy.addItem(st)
            if current_strat in [self.combo_strategy.itemText(i) for i in range(self.combo_strategy.count())]:
                self.combo_strategy.setCurrentText(current_strat)
            self.combo_strategy.blockSignals(False)

            # Update summary statistics with "No Data" safety rules
            if total == 0:
                self.lbl_total.setText("No Data")
                self.lbl_wins.setText("No Data")
                self.lbl_losses.setText("No Data")
                self.lbl_winrate.setText("No Data")
            else:
                self.lbl_total.setText(str(total))
                self.lbl_wins.setText(str(wins))
                self.lbl_losses.setText(str(losses))
                completed = wins + losses
                win_rate = (wins / completed * 100.0) if completed > 0 else 0.0
                self.lbl_winrate.setText(f"{win_rate:.1f}%")
                
            self.table.resizeColumnsToContents()
            self.filter_table()
            
        except Exception as e:
            print("Error loading journal data:", e)

    def on_row_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            self.selected_trade_id = None
            self.lbl_no_selection.show()
            self.editor_widget.hide()
            return
            
        row = selected[0].row()
        tid_item = self.table.item(row, 0)
        sym_item = self.table.item(row, 2)
        res_item = self.table.item(row, 7)
        if not tid_item: return
        
        self.selected_trade_id = tid_item.text()
        self.lbl_editor_trade.setText(f"Trade #{self.selected_trade_id} — {sym_item.text() if sym_item else ''} [{res_item.text() if res_item else ''}]")
        
        ann = self.annotations.get(self.selected_trade_id, {})
        strat_cell = self.table.item(row, 8)
        
        strat_val = ann.get("strategy", strat_cell.text() if strat_cell and strat_cell.text() != "No Data" else "")
        self.edit_strategy.setText(strat_val if strat_val != "No Data" else "")
        
        emotion_val = ann.get("emotion", "No Data")
        if emotion_val in [self.combo_emotion.itemText(i) for i in range(self.combo_emotion.count())]:
            self.combo_emotion.setCurrentText(emotion_val)
        else:
            self.combo_emotion.setCurrentText("No Data")
            
        reason_val = ann.get("reason", "")
        self.edit_reason.setText(reason_val if reason_val != "No Data" else "")
        
        notes_val = ann.get("notes", "")
        self.edit_notes.setPlainText(notes_val if notes_val != "No Data" else "")
        
        entry_img = ann.get("entry_screenshot", "")
        self.edit_entry_img.setText(entry_img if entry_img != "No Data" else "")
        
        exit_img = ann.get("exit_screenshot", "")
        self.edit_exit_img.setText(exit_img if exit_img != "No Data" else "")
        
        self.lbl_no_selection.hide()
        self.editor_widget.show()

    def browse_screenshot(self, kind):
        path, _ = QFileDialog.getOpenFileName(self, f"Select {kind.title()} Screenshot", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if path:
            if kind == "entry":
                self.edit_entry_img.setText(path)
            else:
                self.edit_exit_img.setText(path)

    def view_screenshot(self, path):
        if not path or path == "No Data" or not os.path.exists(path):
            QMessageBox.warning(self, "No Screenshot", "No valid screenshot file path is attached or available for this trade.\nDisplaying: 'No Data'")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def save_current_annotations(self):
        if not self.selected_trade_id:
            return
            
        strat = self.edit_strategy.text().strip() or "No Data"
        emotion = self.combo_emotion.currentText()
        reason = self.edit_reason.text().strip() or "No Data"
        notes = self.edit_notes.toPlainText().strip() or "No Data"
        entry_img = self.edit_entry_img.text().strip() or "No Data"
        exit_img = self.edit_exit_img.text().strip() or "No Data"
        
        self.annotations[self.selected_trade_id] = {
            "strategy": strat,
            "emotion": emotion,
            "reason": reason,
            "notes": notes,
            "entry_screenshot": entry_img,
            "exit_screenshot": exit_img
        }
        self._save_annotations_to_file()
        
        # Update current table row directly without resetting selection
        for r in range(self.table.rowCount()):
            item_id = self.table.item(r, 0)
            if item_id and item_id.text() == self.selected_trade_id:
                def upd(col, txt, color=None, align=Qt.AlignCenter):
                    it = self.table.item(r, col)
                    if not it:
                        it = QTableWidgetItem()
                        self.table.setItem(r, col, it)
                    it.setText(str(txt))
                    it.setTextAlignment(align)
                    if color: it.setForeground(QBrush(QColor(color)))

                upd(8, strat, color="#2196F3" if strat != "No Data" else "#A0AAB5")
                upd(9, emotion, color="#FF9800" if emotion != "No Data" else "#A0AAB5")
                upd(10, reason, align=Qt.AlignLeft|Qt.AlignVCenter, color="#FFF" if reason != "No Data" else "#A0AAB5")
                upd(11, notes, align=Qt.AlignLeft|Qt.AlignVCenter, color="#FFF" if notes != "No Data" else "#A0AAB5")
                upd(12, entry_img, align=Qt.AlignLeft|Qt.AlignVCenter, color="#AAA")
                upd(13, exit_img, align=Qt.AlignLeft|Qt.AlignVCenter, color="#AAA")
                break
                
        QMessageBox.information(self, "Annotations Saved", f"Journal notes and annotations for Trade #{self.selected_trade_id} saved successfully.")

    def filter_table(self, *args):
        target_res = self.combo_result.currentText()
        target_sig = self.combo_signal.currentText()
        target_strat = self.combo_strategy.currentText()
        filter_date = self.chk_date.isChecked()
        d_start = self.date_start.date().toPython()
        d_end = self.date_end.date().toPython()
        
        for row in range(self.table.rowCount()):
            item_date = self.table.item(row, 1)
            item_sig = self.table.item(row, 3)
            item_res = self.table.item(row, 7)
            item_strat = self.table.item(row, 8)
            
            show = True
            if target_res != "All Results" and item_res and item_res.text() != target_res:
                show = False
            if target_sig != "All Signals" and item_sig and item_sig.text() != target_sig:
                show = False
            if target_strat != "All Strategies" and item_strat and item_strat.text() != target_strat:
                show = False
                
            if show and filter_date and item_date:
                try:
                    dt_str = item_date.text().split(" ")[0]
                    dt_val = datetime.strptime(dt_str, "%Y-%m-%d").date()
                    if not (d_start <= dt_val <= d_end):
                        show = False
                except Exception:
                    pass

            self.table.setRowHidden(row, not show)

    def export_csv(self):
        default_name = f"trade_journal_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export Trading Journal CSV", default_name, "CSV Files (*.csv)")
        
        if not path:
            return
            
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
                
                exported_count = 0
                for row in range(self.table.rowCount()):
                    if self.table.isRowHidden(row):
                        continue
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        val = item.text() if item else "No Data"
                        row_data.append(val if val else "No Data")
                    writer.writerow(row_data)
                    exported_count += 1
                    
            QMessageBox.information(self, "Export Success", f"Trading Journal exported successfully ({exported_count} trades):\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV file:\n{str(e)}")
