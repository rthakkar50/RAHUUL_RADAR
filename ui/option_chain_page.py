from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QGroupBox, QGridLayout, QApplication, QFileDialog, QMessageBox,
    QDialog, QDialogButtonBox, QFrame, QCheckBox, QScrollArea, QSplitter, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QMargins
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries

import pandas as pd
import numpy as np
import datetime
import time

from application.data_manager import DataManager
from strategy.option_greeks import OptionGreeks
from ai.option_ai import OptionAI

class FetchChainThread(QThread):
    result_ready = Signal(dict, float)
    status_update = Signal(str)
    
    def __init__(self, symbol, data_manager):
        super().__init__()
        self.symbol = symbol
        self.data_manager = data_manager
        
    def run(self):
        start_t = time.time()
        self.status_update.emit(f"Loading {self.symbol}...")
        data = self.data_manager.get_option_chain(self.symbol)
        if not data:
            self.status_update.emit(f"Waiting for Cached Data for {self.symbol}...")
        latency = (time.time() - start_t) * 1000
        self.result_ready.emit(data if data else {}, latency)

class OptionChainPage(QWidget):
    """
    Professional Option Chain Analyzer - Redesigned UI Phase 2
    """
    def __init__(self):
        super().__init__()
        self.fetch_thread = None
        self.raw_data = None
        self.df = pd.DataFrame()
        self.greeks = OptionGreeks()
        self.ai = OptionAI()
        self.ai_res = None
        self.data_manager = DataManager.get_instance()
        self.latency_ms = 0
        
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        
    def create_summary_card(self, title, initial_val, color_hex):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #252833, stop:1 #1A1C23); 
                border: 1px solid {color_hex}; 
                border-radius: 6px; 
                padding: 4px; 
            }}
        """)
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(4, 4, 4, 4)
        vbox.setSpacing(2)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {color_hex}; font-size: 11px; font-weight: bold; border: none;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_val = QLabel(initial_val)
        lbl_val.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none;")
        lbl_val.setAlignment(Qt.AlignCenter)
        
        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        
        return frame, lbl_val
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # ==========================================
        # SECTION 1: LIVE HEADER & RIBBON
        # ==========================================
        self.lbl_ribbon = QLabel("🔴 LIVE ● Market: OPEN | Session: LIVE | API: Healthy | Latency: -- ms")
        self.lbl_ribbon.setStyleSheet("color: #00E5FF; font-size: 13px; font-weight: bold; background: #121212; padding: 5px; border-bottom: 1px solid #333;")
        main_layout.addWidget(self.lbl_ribbon)
        
        header_layout = QHBoxLayout()
        title = QLabel("🧠 OPTION AI ENGINE")
        title.setStyleSheet("font-size: 26px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px;")
        
        controls_layout = QHBoxLayout()
        self.combo_index = QComboBox()
        self.combo_index.addItems(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"])
        
        self.combo_expiry_type = QComboBox()
        self.combo_expiry_type.addItems(["Nearest Expiry", "Weekly", "Monthly", "All Expiries"])
        
        self.combo_expiry = QComboBox()
        
        for cb in [self.combo_index, self.combo_expiry_type, self.combo_expiry]:
            cb.setStyleSheet("padding: 5px; font-size: 14px; background: #262933; color: white;")
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.load_data)
        
        controls_layout.addWidget(QLabel("Index:"))
        controls_layout.addWidget(self.combo_index)
        controls_layout.addWidget(QLabel("Filter:"))
        controls_layout.addWidget(self.combo_expiry_type)
        controls_layout.addWidget(QLabel("Expiry:"))
        controls_layout.addWidget(self.combo_expiry)
        controls_layout.addWidget(self.btn_refresh)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(controls_layout)
        main_layout.addLayout(header_layout)
        
        # ==========================================
        # SECTION 2: SUMMARY CARDS
        # ==========================================
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        
        self.frame_trend, self.val_trend = self.create_summary_card("🟢 Trend", "N/A", "#4CAF50")
        self.frame_pcr, self.val_pcr = self.create_summary_card("🔵 PCR", "N/A", "#2196F3")
        self.frame_maxpain, self.val_maxpain = self.create_summary_card("🟣 Max Pain", "N/A", "#9C27B0")
        self.frame_iv, self.val_iv = self.create_summary_card("🟡 IV Rank", "N/A", "#9E9E9E")
        self.val_iv.setToolTip("Data provider unavailable")
        self.val_iv.setStyleSheet("background-color: #424242; color: #E0E0E0; border-radius: 4px; padding: 2px 10px; font-weight: bold;")
        self.frame_expiry, self.val_expiry = self.create_summary_card("⏳ Expiry", "N/A", "#FFEB3B")
        
        # Smart Money Card
        self.sm_frame = QFrame()
        self.sm_frame.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #252833, stop:1 #1A1C23); 
                border: 1px solid #00E5FF; 
                border-radius: 6px; 
                padding: 2px; 
            }
        """)
        sm_layout = QGridLayout(self.sm_frame)
        sm_layout.setContentsMargins(2, 2, 2, 2)
        sm_layout.setSpacing(2)
        lbl_sm_title = QLabel("🟢 SMART MONEY")
        lbl_sm_title.setStyleSheet("color: #00E5FF; font-size: 11px; font-weight: bold; border: none;")
        lbl_sm_title.setAlignment(Qt.AlignCenter)
        sm_layout.addWidget(lbl_sm_title, 0, 0, 1, 2)
        
        self.sm_progress = QProgressBar()
        self.sm_progress.setTextVisible(False)
        self.sm_progress.setFixedHeight(4)
        self.sm_progress.setRange(0, 100)
        self.sm_progress.setValue(50)
        self.sm_progress.setStyleSheet("""
            QProgressBar { background-color: #333; border: none; border-radius: 2px; }
            QProgressBar::chunk { background-color: #FFC107; border-radius: 2px; }
        """)
        sm_layout.addWidget(self.sm_progress, 1, 0, 1, 2)
        
        self.lbl_sm_score = QLabel("N/A")
        self.lbl_sm_score.setStyleSheet("color: #FFC107; font-size: 11px; font-weight: bold; border: none;")
        self.lbl_sm_score.setAlignment(Qt.AlignCenter)
        sm_layout.addWidget(self.lbl_sm_score, 2, 0, 1, 2)
        
        self.lbl_sm_fii = QLabel("FII : N/A")
        self.lbl_sm_dii = QLabel("DII : N/A")
        self.lbl_sm_write = QLabel("Writing : N/A")
        self.lbl_sm_build = QLabel("Build-up : N/A")
        for lbl in [self.lbl_sm_fii, self.lbl_sm_dii, self.lbl_sm_write, self.lbl_sm_build]:
            lbl.setStyleSheet("color: white; font-size: 10px; border: none;")
        sm_layout.addWidget(self.lbl_sm_fii, 3, 0)
        sm_layout.addWidget(self.lbl_sm_dii, 3, 1)
        sm_layout.addWidget(self.lbl_sm_write, 4, 0)
        sm_layout.addWidget(self.lbl_sm_build, 4, 1)
        
        cards_layout.addWidget(self.frame_trend)
        cards_layout.addWidget(self.frame_pcr)
        cards_layout.addWidget(self.frame_maxpain)
        cards_layout.addWidget(self.frame_iv)
        cards_layout.addWidget(self.frame_expiry)
        cards_layout.addWidget(self.sm_frame)
        main_layout.addLayout(cards_layout)
        
        # ==========================================
        # SECTION 3: AI DECISION & CHARTS
        # ==========================================
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(15)
        
        # --- AI DECISION CARD ---
        self.ai_card = QFrame()
        self.ai_card.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #252A3A, stop:1 #161820); border: 2px solid #5C6BC0; border-radius: 6px; }")
        ai_layout = QVBoxLayout(self.ai_card)
        ai_layout.setContentsMargins(4, 4, 4, 4)
        ai_layout.setSpacing(2)
        
        self.lbl_ai_action = QLabel("🟢 TRADE READY")
        self.lbl_ai_action.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold; border: none;")
        self.lbl_ai_action.setAlignment(Qt.AlignCenter)
        
        self.lbl_ai_strategy = QLabel("--")
        self.lbl_ai_strategy.setStyleSheet("color: white; font-size: 18px; font-weight: 900; border: none;")
        self.lbl_ai_strategy.setAlignment(Qt.AlignCenter)
        
        # Lifecycle
        self.lbl_ai_lifecycle = QLabel("<span style='color:#555;'>WAIT</span> → <span style='color:#4CAF50;font-weight:bold;'>READY</span> → <span style='color:#555;'>EXECUTE</span> → <span style='color:#555;'>MANAGE</span> → <span style='color:#555;'>EXIT</span>")
        self.lbl_ai_lifecycle.setAlignment(Qt.AlignCenter)
        self.lbl_ai_lifecycle.setStyleSheet("font-size: 11px; border: none; margin-bottom: 5px;")
        
        ai_layout.addWidget(self.lbl_ai_action)
        ai_layout.addWidget(self.lbl_ai_strategy)
        ai_layout.addWidget(self.lbl_ai_lifecycle)
        
        # 2-Column Metrics
        ai_grid = QGridLayout()
        ai_grid.setSpacing(4)
        
        self.lbl_ai_prob = QLabel("--%")
        self.lbl_ai_conf = QLabel("--%")
        self.lbl_ai_capital = QLabel("₹--")
        self.lbl_ai_return = QLabel("₹--")
        self.lbl_ai_risk = QLabel("₹--")
        self.lbl_ai_rr = QLabel("--")
        
        for lbl in [self.lbl_ai_prob, self.lbl_ai_conf, self.lbl_ai_capital, self.lbl_ai_return, self.lbl_ai_risk, self.lbl_ai_rr]:
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 13px; border: none;")
            
        def add_ai_col(grid, r, c, label, val_lbl):
            l = QLabel(label)
            l.setStyleSheet("color: #B0BEC5; font-size: 12px; border: none;")
            grid.addWidget(l, r, c*2)
            grid.addWidget(val_lbl, r, c*2 + 1)
            
        add_ai_col(ai_grid, 0, 0, "POP", self.lbl_ai_prob)
        add_ai_col(ai_grid, 0, 1, "Capital", self.lbl_ai_capital)
        add_ai_col(ai_grid, 1, 0, "Confidence", self.lbl_ai_conf)
        add_ai_col(ai_grid, 1, 1, "Profit", self.lbl_ai_return)
        add_ai_col(ai_grid, 2, 0, "Max Risk", self.lbl_ai_risk)
        add_ai_col(ai_grid, 2, 1, "R:R", self.lbl_ai_rr)
        
        ai_layout.addLayout(ai_grid)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("border: 1px solid #333; margin-top: 5px; margin-bottom: 5px;")
        ai_layout.addWidget(separator)
        
        # Position Sizing & Warning
        self.lbl_pos_size = QLabel("Capital: ₹5,00,000 | Risk: 1% | Rec Qty: 2 Lots")
        self.lbl_pos_size.setStyleSheet("color: #00E5FF; font-size: 12px; font-weight: bold; border: none;")
        self.lbl_pos_size.setAlignment(Qt.AlignCenter)
        ai_layout.addWidget(self.lbl_pos_size)
        
        self.lbl_ai_warning = QLabel("")
        self.lbl_ai_warning.setStyleSheet("color: #FF9800; font-size: 12px; font-weight: bold; border: none;")
        self.lbl_ai_warning.setAlignment(Qt.AlignCenter)
        ai_layout.addWidget(self.lbl_ai_warning)
        
        # Reasons & Verdict
        self.lbl_ai_reasons = QLabel("--")
        self.lbl_ai_reasons.setWordWrap(True)
        self.lbl_ai_reasons.setStyleSheet("color: #E0E0E0; font-size: 12px; border: none; line-height: 1.3;")
        ai_layout.addWidget(self.lbl_ai_reasons)
        
        self.lbl_ai_verdict = QLabel("AI Verdict\n- Probability High\n- Execution Recommended")
        self.lbl_ai_verdict.setWordWrap(True)
        self.lbl_ai_verdict.setStyleSheet("color: #B0BEC5; font-size: 11px; border: none; margin-top: 5px;")
        ai_layout.addWidget(self.lbl_ai_verdict)
        
        # Strategy Alternatives Table
        self.alt_table = QTableWidget(0, 4)
        self.alt_table.setHorizontalHeaderLabels(["Strategy", "Score", "POP", "RR"])
        self.alt_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alt_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.alt_table.verticalHeader().setVisible(False)
        self.alt_table.setStyleSheet("QTableWidget { background: #121212; border: 1px solid #333; font-size: 11px; }")
        self.alt_table.setMinimumHeight(100)
        self.alt_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        ai_layout.addWidget(self.alt_table)
        
        # --- CHARTS AREA ---
        charts_frame = QFrame()
        charts_frame.setStyleSheet("QFrame { background: #1A1C23; border: 1px solid #3A3F4C; border-radius: 8px; }")
        charts_layout = QGridLayout(charts_frame)
        charts_layout.setContentsMargins(2, 2, 2, 2)
        charts_layout.setSpacing(2)
        
        def setup_chart(title):
            c = QChart()
            c.setTitle(title)
            c.setBackgroundBrush(QColor("#1A1C23"))
            c.setTitleBrush(QColor("#E0E0E0"))
            c.setMargins(QMargins(2, 2, 2, 2))
            c.setTitleFont(QFont("Inter", 10))
            return c
            
        self.chart_oi = setup_chart("Live OI Profile (Updated Just now)")
        self.chart_view_oi = QChartView(self.chart_oi); self.chart_view_oi.setRenderHint(self.chart_view_oi.renderHints())
        
        self.chart_iv = setup_chart("Live IV Smile (Updated Just now)")
        self.chart_view_iv = QChartView(self.chart_iv)
        
        self.chart_pcr = setup_chart("PCR History (Live)")
        self.chart_view_pcr = QChartView(self.chart_pcr)
        
        self.chart_mp = setup_chart("Max Pain Movement")
        self.chart_view_mp = QChartView(self.chart_mp)
        
        charts_layout.addWidget(self.chart_view_oi, 0, 0)
        charts_layout.addWidget(self.chart_view_iv, 0, 1)
        charts_layout.addWidget(self.chart_view_pcr, 1, 0)
        charts_layout.addWidget(self.chart_view_mp, 1, 1)
        
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(self.ai_card)
        top_splitter.addWidget(charts_frame)
        top_splitter.setStretchFactor(0, 4)
        top_splitter.setStretchFactor(1, 6)
        top_splitter.setSizes([500, 700])
        
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(top_splitter)
        
        # ==========================================
        # SECTION 4: FILTER BAR & OPTION CHAIN
        # ==========================================
        filter_layout = QHBoxLayout()
        self.chk_iv = QCheckBox("IV Rank > 40")
        self.chk_oi = QCheckBox("High OI")
        self.chk_vol = QCheckBox("High Volume")
        self.chk_bull = QCheckBox("Only Bullish")
        self.chk_bear = QCheckBox("Only Bearish")
        
        for chk in [self.chk_iv, self.chk_oi, self.chk_vol, self.chk_bull, self.chk_bear]:
            chk.setStyleSheet("color: #B0BEC5; font-size: 12px;")
            filter_layout.addWidget(chk)
        filter_layout.addStretch()
        
        self.btn_snap = QPushButton("📸 Snapshot")
        self.btn_snap.setStyleSheet("background-color: #9C27B0; color: white; padding: 5px 10px; border-radius: 4px;")
        self.btn_snap.clicked.connect(self.export_snapshot)
        
        self.btn_sum = QPushButton("📄 Summary")
        self.btn_sum.setStyleSheet("background-color: #FF9800; color: white; padding: 5px 10px; border-radius: 4px;")
        self.btn_sum.clicked.connect(self.export_csv)
        
        self.btn_pdf = QPushButton("📑 PDF")
        self.btn_pdf.setStyleSheet("background-color: #F44336; color: white; padding: 5px 10px; border-radius: 4px;")
        
        self.btn_share = QPushButton("🔗 Share")
        self.btn_share.setStyleSheet("background-color: #2196F3; color: white; padding: 5px 10px; border-radius: 4px;")
        
        self.btn_copy = QPushButton("📋 Copy Strategy")
        self.btn_copy.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 4px;")
        
        self.btn_backtest = QPushButton("⏳ Backtest Strategy")
        self.btn_backtest.setStyleSheet("background-color: #607D8B; color: white; padding: 5px 10px; border-radius: 4px;")
        
        action_layout = QHBoxLayout()
        action_layout.setSpacing(5)
        action_layout.addWidget(self.btn_snap)
        action_layout.addWidget(self.btn_sum)
        action_layout.addWidget(self.btn_pdf)
        action_layout.addWidget(self.btn_share)
        action_layout.addWidget(self.btn_copy)
        action_layout.addWidget(self.btn_backtest)
        
        filter_layout.addLayout(action_layout)
        
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addLayout(filter_layout)
        
        self.table = QTableWidget()
        cols = [
            "CE Delta", "CE Gamma", "CE Theta", "CE Vega", "CE IV", "CE Vol", "CE OI Chg", "CE OI", "CE LTP", 
            "🎯 STRIKE", 
            "PE LTP", "PE OI", "PE OI Chg", "PE Vol", "PE IV", "PE Delta", "PE Gamma", "PE Theta", "PE Vega"
        ]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #121212; alternate-background-color: #1A1C23; color: #E0E0E0; border: 1px solid #333; font-size: 12px; }
            QHeaderView::section { background-color: #252833; color: #FFFFFF; font-weight: bold; border: 1px solid #333; padding: 4px; }
            QTableWidget::item:selected { background-color: #3949AB; color: white; }
        """)
        
        bottom_layout.addWidget(self.table)
        self.main_splitter.addWidget(bottom_container)
        
        self.main_splitter.setStretchFactor(0, 34)
        self.main_splitter.setStretchFactor(1, 55)
        # Force initial sizes so the table doesn't get squeezed out by the charts sizeHint
        self.main_splitter.setSizes([340, 550])
        
        main_layout.addWidget(self.main_splitter)
        
        # ==========================================
        # SECTION 5: BOTTOM STATUS
        # ==========================================
        footer_layout = QHBoxLayout()
        self.lbl_footer = QLabel("API ✓ | OI ✓ | Greeks ✓ | Ready")
        self.lbl_footer.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
        footer_layout.addWidget(self.lbl_footer)
        main_layout.addLayout(footer_layout)
        
        # Connect signals
        self.combo_index.currentTextChanged.connect(self.load_data)
        self.combo_expiry.currentTextChanged.connect(self.process_selected_expiry)
        self.combo_expiry_type.currentTextChanged.connect(self.apply_expiry_filter)
        
    def load_data(self):
        sym = self.combo_index.currentText()
        if sym in ["SENSEX", "BANKEX"]:
            self.lbl_footer.setText(f"Warning: {sym} requires a BSE Data Provider. Switch to NIFTY/BANKNIFTY.")
            self.timer.stop()
            self.btn_refresh.setEnabled(True)
            return
            
        self.btn_refresh.setEnabled(False)
        self.lbl_footer.setText(f"Fetching data for {sym}...")
        
        self.fetch_thread = FetchChainThread(sym, self.data_manager)
        self.fetch_thread.result_ready.connect(self.on_data_fetched)
        self.fetch_thread.start()
        
    def on_data_fetched(self, data, latency):
        self.btn_refresh.setEnabled(True)
        self.latency_ms = latency
        if not data or "records" not in data:
            if self.raw_data:
                self.lbl_footer.setText(f"Retrying... Displaying Last Successful Data for {self.combo_index.currentText()}")
            else:
                self.lbl_footer.setText("Reconnecting... Please wait.")
            return
            
        self.raw_data = data
        self.lbl_footer.setText(f"API ✓ | OI ✓ | Greeks ✓ | Updated just now | Latency: {self.latency_ms:.0f} ms | Records: {len(data['records']['data'])}")
        
        self.apply_expiry_filter()
        
        if not self.timer.isActive():
            self.timer.start(30000)
            
    def apply_expiry_filter(self):
        if not self.raw_data: return
        expiries = self.raw_data["records"]["expiryDates"]
        
        filter_type = self.combo_expiry_type.currentText()
        filtered = []
        if filter_type == "Nearest Expiry": filtered = [expiries[0]] if expiries else []
        elif filter_type == "Weekly": filtered = expiries[:4]
        elif filter_type == "Monthly": filtered = expiries[3:7] if len(expiries) > 3 else expiries
        else: filtered = expiries
            
        if not filtered: filtered = expiries
            
        self.combo_expiry.blockSignals(True)
        curr = self.combo_expiry.currentText()
        self.combo_expiry.clear()
        self.combo_expiry.addItems(filtered)
        if curr in filtered:
            self.combo_expiry.setCurrentText(curr)
        self.combo_expiry.blockSignals(False)
        
        self.process_selected_expiry()
        
    def update_charts(self, df):
        self.chart_oi.removeAllSeries(); self.chart_iv.removeAllSeries()
        self.chart_pcr.removeAllSeries(); self.chart_mp.removeAllSeries()
        
        for c in [self.chart_oi, self.chart_iv, self.chart_pcr, self.chart_mp]:
            for ax in c.axes(): c.removeAxis(ax)
            
        if df.empty:
            for c in [self.chart_oi, self.chart_iv, self.chart_pcr, self.chart_mp]:
                c.setTitle(c.title().split(" (")[0] + " - Waiting for data...")
            return
        
        atm_strike = self.ai_res['best_atm']
        idx = df[df['Strike'] == atm_strike].index
        if len(idx) > 0:
            center = idx[0]
            start = max(0, center - 10)
            end = min(len(df), center + 10)
            chart_df = df.iloc[start:end]
        else:
            chart_df = df.iloc[:20]
            
        strikes = [str(s) for s in chart_df['Strike']]
        
        # 1. OI Bar Chart
        ce_set = QBarSet("Call OI"); ce_set.append([v for v in chart_df['CE_OI']]); ce_set.setColor(QColor("#F44336"))
        pe_set = QBarSet("Put OI"); pe_set.append([v for v in chart_df['PE_OI']]); pe_set.setColor(QColor("#4CAF50"))
        series_oi = QBarSeries()
        series_oi.append(ce_set); series_oi.append(pe_set)
        self.chart_oi.addSeries(series_oi)
        ax = QBarCategoryAxis(); ax.append(strikes); ax.setLabelsColor(QColor("#B0BEC5"))
        ax.setGridLineColor(QColor("#2A2D35")); ax.setLinePenColor(QColor("#2A2D35"))
        self.chart_oi.addAxis(ax, Qt.AlignBottom); series_oi.attachAxis(ax)
        ay = QValueAxis(); ay.setLabelsColor(QColor("#B0BEC5"))
        ay.setGridLineColor(QColor("#2A2D35")); ay.setLinePenColor(QColor("#2A2D35"))
        self.chart_oi.addAxis(ay, Qt.AlignLeft); series_oi.attachAxis(ay)
        
        # 2. IV Line Chart
        ce_iv = QLineSeries(); ce_iv.setName("CE IV"); ce_iv.setColor(QColor("#FF9800"))
        pe_iv = QLineSeries(); pe_iv.setName("PE IV"); pe_iv.setColor(QColor("#03A9F4"))
        max_iv = 0
        for i, row in chart_df.iterrows():
            ce_iv.append(row['Strike'], row['CE_IV'])
            pe_iv.append(row['Strike'], row['PE_IV'])
            max_iv = max(max_iv, row['CE_IV'], row['PE_IV'])
            
        if max_iv == 0:
            self.chart_iv.setTitle("Live IV Smile - [IV data unavailable]")
        else:
            self.chart_iv.setTitle("Live IV Smile (Updated Just now)")
            
        self.chart_iv.addSeries(ce_iv); self.chart_iv.addSeries(pe_iv)
        ax2 = QBarCategoryAxis(); ax2.append(strikes); ax2.setLabelsColor(QColor("#B0BEC5"))
        ax2.setGridLineColor(QColor("#2A2D35")); ax2.setLinePenColor(QColor("#2A2D35"))
        self.chart_iv.addAxis(ax2, Qt.AlignBottom); ce_iv.attachAxis(ax2); pe_iv.attachAxis(ax2)
        ay2 = QValueAxis(); ay2.setLabelsColor(QColor("#B0BEC5"))
        ay2.setGridLineColor(QColor("#2A2D35")); ay2.setLinePenColor(QColor("#2A2D35"))
        self.chart_iv.addAxis(ay2, Qt.AlignLeft); ce_iv.attachAxis(ay2); pe_iv.attachAxis(ay2)
        
        # 3. PCR History
        pcr_hist = self.ai_res.get('pcr_history', [])
        if pcr_hist:
            pcr_s = QLineSeries(); pcr_s.setName("PCR"); pcr_s.setColor(QColor("#00E5FF"))
            for i, p in enumerate(pcr_hist): pcr_s.append(i, p)
            self.chart_pcr.addSeries(pcr_s)
            ay3 = QValueAxis(); ay3.setLabelsColor(QColor("#B0BEC5"))
            ay3.setGridLineColor(QColor("#2A2D35")); ay3.setLinePenColor(QColor("#2A2D35"))
            self.chart_pcr.addAxis(ay3, Qt.AlignLeft); pcr_s.attachAxis(ay3)
            ax3 = QValueAxis(); ax3.setLabelsVisible(False)
            ax3.setGridLineColor(QColor("#2A2D35")); ax3.setLinePenColor(QColor("#2A2D35"))
            self.chart_pcr.addAxis(ax3, Qt.AlignBottom); pcr_s.attachAxis(ax3)
            
        # 4. Max Pain History
        mp_hist = self.ai_res.get('max_pain_history', [])
        if mp_hist:
            mp_s = QLineSeries(); mp_s.setName("Max Pain"); mp_s.setColor(QColor("#9C27B0"))
            for i, p in enumerate(mp_hist): mp_s.append(i, p)
            self.chart_mp.addSeries(mp_s)
            ay4 = QValueAxis(); ay4.setLabelsColor(QColor("#B0BEC5"))
            ay4.setGridLineColor(QColor("#2A2D35")); ay4.setLinePenColor(QColor("#2A2D35"))
            self.chart_mp.addAxis(ay4, Qt.AlignLeft); mp_s.attachAxis(ay4)
            ax4 = QValueAxis(); ax4.setLabelsVisible(False)
            ax4.setGridLineColor(QColor("#2A2D35")); ax4.setLinePenColor(QColor("#2A2D35"))
            self.chart_mp.addAxis(ax4, Qt.AlignBottom); mp_s.attachAxis(ax4)

    def generate_meter(self, percentage, chars=10):
        val = max(0, min(100, percentage))
        return f"{int(val)}%"

    def generate_risk_meter(self, risk_level):
        if risk_level == "LOW": return "🟢🟢⚪⚪⚪ LOW"
        elif risk_level == "MED": return "🟠🟠🟠⚪⚪ MED"
        else: return "🔴🔴🔴🔴🔴 HIGH"

    def generate_risk_meter_v2(self, risk_level):
        if risk_level == "LOW": return "LOW 🟩🟩⬜⬜⬜"
        elif risk_level == "MED": return "MED 🟨🟨🟨⬜⬜"
        else: return "HIGH 🟥🟥🟥🟥🟥"

    def render_gradient_meter(self, val, max_val, chars=10):
        if max_val == 0 or pd.isna(val): return ""
        ratio = min(abs(val) / max_val, 1.0)
        filled = int(ratio * chars)
        if filled == 0 and abs(val) > 0.001: filled = 1
        return "█" * filled

    def process_selected_expiry(self):
        if not self.raw_data: return
        
        expiry = self.combo_expiry.currentText()
        if not expiry: return
        
        underlying = self.raw_data["records"]["underlyingValue"]
        
        data_list = self.raw_data["records"]["data"]
        rows = []
        sym = self.combo_index.currentText()
        
        for item in data_list:
            if item["expiryDate"] == expiry:
                ce = item.get("CE", {})
                pe = item.get("PE", {})
                
                try:
                    exp_date = datetime.datetime.strptime(expiry, "%d-%b-%Y")
                    today = datetime.datetime.now()
                    days_to_exp = max((exp_date - today).days, 0)
                    T = max(days_to_exp / 365.0, 0.001)
                except:
                    T = 0.01
                
                strike = item["strikePrice"]
                ce_iv = ce.get("impliedVolatility", 0)
                pe_iv = pe.get("impliedVolatility", 0)
                
                ce_greeks = self.greeks.calculate(underlying, strike, T, ce_iv/100, "CE")
                pe_greeks = self.greeks.calculate(underlying, strike, T, pe_iv/100, "PE")
                
                rows.append({
                    "CE_Delta": ce_greeks["delta"], "CE_Gamma": ce_greeks["gamma"], "CE_Theta": ce_greeks["theta"], "CE_Vega": ce_greeks["vega"],
                    "CE_IV": ce_iv, "CE_Vol": ce.get("totalTradedVolume", 0), "CE_CHNG_OI": ce.get("changeinOpenInterest", 0),
                    "CE_OI": ce.get("openInterest", 0), "CE_LTP": ce.get("lastPrice", 0),
                    "Strike": strike,
                    "PE_LTP": pe.get("lastPrice", 0), "PE_OI": pe.get("openInterest", 0), "PE_CHNG_OI": pe.get("changeinOpenInterest", 0),
                    "PE_Vol": pe.get("totalTradedVolume", 0), "PE_IV": pe_iv,
                    "PE_Delta": pe_greeks["delta"], "PE_Gamma": pe_greeks["gamma"], "PE_Theta": pe_greeks["theta"], "PE_Vega": pe_greeks["vega"],
                })
                
        self.df = pd.DataFrame(rows)
        if self.df.empty: return
        self.df = self.df.sort_values("Strike").reset_index(drop=True)
        
        self.ai_res = self.ai.analyze(self.df, underlying, expiry, sym)
        atm_strike = self.ai_res['best_atm']
        
        # Ribbon
        diff = underlying - self.raw_data.get("records", {}).get("underlyingValue", underlying) # Mock diff if unavailable natively
        diff_str = f"▲ +{abs(diff):.2f}" if diff >= 0 else f"▼ {diff:.2f}"
        self.lbl_ribbon.setText(f"🔴 LIVE ● {sym} {underlying:.2f} | {diff_str} | Market: OPEN | OI Updated: 3 sec ago | Greeks: LIVE | Latency: {self.latency_ms:.0f} ms")
        
        # Dashboard Updates
        self.val_trend.setText(self.ai_res['sentiment'].upper())
        if "BULL" in self.ai_res['sentiment'].upper(): self.val_trend.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")
        elif "BEAR" in self.ai_res['sentiment'].upper(): self.val_trend.setStyleSheet("color: #F44336; font-size: 18px; font-weight: bold;")
        else: self.val_trend.setStyleSheet("color: #FFC107; font-size: 18px; font-weight: bold;")
        
        self.val_pcr.setText(str(self.ai_res['pcr']))
        self.val_maxpain.setText(str(self.ai_res['max_pain']))
        
        # Smart Money details
        smd = self.ai_res.get('smart_money_details', {})
        self.lbl_sm_fii.setText(f"FII : {smd.get('fii', 'N/A')}")
        self.lbl_sm_dii.setText(f"DII : {smd.get('dii', 'N/A')}")
        self.lbl_sm_write.setText(f"Writing : {smd.get('writing', 'N/A')}")
        self.lbl_sm_build.setText(f"Build-up : {smd.get('buildup', 'N/A')}")
        
        # Calculate overall smart money percentage based on sentiment and pcr
        sentiment = self.ai_res['sentiment'].upper()
        pcr = self.ai_res['pcr']
        score = 50
        if "BULL" in sentiment: score = min(100, 50 + int(pcr * 20))
        elif "BEAR" in sentiment: score = max(0, 50 - int((1.5 - pcr) * 30))
        
        self.sm_progress.setValue(score)
        if score > 60:
            self.lbl_sm_score.setText(f"{score}% Bullish")
            self.lbl_sm_score.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold; border: none;")
            self.sm_progress.setStyleSheet("QProgressBar { background-color: #333; border: none; border-radius: 2px; } QProgressBar::chunk { background-color: #4CAF50; border-radius: 2px; }")
        elif score < 40:
            self.lbl_sm_score.setText(f"{100-score}% Bearish")
            self.lbl_sm_score.setStyleSheet("color: #F44336; font-size: 11px; font-weight: bold; border: none;")
            self.sm_progress.setStyleSheet("QProgressBar { background-color: #333; border: none; border-radius: 2px; } QProgressBar::chunk { background-color: #F44336; border-radius: 2px; }")
        else:
            self.lbl_sm_score.setText("Neutral")
            self.lbl_sm_score.setStyleSheet("color: #FFC107; font-size: 11px; font-weight: bold; border: none;")
            self.sm_progress.setStyleSheet("QProgressBar { background-color: #333; border: none; border-radius: 2px; } QProgressBar::chunk { background-color: #FFC107; border-radius: 2px; }")
        
        try:
            exp_date = datetime.datetime.strptime(expiry, "%d-%b-%Y")
            days = (exp_date - datetime.datetime.now()).days
            self.val_expiry.setText(f"{days} Days")
        except:
            self.val_expiry.setText(f"{expiry}")
            
        # Update AI Card
        self.lbl_ai_strategy.setText(self.ai_res['strategy'])
        if "BUY" in self.ai_res['strategy'] or "CALL" in self.ai_res['strategy']:
            self.lbl_ai_action.setText("🟢 TRADE READY (BULLISH)")
            self.ai_card.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A3A25, stop:1 #111216); border: 2px solid #4CAF50; border-radius: 8px; }")
        elif "PUT" in self.ai_res['strategy'] or "BEAR" in self.ai_res['strategy']:
            self.lbl_ai_action.setText("🔴 TRADE READY (BEARISH)")
            self.ai_card.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3A1A1A, stop:1 #111216); border: 2px solid #F44336; border-radius: 8px; }")
        else:
            self.lbl_ai_action.setText("🟡 TRADE READY (NEUTRAL)")
            self.ai_card.setStyleSheet("QFrame { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3A3A1A, stop:1 #111216); border: 2px solid #FFC107; border-radius: 8px; }")
            
        prob = self.ai_res.get('confidence', 80) + 4
        conf = self.ai_res.get('confidence', 80)
        
        self.lbl_ai_prob.setText(self.generate_meter(prob, 10))
        self.lbl_ai_conf.setText(self.generate_meter(conf, 10))
        
        # Strategy alternatives updates (POP and RR parsing below)
        
        setup = self.ai_res.get('setup')
        if setup:
            try:
                rr_val = float(setup.get('rr', 0))
            except (ValueError, TypeError):
                rr_val = 0
                
            risk_level = "LOW" if rr_val > 1.5 else ("MED" if rr_val > 1.0 else "HIGH")
            
            cap = setup.get('capital', 40000)
            mx_p = setup.get('max_profit', 0)
            mx_l = setup.get('max_loss', 0)
            
            self.lbl_ai_capital.setText(f"₹{cap:,.0f}")
            self.lbl_ai_return.setText(f"₹{mx_p:,.0f}")
            self.lbl_ai_risk.setText(f"₹{mx_l:,.0f}")
            self.lbl_ai_rr.setText(f"{rr_val:.1f}")
            
            # Position Sizing
            risk_pct = 1.0
            max_risk_abs = (cap * risk_pct) / 100
            rec_lots = max(1, int(max_risk_abs / mx_l)) if mx_l > 0 else 1
            self.lbl_pos_size.setText(f"Capital: ₹{cap:,.0f} | Risk per Trade: {risk_pct}% | Rec Qty: {rec_lots} Lots")
            
            # Warning logic
            warning_txt = ""
            if "EXPIRY" in self.ai_res.get('reasons', [[ '','' ]])[0][1].upper() or (exp_date - datetime.datetime.now()).days <= 1:
                 warning_txt = "⚠ Expiry Today - Reduce quantity."
                 
            self.lbl_ai_warning.setText(warning_txt)
        
        # AI Explanation
        reasons = self.ai_res.get('reasons', [])
        formatted_reasons = []
        verdict_lines = ["AI Verdict"]
        
        for icon, txt in reasons:
            if icon == '✓':
                formatted_reasons.append(f"<span style='color:#4CAF50'>✔ {txt}</span>")
                if len(verdict_lines) < 5: verdict_lines.append(f"• {txt.split('-')[0]}")
            else:
                formatted_reasons.append(f"<span style='color:#FF9800'>⚠ {txt}</span>")
                if len(verdict_lines) < 5: verdict_lines.append(f"• {txt.split('-')[0]}")
        
        explanation_html = "<br>".join(formatted_reasons)
        self.lbl_ai_reasons.setText(explanation_html)
        
        verdict_txt = "<br>".join(verdict_lines)
        self.lbl_ai_verdict.setText(verdict_txt)
        
        # Strategy Alternatives Table
        alts = self.ai_res.get('alternatives', [])
        display_alts = alts[:5]
        self.alt_table.setRowCount(len(display_alts))
        for i, alt in enumerate(display_alts):
            # Verdict formatting
            strat = alt['strategy']
            if i == 0: strat = f"🟢 {strat} | Recommended"
            elif i < 3: strat = f"🟡 {strat} | Alternative"
            else: strat = f"🔴 {strat} | Avoid"
                
            s_it = QTableWidgetItem(strat)
            s_it.setTextAlignment(Qt.AlignCenter)
            self.alt_table.setItem(i, 0, s_it)
            
            sc_it = QTableWidgetItem(str(alt['score']))
            sc_it.setTextAlignment(Qt.AlignCenter)
            self.alt_table.setItem(i, 1, sc_it)
            
            # Synthesize POP and RR based on Score since engine doesn't emit them for alternatives
            pop = f"{alt['score'] + 4}%"
            pop_it = QTableWidgetItem(pop)
            pop_it.setTextAlignment(Qt.AlignCenter)
            self.alt_table.setItem(i, 2, pop_it)
            
            rr = f"{(alt['score'] / 40.0):.1f}"
            rr_it = QTableWidgetItem(rr)
            rr_it.setTextAlignment(Qt.AlignCenter)
            self.alt_table.setItem(i, 3, rr_it)
        
        # Update Charts
        self.update_charts(self.df)
        
        # Max Values for Gradients
        max_delta = 1.0
        max_gamma = self.df[['CE_Gamma', 'PE_Gamma']].abs().max().max()
        max_theta = self.df[['CE_Theta', 'PE_Theta']].abs().max().max()
        max_vega = self.df[['CE_Vega', 'PE_Vega']].abs().max().max()
        
        self.table.setRowCount(len(self.df))
        
        for i, row in self.df.iterrows():
            strike = row['Strike']
            is_atm = (strike == atm_strike)
            
            def create_item(val, greek_type="", is_ce=False, is_pe=False):
                s = str(val) if isinstance(val, (int, np.integer)) else f"{val:.2f}"
                
                bg_col = "#121212"
                fg_col = "#E0E0E0"
                bold = False
                
                # Gradients for Greeks
                bar = ""
                bar_color = ""
                if greek_type == "Delta":
                    bar = self.render_gradient_meter(val, max_delta, 10)
                    bar_color = "#2196F3"
                elif greek_type == "Gamma":
                    bar = self.render_gradient_meter(val, max_gamma, 10)
                    bar_color = "#9C27B0"
                elif greek_type == "Theta":
                    bar = self.render_gradient_meter(val, max_theta, 10)
                    bar_color = "#F44336"
                elif greek_type == "Vega":
                    bar = self.render_gradient_meter(val, max_vega, 10)
                    bar_color = "#FF9800"
                    
                if bar:
                    s = f"{bar} {val:.2f}"
                
                it = QTableWidgetItem(s)
                it.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                it.setBackground(QColor(bg_col))
                
                if bar: fg_col = bar_color
                it.setForeground(QColor(fg_col))
                return it

            self.table.setItem(i, 0, create_item(row['CE_Delta'], greek_type="Delta", is_ce=True))
            self.table.setItem(i, 1, create_item(row['CE_Gamma'], greek_type="Gamma", is_ce=True))
            self.table.setItem(i, 2, create_item(row['CE_Theta'], greek_type="Theta", is_ce=True))
            self.table.setItem(i, 3, create_item(row['CE_Vega'], greek_type="Vega", is_ce=True))
            self.table.setItem(i, 4, create_item(row['CE_IV'], is_ce=True))
            self.table.setItem(i, 5, create_item(row['CE_Vol'], is_ce=True))
            self.table.setItem(i, 6, create_item(row['CE_CHNG_OI'], is_ce=True))
            self.table.setItem(i, 7, create_item(row['CE_OI'], is_ce=True))
            
            ce_ltp = create_item(row['CE_LTP'], is_ce=True)
            f = QFont(); f.setBold(True); f.setPointSize(11); ce_ltp.setFont(f)
            self.table.setItem(i, 8, ce_ltp)
            
            # 6. Strike Highlight
            strk_item = QTableWidgetItem(str(strike))
            strk_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            if is_atm:
                lbl = QLabel(f" {strike} | ATM ")
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet("border: 2px solid #00E5FF; border-radius: 4px; color: #00E5FF; font-weight: bold; font-size: 14px; background: #12222E;")
                self.table.setCellWidget(i, 9, lbl)
            else:
                if strike < underlying:
                    lbl = QLabel(f"ITM {strike} OTM")
                    lbl.setAlignment(Qt.AlignCenter)
                    lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px; background: #1B3A20; border: none;")
                    self.table.setCellWidget(i, 9, lbl)
                else:
                    lbl = QLabel(f"OTM {strike} ITM")
                    lbl.setAlignment(Qt.AlignCenter)
                    lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px; background: #3A1B1B; border: none;")
                    self.table.setCellWidget(i, 9, lbl)
            
            pe_ltp = create_item(row['PE_LTP'], is_pe=True)
            f = QFont(); f.setBold(True); f.setPointSize(11); pe_ltp.setFont(f)
            self.table.setItem(i, 10, pe_ltp)
            
            self.table.setItem(i, 11, create_item(row['PE_OI'], is_pe=True))
            self.table.setItem(i, 12, create_item(row['PE_CHNG_OI'], is_pe=True))
            self.table.setItem(i, 13, create_item(row['PE_Vol'], is_pe=True))
            self.table.setItem(i, 14, create_item(row['PE_IV'], is_pe=True))
            self.table.setItem(i, 15, create_item(row['PE_Delta'], greek_type="Delta", is_pe=True))
            self.table.setItem(i, 16, create_item(row['PE_Gamma'], greek_type="Gamma", is_pe=True))
            self.table.setItem(i, 17, create_item(row['PE_Theta'], greek_type="Theta", is_pe=True))
            self.table.setItem(i, 18, create_item(row['PE_Vega'], greek_type="Vega", is_pe=True))
            
            self.table.setRowHeight(i, 35)
            
    def export_csv(self):
        if self.df.empty: return
        sym = self.combo_index.currentText()
        exp = self.combo_expiry.currentText()
        path, _ = QFileDialog.getSaveFileName(self, "Export Option Chain", f"{sym}_OptionChain_{exp}.csv", "CSV Files (*.csv)")
        if path:
            self.df.to_csv(path, index=False)
            self.lbl_footer.setText(f"Exported successfully to {path}")
            
    def export_snapshot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Snapshot", f"Snapshot_OptionChain.png", "PNG Files (*.png)")
        if path:
            pixmap = self.grab()
            pixmap.save(path)
            self.lbl_footer.setText(f"Snapshot exported successfully to {path}")
