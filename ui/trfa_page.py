from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QMessageBox, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from database.trfa_db import TRFADatabase

class TRFAPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = TRFADatabase()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Trade Replay & Forensic Analysis (TRFA)")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(header)
        
        desc = QLabel("Analyze the root cause of every trade. Review AI-generated forensic reports.")
        desc.setStyleSheet("color: #AAA;")
        layout.addWidget(desc)
        
        self.btn_refresh = QPushButton("Refresh Reports")
        self.btn_refresh.setFixedWidth(150)
        self.btn_refresh.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(self.btn_refresh, alignment=Qt.AlignRight)
        
        # Splitter for Table and Details
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Symbol", "Signal", "Status", "PnL", "Exit Reason", "Root Cause"])
        
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1E2028; color: #FFF; border: 1px solid #3D4047; border-radius: 6px; }
            QTableWidget::item:selected { background-color: #2196F3; color: white; }
            QHeaderView::section { background-color: #2D3039; color: #888; padding: 6px; font-weight: bold; }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.show_details)
        
        splitter.addWidget(self.table)
        
        # Detail View
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setStyleSheet("background-color: #1E2028; color: #FFF; border: 1px solid #3D4047; padding: 10px; font-size: 14px;")
        splitter.addWidget(self.details)
        
        self.load_data()
        
    def load_data(self):
        self.table.setRowCount(0)
        self.reports = self.db.get_recent_reports(50)
        self.table.setRowCount(len(self.reports))
        
        for i, rep in enumerate(self.reports):
            self.table.setItem(i, 0, QTableWidgetItem(rep.get("timestamp", "")[:19]))
            self.table.setItem(i, 1, QTableWidgetItem(rep.get("symbol", "")))
            
            sig_item = QTableWidgetItem(rep.get("signal", ""))
            sig_item.setForeground(QColor("#4CAF50") if rep.get("signal") == "BUY" else QColor("#F44336"))
            self.table.setItem(i, 2, sig_item)
            
            status = rep.get("status", "")
            stat_item = QTableWidgetItem(status)
            stat_item.setForeground(QColor("#4CAF50") if status == "WIN" else QColor("#F44336"))
            self.table.setItem(i, 3, stat_item)
            
            pnl = float(rep.get("pnl", 0))
            pnl_item = QTableWidgetItem(f"{pnl:.2f}")
            pnl_item.setForeground(QColor("#4CAF50") if pnl > 0 else QColor("#F44336"))
            self.table.setItem(i, 4, pnl_item)
            
            self.table.setItem(i, 5, QTableWidgetItem(rep.get("exit_reason", "")))
            self.table.setItem(i, 6, QTableWidgetItem(rep.get("root_cause", "")))
            
    def show_details(self):
        selected = self.table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        rep = self.reports[row]
        
        html = f"""
        <h2 style='color: #64B5F6;'>Forensic Report: {rep.get('symbol')} ({rep.get('status')})</h2>
        <p><b>Timestamp:</b> {rep.get('timestamp')}</p>
        <p><b>Signal:</b> {rep.get('signal')}</p>
        <p><b>PnL:</b> <span style='color: {"#4CAF50" if rep.get("pnl", 0) > 0 else "#F44336"}'>{rep.get('pnl', 0):.2f}</span></p>
        <hr>
        <h3 style='color: #FFB300;'>Root Cause</h3>
        <p>{rep.get('root_cause')}</p>
        <h3 style='color: #4CAF50;'>Explanation</h3>
        <p>{rep.get('explanation')}</p>
        <h3 style='color: #E91E63;'>Recommendation (Manual Review)</h3>
        <p>{rep.get('recommendation')}</p>
        """
        self.details.setHtml(html)
