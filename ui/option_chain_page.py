from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QGroupBox, QGridLayout, QApplication, QFileDialog, QMessageBox,
    QDialog, QDialogButtonBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QColor, QFont

import pandas as pd
import numpy as np
import datetime

from application.data_manager import DataManager
from strategy.option_greeks import OptionGreeks
from ai.option_ai import OptionAI

class FetchChainThread(QThread):
    result_ready = Signal(dict)
    status_update = Signal(str)
    
    def __init__(self, symbol, data_manager):
        super().__init__()
        self.symbol = symbol
        self.data_manager = data_manager
        
    def run(self):
        self.status_update.emit(f"Loading {self.symbol}... (Connecting to DataManager)")
        data = self.data_manager.get_option_chain(self.symbol)
        if not data:
            self.status_update.emit(f"Waiting for Cached Data for {self.symbol}...")
        self.result_ready.emit(data if data else {})


class OptionChainPage(QWidget):
    """
    Professional Option Chain Analyzer - Sprint 65
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
        
        self.setup_ui()
        
        # Auto refresh timer (30s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header Controls
        header_top = QHBoxLayout()
        header_bottom = QHBoxLayout()
        
        title = QLabel("🔗 Professional Option Chain Analyzer")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #9C27B0;")
        
        self.combo_index = QComboBox()
        # Including SENSEX and BANKEX, although NSE API doesn't support them natively. We will handle this in code.
        self.combo_index.addItems(["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"])
        self.combo_index.setStyleSheet("padding: 5px; font-size: 14px;")
        
        self.combo_expiry_type = QComboBox()
        self.combo_expiry_type.addItems(["Nearest Expiry", "Weekly", "Monthly", "All Expiries"])
        self.combo_expiry_type.setStyleSheet("padding: 5px; font-size: 14px;")
        
        self.combo_expiry = QComboBox()
        self.combo_expiry.setStyleSheet("padding: 5px; font-size: 14px;")
        
        self.btn_refresh = QPushButton("🔄 Refresh (30s)")
        self.btn_refresh.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_export_csv = QPushButton("📥 Export CSV")
        self.btn_export_csv.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.btn_export_csv.clicked.connect(self.export_csv)
        
        self.btn_export_excel = QPushButton("📊 Export Excel")
        self.btn_export_excel.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 8px;")
        self.btn_export_excel.clicked.connect(self.export_excel)
        
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: #888; font-size: 12px;")
        
        header_top.addWidget(title)
        header_top.addStretch()
        
        header_bottom.addWidget(QLabel("Index:"))
        header_bottom.addWidget(self.combo_index)
        header_bottom.addWidget(QLabel("Filter:"))
        header_bottom.addWidget(self.combo_expiry_type)
        header_bottom.addWidget(QLabel("Expiry:"))
        header_bottom.addWidget(self.combo_expiry)
        header_bottom.addWidget(self.btn_refresh)
        header_bottom.addWidget(self.btn_export_csv)
        header_bottom.addWidget(self.btn_export_excel)
        header_bottom.addStretch()
        
        layout.addLayout(header_top)
        layout.addLayout(header_bottom)
        layout.addWidget(self.lbl_status)
        
        # Top Dashboard Panel (Feature-10)
        top_dash = QHBoxLayout()
        self.lbl_trend = QLabel("Trend: --")
        self.lbl_momentum = QLabel("Momentum: --")
        self.lbl_bias = QLabel("OI Bias: --")
        self.lbl_countdown = QLabel("⏳ Expiry: --")
        
        for lbl in [self.lbl_trend, self.lbl_momentum, self.lbl_bias, self.lbl_countdown]:
            lbl.setStyleSheet("font-size: 14px; font-weight: bold; background: #2D3039; padding: 6px; border-radius: 4px;")
            top_dash.addWidget(lbl)
            
        layout.addLayout(top_dash)
        
        # Smart Analysis Panel
        self.panel_layout = QHBoxLayout()
        
        # Box 1: Sentiment & PCR
        box1 = QGroupBox("Market Sentiment & PCR")
        grid1 = QGridLayout()
        self.lbl_sentiment = QLabel("--")
        self.lbl_pcr = QLabel("--")
        self.lbl_pcr_trend = QLabel("--")
        self.lbl_buildup = QLabel("--")
        self.lbl_smart_money = QLabel("--")
        self.lbl_unusual = QLabel("--")
        grid1.addWidget(QLabel("Sentiment:"), 0, 0)
        grid1.addWidget(self.lbl_sentiment, 0, 1)
        grid1.addWidget(QLabel("Live PCR:"), 1, 0)
        grid1.addWidget(self.lbl_pcr, 1, 1)
        grid1.addWidget(QLabel("PCR Trend:"), 2, 0)
        grid1.addWidget(self.lbl_pcr_trend, 2, 1)
        grid1.addWidget(QLabel("Build-up:"), 3, 0)
        grid1.addWidget(self.lbl_buildup, 3, 1)
        grid1.addWidget(QLabel("Activity:"), 4, 0)
        grid1.addWidget(self.lbl_unusual, 4, 1)
        grid1.addWidget(QLabel("Smart Money:"), 5, 0)
        grid1.addWidget(self.lbl_smart_money, 5, 1)
        box1.setLayout(grid1)
        self.panel_layout.addWidget(box1)
        
        # Box 2: Option AI Setup
        box3 = QGroupBox("🧠 Option AI Setup Engine")
        box3.setStyleSheet("QGroupBox { border: 2px solid #9C27B0; border-radius: 6px; } QGroupBox::title { color: #E1BEE7; }")
        grid3 = QGridLayout()
        self.lbl_ai_rec = QLabel("--")
        self.lbl_ai_reasons = QLabel("--")
        self.lbl_ai_setup = QLabel("--")
        grid3.addWidget(QLabel("Strategy:"), 0, 0)
        grid3.addWidget(self.lbl_ai_rec, 0, 1)
        grid3.addWidget(QLabel("Reasons:"), 1, 0)
        grid3.addWidget(self.lbl_ai_reasons, 1, 1)
        grid3.addWidget(QLabel("Setup Details:"), 2, 0)
        grid3.addWidget(self.lbl_ai_setup, 2, 1)
        box3.setLayout(grid3)
        self.panel_layout.addWidget(box3)
        
        layout.addLayout(self.panel_layout)
        
        # Table
        self.table = QTableWidget()
        cols = [
            "CE Delta", "CE Gamma", "CE Theta", "CE Vega", "CE IV", "CE Vol", "CE OI Chg", "CE OI", "CE LTP", 
            "Strike", 
            "PE LTP", "PE OI", "PE OI Chg", "PE Vol", "PE IV", "PE Delta", "PE Gamma", "PE Theta", "PE Vega"
        ]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)
        header_view.setSectionResizeMode(9, QHeaderView.ResizeToContents) # Strike
        
        # HOTFIX: Make Table strictly Read-Only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1E2028; color: #FFF; border: 1px solid #3D4047; }
            QTableWidget::item:selected { background-color: #3949AB; color: white; }
            QHeaderView::section { background-color: #2D3039; color: #888; padding: 4px; font-weight: bold; }
        """)
        layout.addWidget(self.table)
        
        # Connect signals
        self.combo_index.currentTextChanged.connect(self.load_data)
        self.combo_expiry.currentTextChanged.connect(self.process_selected_expiry)
        self.combo_expiry_type.currentTextChanged.connect(self.apply_expiry_filter)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def load_data(self):
        sym = self.combo_index.currentText()
        if sym in ["SENSEX", "BANKEX"]:
            self.lbl_status.setText(f"Warning: {sym} requires a BSE Data Provider. NSE API does not support BSE indices.")
            QMessageBox.warning(self, "BSE Not Supported", f"{sym} requires a separate BSE Data Provider API which is not part of the NSE Official API. Switch to NIFTY/BANKNIFTY.")
            self.timer.stop()
            self.btn_refresh.setEnabled(True)
            return
            
        self.btn_refresh.setEnabled(False)
        
        self.fetch_thread = FetchChainThread(sym, self.data_manager)
        self.fetch_thread.status_update.connect(self.lbl_status.setText)
        self.fetch_thread.result_ready.connect(self.on_data_fetched)
        self.fetch_thread.start()
        
    def on_data_fetched(self, data):
        self.btn_refresh.setEnabled(True)
        if not data or "records" not in data:
            # If we don't have new data, see if we have raw_data cached from before
            if self.raw_data:
                self.lbl_status.setText(f"Retrying... Displaying Last Successful Data for {self.combo_index.currentText()}")
                # Don't return, let it keep showing the old table
            else:
                self.lbl_status.setText("Reconnecting... Please wait.")
            return
            
        self.raw_data = data
        self.lbl_status.setText("Data fetched successfully. Processing...")
        
        self.apply_expiry_filter()
        
        if not self.timer.isActive():
            self.timer.start(30000)
            
    def apply_expiry_filter(self):
        if not self.raw_data: return
        expiries = self.raw_data["records"]["expiryDates"]
        
        filter_type = self.combo_expiry_type.currentText()
        filtered = []
        
        if filter_type == "Nearest Expiry":
            filtered = [expiries[0]] if expiries else []
        elif filter_type == "Weekly":
            # Just take the first 4 expiries as weekly representation
            filtered = expiries[:4]
        elif filter_type == "Monthly":
            # Rough logic: usually last week of month. We just take ones that are likely monthly.
            filtered = expiries[3:7] if len(expiries) > 3 else expiries
        else:
            filtered = expiries
            
        if not filtered:
            filtered = expiries
            
        self.combo_expiry.blockSignals(True)
        curr = self.combo_expiry.currentText()
        self.combo_expiry.clear()
        self.combo_expiry.addItems(filtered)
        if curr in filtered:
            self.combo_expiry.setCurrentText(curr)
        self.combo_expiry.blockSignals(False)
        
        self.process_selected_expiry()
            
    def process_selected_expiry(self):
        if not self.raw_data: return
        
        expiry = self.combo_expiry.currentText()
        if not expiry: return
        
        underlying = self.raw_data["records"]["underlyingValue"]
        self.lbl_status.setText(f"Underlying: {underlying:.2f} | Expiry: {expiry}")
        
        data_list = self.raw_data["records"]["data"]
        rows = []
        
        sym = self.combo_index.currentText()
        
        for item in data_list:
            if item["expiryDate"] == expiry:
                ce = item.get("CE", {})
                pe = item.get("PE", {})
                
                # T to expiry
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
                    "CE_Delta": ce_greeks["delta"],
                    "CE_Gamma": ce_greeks["gamma"],
                    "CE_Theta": ce_greeks["theta"],
                    "CE_Vega": ce_greeks["vega"],
                    "CE_IV": ce_iv,
                    "CE_Vol": ce.get("totalTradedVolume", 0),
                    "CE_CHNG_OI": ce.get("changeinOpenInterest", 0),
                    "CE_OI": ce.get("openInterest", 0),
                    "CE_LTP": ce.get("lastPrice", 0),
                    "Strike": strike,
                    "PE_LTP": pe.get("lastPrice", 0),
                    "PE_OI": pe.get("openInterest", 0),
                    "PE_CHNG_OI": pe.get("changeinOpenInterest", 0),
                    "PE_Vol": pe.get("totalTradedVolume", 0),
                    "PE_IV": pe_iv,
                    "PE_Delta": pe_greeks["delta"],
                    "PE_Gamma": pe_greeks["gamma"],
                    "PE_Theta": pe_greeks["theta"],
                    "PE_Vega": pe_greeks["vega"],
                })
                
        self.df = pd.DataFrame(rows)
        if self.df.empty: return
        self.df = self.df.sort_values("Strike").reset_index(drop=True)
        
        # Update AI Panels FIRST to get smart strikes
        self.ai_res = self.ai.analyze(self.df, underlying, expiry, sym)
        
        # Update Top Dashboard
        self.lbl_trend.setText(f"Trend: {self.ai_res['sentiment']}")
        if self.ai_res['sentiment'] == "Bullish": self.lbl_trend.setStyleSheet("color: #4CAF50; font-weight: bold; background: #1B5E20; padding: 6px;")
        elif self.ai_res['sentiment'] == "Bearish": self.lbl_trend.setStyleSheet("color: #F44336; font-weight: bold; background: #B71C1C; padding: 6px;")
        
        self.lbl_bias.setText(f"OI Bias: {self.ai_res['pcr']}")
        self.lbl_momentum.setText(f"Max Pain: {self.ai_res['max_pain']}")
        
        try:
            exp_date = datetime.datetime.strptime(expiry, "%d-%b-%Y")
            today = datetime.datetime.now()
            diff = exp_date - today
            days = diff.days
            if days == 0: self.lbl_countdown.setText("⏳ Expiry: TODAY")
            else: self.lbl_countdown.setText(f"⏳ Expiry: {days} Days Left")
        except:
            self.lbl_countdown.setText(f"⏳ Expiry: {expiry}")
            
        self.lbl_pcr.setText(str(self.ai_res['pcr']))
        self.lbl_pcr_trend.setText(self.ai_res['pcr_trend'])
        self.lbl_buildup.setText(self.ai_res['buildup'])
        self.lbl_smart_money.setText(self.ai_res.get('smart_money', '--'))
        self.lbl_unusual.setText(self.ai_res.get('unusual_activity', '--'))
        
        if "Selling" in self.ai_res.get('smart_money', ''): self.lbl_smart_money.setStyleSheet("color: #F44336; font-weight: bold;")
        elif "Buying" in self.ai_res.get('smart_money', ''): self.lbl_smart_money.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        self.lbl_sentiment.setText(f"{self.ai_res['sentiment']} ({self.ai_res['confidence']}%)")
        
        rec = self.ai_res['recommendation']
        strat = self.ai_res['strategy']
        self.lbl_ai_rec.setText(f"{strat} ({rec})")
        if "BUY CE" in rec or "BULL" in strat: self.lbl_ai_rec.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
        elif "BUY PE" in rec or "BEAR" in strat: self.lbl_ai_rec.setStyleSheet("color: #FF5252; font-weight: bold; font-size: 16px;")
        else: self.lbl_ai_rec.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 16px;")
        
        self.lbl_ai_reasons.setText(" | ".join(self.ai_res['reasons']))
        
        setup = self.ai_res.get('setup')
        if setup:
            ent = setup['entry']
            sl = setup['sl']
            t1 = setup['target_1']
            
            ent_s = f"₹{ent:.2f}" if isinstance(ent, (int, float)) else str(ent)
            sl_s = f"₹{sl:.2f}" if isinstance(sl, (int, float)) else str(sl)
            t1_s = f"₹{t1:.2f}" if isinstance(t1, (int, float)) else str(t1)
            
            s_text = f"Strike: {setup['strike']} | Entry: {ent_s} | SL: {sl_s} | T1: {t1_s} | RR: {setup['rr']}"
            self.lbl_ai_setup.setText(s_text)
            self.lbl_ai_setup.setStyleSheet("color: #00E5FF; font-weight: bold;")
        else:
            self.lbl_ai_setup.setText("--")
            self.lbl_ai_setup.setStyleSheet("")
            
        # Prepare for Table Render (Heatmaps)
        max_ce_oi = self.df['CE_OI'].max()
        max_pe_oi = self.df['PE_OI'].max()
        
        self.table.setRowCount(len(self.df))
        atm_strike = self.ai_res['best_atm']
        
        for i, row in self.df.iterrows():
            strike = row['Strike']
            is_atm = (strike == atm_strike)
            is_highest_ce = (row['CE_OI'] == max_ce_oi and max_ce_oi > 0)
            is_highest_pe = (row['PE_OI'] == max_pe_oi and max_pe_oi > 0)
            
            def create_item(val, col_type="", is_ce=False, is_pe=False):
                s = str(val) if isinstance(val, (int, np.integer)) else f"{val:.2f}"
                it = QTableWidgetItem(s)
                it.setTextAlignment(Qt.AlignCenter)
                
                # Base Colors
                bg_col = "#1E2028"
                fg_col = "#FFFFFF"
                
                if is_atm:
                    bg_col = "#FFD700" # Gold
                    fg_col = "#000000"
                elif is_ce and strike < underlying: bg_col = "#2A3D2A" # Light Green ITM CE
                elif is_ce and strike > underlying: bg_col = "#2A3545" # Light Blue OTM CE
                elif is_pe and strike > underlying: bg_col = "#2A3D2A" # Light Green ITM PE
                elif is_pe and strike < underlying: bg_col = "#2A3545" # Light Blue OTM PE
                
                # Highlight Highest OI Row overriding
                if is_highest_ce and is_ce: bg_col = "#4CAF50" # Dark Green
                if is_highest_pe and is_pe: bg_col = "#F44336" # Dark Red
                
                # Heatmap for OI column specifically
                if col_type == "OI":
                    if is_ce and max_ce_oi > 0:
                        intensity = int((val / max_ce_oi) * 200)
                        bg_col = f"#{intensity:02x}0000" if not is_atm else bg_col
                    elif is_pe and max_pe_oi > 0:
                        intensity = int((val / max_pe_oi) * 200)
                        bg_col = f"#00{intensity:02x}00" if not is_atm else bg_col
                        
                # Live OI Change Bar
                if col_type == "OI_CHG":
                    if val > 0:
                        s = f"📈 +{val}"
                        fg_col = "#4CAF50" if not is_atm else "#005500"
                    elif val < 0:
                        s = f"📉 {val}"
                        fg_col = "#F44336" if not is_atm else "#990000"
                    it.setText(s)
                    
                it.setBackground(QColor(bg_col))
                it.setForeground(QColor(fg_col))
                
                if is_atm or is_highest_ce or is_highest_pe:
                    f = QFont()
                    f.setBold(True)
                    it.setFont(f)
                return it

            self.table.setItem(i, 0, create_item(row['CE_Delta'], is_ce=True))
            self.table.setItem(i, 1, create_item(row['CE_Gamma'], is_ce=True))
            self.table.setItem(i, 2, create_item(row['CE_Theta'], is_ce=True))
            self.table.setItem(i, 3, create_item(row['CE_Vega'], is_ce=True))
            self.table.setItem(i, 4, create_item(row['CE_IV'], is_ce=True))
            self.table.setItem(i, 5, create_item(row['CE_Vol'], is_ce=True))
            self.table.setItem(i, 6, create_item(row['CE_CHNG_OI'], col_type="OI_CHG", is_ce=True))
            self.table.setItem(i, 7, create_item(row['CE_OI'], col_type="OI", is_ce=True))
            self.table.setItem(i, 8, create_item(row['CE_LTP'], is_ce=True))
            
            # Strike Column
            strk_item = QTableWidgetItem(str(strike))
            strk_item.setTextAlignment(Qt.AlignCenter)
            if is_atm:
                strk_item.setBackground(QColor("#FFD700"))
                strk_item.setForeground(QColor("#000000"))
                f = QFont(); f.setBold(True); strk_item.setFont(f)
            else:
                strk_item.setBackground(QColor("#000000"))
                strk_item.setForeground(QColor("#FF9800"))
            self.table.setItem(i, 9, strk_item)
            
            self.table.setItem(i, 10, create_item(row['PE_LTP'], is_pe=True))
            self.table.setItem(i, 11, create_item(row['PE_OI'], col_type="OI", is_pe=True))
            self.table.setItem(i, 12, create_item(row['PE_CHNG_OI'], col_type="OI_CHG", is_pe=True))
            self.table.setItem(i, 13, create_item(row['PE_Vol'], is_pe=True))
            self.table.setItem(i, 14, create_item(row['PE_IV'], is_pe=True))
            self.table.setItem(i, 15, create_item(row['PE_Delta'], is_pe=True))
            self.table.setItem(i, 16, create_item(row['PE_Gamma'], is_pe=True))
            self.table.setItem(i, 17, create_item(row['PE_Theta'], is_pe=True))
            self.table.setItem(i, 18, create_item(row['PE_Vega'], is_pe=True))
            
    def on_item_double_clicked(self, item):
        row = item.row()
        col = item.column()
        
        if self.df.empty or row >= len(self.df):
            return
            
        row_data = self.df.iloc[row]
        strike = row_data['Strike']
        
        # Determine if CE or PE was clicked
        is_ce = True if col < 9 else False
        opt_type = "CE" if is_ce else "PE"
        
        ltp = row_data[f'{opt_type}_LTP']
        oi = row_data[f'{opt_type}_OI']
        oi_chg = row_data[f'{opt_type}_CHNG_OI']
        iv = row_data[f'{opt_type}_IV']
        delta = row_data[f'{opt_type}_Delta']
        gamma = row_data[f'{opt_type}_Gamma']
        theta = row_data[f'{opt_type}_Theta']
        vega = row_data[f'{opt_type}_Vega']
        
        sym = self.combo_index.currentText()
        
        self.show_strike_analysis_popup(sym, strike, opt_type, ltp, oi, oi_chg, iv, delta, gamma, theta, vega)
        
    def show_strike_analysis_popup(self, sym, strike, opt_type, ltp, oi, oi_chg, iv, delta, gamma, theta, vega):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Strike Analysis: {sym} {strike} {opt_type}")
        dialog.setMinimumWidth(350)
        dialog.setStyleSheet("QDialog { background-color: #121212; color: white; } QLabel { font-size: 14px; }")
        
        layout = QVBoxLayout(dialog)
        
        # Header
        lbl_header = QLabel(f"<b>{sym} {strike} {opt_type}</b>")
        lbl_header.setStyleSheet("font-size: 18px; color: #00E5FF; padding: 5px;")
        lbl_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_header)
        
        # Grid Data
        grid = QGridLayout()
        grid.addWidget(QLabel("LTP"), 0, 0); grid.addWidget(QLabel(f"<b>₹{ltp:.2f}</b>"), 0, 1)
        grid.addWidget(QLabel("OI"), 1, 0); grid.addWidget(QLabel(f"<b>{int(oi):,}</b>"), 1, 1)
        
        oi_chg_str = f"+{int(oi_chg):,}" if oi_chg > 0 else f"{int(oi_chg):,}"
        oi_chg_color = "#4CAF50" if oi_chg > 0 else "#F44336"
        lbl_oi_chg = QLabel(f"<b>{oi_chg_str}</b>")
        lbl_oi_chg.setStyleSheet(f"color: {oi_chg_color};")
        grid.addWidget(QLabel("OI Change"), 2, 0); grid.addWidget(lbl_oi_chg, 2, 1)
        
        grid.addWidget(QLabel("IV"), 3, 0); grid.addWidget(QLabel(f"<b>{iv:.2f}</b>"), 3, 1)
        grid.addWidget(QLabel("Delta"), 4, 0); grid.addWidget(QLabel(f"<b>{delta:.2f}</b>"), 4, 1)
        grid.addWidget(QLabel("Gamma"), 5, 0); grid.addWidget(QLabel(f"<b>{gamma:.4f}</b>"), 5, 1)
        grid.addWidget(QLabel("Theta"), 6, 0); grid.addWidget(QLabel(f"<b>{theta:.2f}</b>"), 6, 1)
        grid.addWidget(QLabel("Vega"), 7, 0); grid.addWidget(QLabel(f"<b>{vega:.2f}</b>"), 7, 1)
        
        layout.addLayout(grid)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #333;")
        layout.addWidget(line)
        
        # AI Rating
        ai_box = QGroupBox("🤖 AI Analysis")
        ai_box.setStyleSheet("QGroupBox { border: 1px solid #4CAF50; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; color: #4CAF50; }")
        ai_layout = QGridLayout()
        
        # Generate dynamic setup based on AI Res if it matches the current strike
        conf = self.ai_res.get('confidence', 50)
        stars = "⭐" * int(conf / 20) + "☆" * (5 - int(conf / 20))
        
        # If the clicked strike is the exact recommendation, show the full setup.
        setup = self.ai_res.get('setup')
        s_act = "WAIT"
        s_ent = ltp
        s_sl = max(0, ltp * 0.7)
        s_t1 = ltp * 1.3
        s_t2 = ltp * 1.6
        
        if setup and setup.get('strike') == strike and ((opt_type == "CE" and "BUY CE" in self.ai_res['recommendation']) or (opt_type == "PE" and "BUY PE" in self.ai_res['recommendation'])):
            s_act = "BUY"
            s_ent = setup['entry']
            s_sl = setup['sl']
            s_t1 = setup['target_1']
            s_t2 = setup['target_2']
            
        ai_layout.addWidget(QLabel("Rating"), 0, 0); ai_layout.addWidget(QLabel(stars), 0, 1)
        ai_layout.addWidget(QLabel("Confidence"), 1, 0); ai_layout.addWidget(QLabel(f"<b>{conf}%</b>"), 1, 1)
        
        lbl_act = QLabel(f"<b>{s_act}</b>")
        lbl_act.setStyleSheet("color: #4CAF50; font-size: 16px;" if s_act == "BUY" else "color: #FF9800; font-size: 16px;")
        ai_layout.addWidget(QLabel("Suggested Action"), 2, 0); ai_layout.addWidget(lbl_act, 2, 1)
        
        if s_act == "BUY":
            ent_s = f"₹{s_ent:.2f}" if isinstance(s_ent, (int, float)) else str(s_ent)
            sl_s = f"₹{s_sl:.2f}" if isinstance(s_sl, (int, float)) else str(s_sl)
            t1_s = f"₹{s_t1:.2f}" if isinstance(s_t1, (int, float)) else str(s_t1)
            t2_s = f"₹{s_t2:.2f}" if isinstance(s_t2, (int, float)) else str(s_t2)
            
            ai_layout.addWidget(QLabel("Entry"), 3, 0); ai_layout.addWidget(QLabel(ent_s), 3, 1)
            ai_layout.addWidget(QLabel("Stop Loss"), 4, 0); ai_layout.addWidget(QLabel(sl_s), 4, 1)
            ai_layout.addWidget(QLabel("Target 1"), 5, 0); ai_layout.addWidget(QLabel(t1_s), 5, 1)
            ai_layout.addWidget(QLabel("Target 2"), 6, 0); ai_layout.addWidget(QLabel(t2_s), 6, 1)
            
        ai_box.setLayout(ai_layout)
        layout.addWidget(ai_box)
        
        # Close Button
        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        btn_box.setStyleSheet("QPushButton { background-color: #333; color: white; padding: 5px; }")
        layout.addWidget(btn_box)
        
        dialog.exec_()

    def export_csv(self):
        if self.df.empty: return
        sym = self.combo_index.currentText()
        exp = self.combo_expiry.currentText()
        path, _ = QFileDialog.getSaveFileName(self, "Export Option Chain", f"{sym}_OptionChain_{exp}.csv", "CSV Files (*.csv)")
        if path:
            self.df.to_csv(path, index=False)
            self.lbl_status.setText(f"Exported successfully to {path}")
            
    def export_excel(self):
        if self.df.empty: return
        try:
            import openpyxl
        except ImportError:
            QMessageBox.warning(self, "Missing Library", "The 'openpyxl' library is required to export to Excel natively. Please use Export CSV instead or run 'pip install openpyxl'.")
            return
            
        sym = self.combo_index.currentText()
        exp = self.combo_expiry.currentText()
        path, _ = QFileDialog.getSaveFileName(self, "Export Option Chain", f"{sym}_OptionChain_{exp}.xlsx", "Excel Files (*.xlsx)")
        if path:
            self.df.to_excel(path, index=False)
            self.lbl_status.setText(f"Exported Excel successfully to {path}")
