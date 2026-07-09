from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QCheckBox, QMessageBox, QCompleter, QComboBox
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QGuiApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
import pandas as pd
from ui.styles import BG_COLOR, CARD_BG, TEXT_PRIMARY, BTN_BLUE, COLOR_BUY, COLOR_SELL
from application.paper_trading_service import PaperTradingEngine
from core.trade_setup_engine import TradeSetupEngine
from core.ai_engine import AIPredictionEngine
from data.stocks import Stock

class ChartScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_PRIMARY};")
        self.engine = PaperTradingEngine()
        self.setup_engine = TradeSetupEngine()
        self.ai_engine = AIPredictionEngine()
        self.current_tf = "1d"
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("LIVE CHARTS")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter Symbol (e.g., RELIANCE.NS)")
        self.search_box.setStyleSheet("background-color: #2D2F36; color: white; padding: 8px; border: 1px solid #3D4047; border-radius: 4px;")
        self.search_box.returnPressed.connect(self.load_charts)
        
        # Auto-complete for search box
        from config.config import AppConfig
        config = AppConfig()
        config.load()
        self.completer_model = QStringListModel(config.watchlist_symbols)
        self.completer = QCompleter(self.completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        # Completer styling (dropdown)
        self.completer.popup().setStyleSheet("""
            QListView { background-color: #2D2F36; color: white; border: 1px solid #3D4047; }
            QListView::item:selected { background-color: #2196F3; }
        """)
        self.search_box.setCompleter(self.completer)
        
        self.btn_load = QPushButton("Load Chart")
        self.btn_load.setStyleSheet(f"background-color: {BTN_BLUE}; color: white; padding: 8px 15px; border-radius: 4px; border: none; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_charts)
        
        self.btn_tv = QPushButton("🌐 Open in Web")
        self.btn_tv.setStyleSheet(f"background-color: #9C27B0; color: white; padding: 8px 15px; border-radius: 4px; border: none; font-weight: bold;")
        self.btn_tv.clicked.connect(self.open_tradingview_web)
        self.btn_tv.hide() # Hidden until a chart is loaded
        
        # Mode Selector
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["SWING", "OPTIONS"])
        combo_style = """
            QComboBox {
                background-color: #3D4047;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid #555;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2F36;
                color: white;
                selection-background-color: #2196F3;
                border: 1px solid #555;
                outline: none;
            }
        """
        self.combo_mode.setStyleSheet(combo_style)
        self.combo_mode.currentTextChanged.connect(self.load_charts)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(QLabel("Mode:"))
        header.addWidget(self.combo_mode)
        header.addWidget(self.search_box)
        header.addWidget(self.btn_load)
        header.addWidget(self.btn_tv)
        layout.addLayout(header)
        
        # Chart Layout
        self.chart_frame = QFrame()
        self.chart_frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 8px; border: 1px solid #3D4047;")
        chart_layout = QVBoxLayout(self.chart_frame)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        
        trade_layout = QHBoxLayout()
        trade_layout.setContentsMargins(15, 10, 15, 10)
        
        self.lbl_ai = QLabel("")
        self.lbl_ai.setStyleSheet("font-size: 14px; font-weight: bold; background-color: #2D2F36; padding: 5px 10px; border-radius: 4px;")
        self.lbl_ai.hide()
        
        self.btn_buy = QPushButton("BUY")
        self.btn_buy.setStyleSheet(f"background-color: {COLOR_BUY}; color: white; font-weight: bold;")
        self.btn_buy.clicked.connect(self.execute_buy)
        self.btn_buy.hide()
        
        self.btn_sell = QPushButton("SELL")
        self.btn_sell.setStyleSheet(f"background-color: {COLOR_SELL}; color: white; font-weight: bold;")
        self.btn_sell.clicked.connect(self.execute_sell)
        self.btn_sell.hide()
        
        trade_layout.addStretch()
        trade_layout.addWidget(self.lbl_ai)
        trade_layout.addWidget(self.btn_buy)
        trade_layout.addWidget(self.btn_sell)
        chart_layout.addLayout(trade_layout)
        
        # Create QWebEngineView for TradingView
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #131722;")
        
        # Chart symbol title bar
        sym_bar = QHBoxLayout()
        sym_bar.setContentsMargins(15, 6, 15, 6)
        self.chart_title_lbl = QLabel("📊  Loading...")
        self.chart_title_lbl.setStyleSheet(
            "color: #FF9800; font-weight: bold; font-size: 13px; "
            "background-color: #1A1C23; padding: 4px 10px; border-radius: 4px;"
        )
        sym_bar.addWidget(self.chart_title_lbl)
        sym_bar.addStretch()
        chart_layout.addLayout(sym_bar)

        # ── Trade Setup Info Bar ───────────────────────────────────────
        self.trade_info_frame = QFrame()
        self.trade_info_frame.setStyleSheet("""
            QFrame {
                background-color: #1E2028;
                border-top: 1px solid #2D2F36;
                border-bottom: 1px solid #2D2F36;
            }
        """)
        info_layout = QHBoxLayout(self.trade_info_frame)
        info_layout.setContentsMargins(16, 8, 16, 8)
        info_layout.setSpacing(20)

        def _info_pair(icon, label_text, color="#CCC"):
            container = QFrame()
            container.setObjectName("InfoContainer")
            container.setStyleSheet("""
                #InfoContainer {
                    background-color: #252830;
                    border-radius: 14px;
                    border: 1px solid #363A45;
                }
            """)
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(12, 4, 12, 4)
            h_layout.setSpacing(6)
            
            lbl_key = QLabel(f"{icon} {label_text} :")
            lbl_key.setStyleSheet("color: #8B909D; font-size: 12px; background: transparent; border: none;")
            lbl_key.setAlignment(Qt.AlignVCenter)
            
            lbl_val = QLabel("--")
            lbl_val.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; background: transparent; border: none;")
            lbl_val.setAlignment(Qt.AlignVCenter)
            
            h_layout.addWidget(lbl_key)
            h_layout.addWidget(lbl_val)
            
            info_layout.addWidget(container)
            return lbl_val

        self.lbl_score  = _info_pair("🟠", "Score", "#FF9800")
        self.lbl_signal = _info_pair("🟢", "Signal", "#4CAF50")
        self.lbl_entry  = _info_pair("🟢", "Entry",  "#4CAF50")
        self.lbl_sl     = _info_pair("🔴", "SL",     "#F44336")
        self.lbl_t1     = _info_pair("🔵", "TP1",    "#2196F3")
        self.lbl_t2     = _info_pair("🟣", "TP2",    "#9C27B0")
        info_layout.addStretch()
        self.trade_info_frame.hide()   # hidden until data loads
        chart_layout.addWidget(self.trade_info_frame)
        # ──────────────────────────────────────────────────────────

        chart_layout.addWidget(self.web_view, 1) # Give it stretch factor 1
        layout.addWidget(self.chart_frame, 1)
        
        # Load default chart
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, lambda: self.load_chart_with_symbol("^NSEI"))

    def open_tradingview_web(self):
        if hasattr(self, 'current_symbol') and self.current_symbol:
            import urllib.parse
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            tv_symbol = self.current_symbol.replace('.NS', '').replace('.BO', '')
            url = f"https://in.tradingview.com/chart/?symbol=NSE:{tv_symbol}"
            QDesktopServices.openUrl(QUrl(url))

    def change_timeframe(self, tf):
        self.current_tf = tf
        if hasattr(self, 'current_symbol') and self.current_symbol:
            self.load_charts()

    def load_chart_with_symbol(self, symbol):
        self.search_box.setText(symbol)
        self.load_charts()

    def load_charts(self):
        symbol = self.search_box.text().strip().upper()
        if not symbol:
            return
            
        self.btn_load.setText("Loading...")
        self.btn_load.setEnabled(False)
        
        from market.yahoo_provider import YahooFinanceProvider
        from market.dhan_provider import DhanProvider
        from config.config import AppConfig
        
        config = AppConfig()
        config.load()
        if getattr(config, 'data_provider', 'yahoo') == 'dhan':
            provider = DhanProvider(
                client_id=getattr(config, 'dhan_client_id', ''),
                access_token=getattr(config, 'dhan_access_token', '')
            )
        else:
            provider = YahooFinanceProvider()
        provider.connect()
        
        tf = self.current_tf
        period = "3mo" if tf in ["1d", "1wk", "1mo"] else "1mo"
        if tf == "1m":
            period = "5d"
        elif tf in ["5m", "15m", "30m", "1h", "4h"]:
            period = "1mo"
        
        # We don't need to clear the pyqtgraph widget anymore
        
        # Retrieve trade object from Dashboard (Synchronization)
        trade_detail = None
        try:
            main_win = self.window()
            if hasattr(main_win, 'dashboard') and hasattr(main_win.dashboard, 'last_results'):
                trade_detail = main_win.dashboard.last_results.get("detail_map", {}).get(symbol)
        except Exception as e:
            print("Dashboard sync error:", e)
        
        self._plot_single(provider, symbol, tf, period, trade_detail)
        
        self.btn_load.setText("Load Chart")
        self.btn_load.setEnabled(True)

    def _plot_single(self, provider, symbol, tf, period, trade_detail):
        # Update AI and Trade Actions
        self.current_symbol = symbol
        self.current_price = provider.get_last_price(symbol)
        
        if self.current_price > 0:
            self.btn_buy.setText(f"BUY @ ₹{self.current_price:,.2f}")
            self.btn_sell.setText(f"SELL @ ₹{self.current_price:,.2f}")
            self.btn_buy.show()
            self.btn_sell.show()
            self.btn_tv.show()
        else:
            self.btn_buy.hide()
            self.btn_sell.hide()
            self.btn_tv.hide()
            
        ohlcv = provider.get_ohlcv(symbol, interval=tf, period=period)
        if ohlcv:
            self.lbl_ai.setText("🤖 AI Analyzing...")
            self.lbl_ai.show()
            ai_res = self.ai_engine.train_and_predict(ohlcv)
            if ai_res:
                col = "#4CAF50" if ai_res['direction'] == 'UP' else "#F44336"
                self.lbl_ai.setText(f"🤖 5D Forecast: <span style='color: {col};'>₹{ai_res['predicted_price_5d']:.2f} ({ai_res['percent_change']:+.2f}%)</span> | Conf: {ai_res['confidence']}%")
            else:
                self.lbl_ai.setText("🤖 AI: Insufficient Data")
        
        # ── Populate Qt trade info bar (Synchronized) ─────────────
        if trade_detail and ohlcv is not None:
            sig = trade_detail.get("signal", "--")
            score_val = trade_detail.get("score", "--")
            sig_color = '#4CAF50' if 'BUY' in sig else '#F44336' if 'SELL' in sig else '#FFC107'

            self.lbl_score.setText(str(score_val))
            self.lbl_signal.setText(sig)
            self.lbl_signal.setStyleSheet(f"color: {sig_color}; font-weight: bold; font-size: 13px; background: transparent; border: none;")

            if sig in ["BUY", "STRONG_BUY", "SELL"]:
                entry = trade_detail.get("entry", "--")
                sl = trade_detail.get("sl", "--")
                t1 = trade_detail.get("target1", "--")
                t2 = trade_detail.get("target2", "--")
                
                self.lbl_entry.setText(f"₹{entry}" if entry != "--" else "--")
                self.lbl_sl.setText(f"₹{sl}" if sl != "--" else "--")
                self.lbl_t1.setText(f"₹{t1}" if t1 != "--" else "--")
                self.lbl_t2.setText(f"₹{t2}" if t2 != "--" else "--")
            else:
                self.lbl_entry.setText("WATCH")
                self.lbl_sl.setText("--")
                self.lbl_t1.setText("--")
                self.lbl_t2.setText("--")
                
            self.trade_info_frame.show()
        else:
            self.trade_info_frame.hide()
        # ───────────────────────────────────────────────────────────────

        # Load TradingView Widget
        # Detect exchange from suffix — .NS = NSE, .BO = BSE
        if symbol.endswith('.BO'):
            exchange = "BSE"
            tv_symbol = symbol.replace('.BO', '')
        else:
            exchange = "NSE"   # Default NSE for .NS and no-suffix
            tv_symbol = symbol.replace('.NS', '')

        if tv_symbol == "^NSEI":
            full_tv_symbol = "NSE:NIFTY1!"
        elif tv_symbol == "^NSEBANK":
            full_tv_symbol = "NSE:BANKNIFTY1!"
        elif tv_symbol == "BANKNIFTY":
            full_tv_symbol = "NSE:BANKNIFTY1!"
        elif tv_symbol == "NIFTY":
            full_tv_symbol = "NSE:NIFTY1!"
        elif tv_symbol == "FINNIFTY":
            full_tv_symbol = "NSE:FINNIFTY1!"
        else:
            tv_symbol = tv_symbol.replace('-', '_')
            full_tv_symbol = f"{exchange}:{tv_symbol}"
        # Map timeframes
        tf_map = {
            "1mo": "M", "1wk": "W", "1d": "D", 
            "4h": "240", "1h": "60", "30m": "30", "15m": "15", "5m": "5", "1m": "1"
        }
        tv_tf = tf_map.get(tf.lower(), "D")
        
        # ── Build TradingView direct URL (setUrl is 100% reliable vs setHtml) ──
        import urllib.parse
        from PySide6.QtCore import QUrl

        tv_params = urllib.parse.urlencode({
            "symbol":   full_tv_symbol,
            "interval": tv_tf,
            "timezone": "Asia/Kolkata",
            "theme":    "dark",
            "style":    "1",
            "locale":   "in",
            "backgroundColor": "#131722",
            "gridColor":       "#1f293d",
            "hide_top_toolbar": "false",
            "hide_legend":      "false",
            "save_image":       "false",
            "withdateranges":   "true",
            "allow_symbol_change": "false",
            "studies":  "[]",
            "utm_source": "rahuul_radar",
        })

        tv_url = f"https://www.tradingview.com/chart/?{tv_params}"
        self.web_view.setUrl(QUrl(tv_url))

        # Update title label
        if hasattr(self, 'chart_title_lbl'):
            self.chart_title_lbl.setText(f"\ud83d\udcca  {full_tv_symbol}")


    def execute_buy(self):
        if not self.current_symbol or not self.current_price:
            return
            
        qty = 10 
        msg = QMessageBox()
        msg.setWindowTitle("Confirm Paper Trade")
        msg.setText(f"Execute Paper BUY for {qty} shares of {self.current_symbol} at ₹{self.current_price:,.2f}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            self.engine.load_state()
            success = self.engine.execute_buy(self.current_symbol, qty, self.current_price)
            if success:
                QMessageBox.information(self, "Success", f"Paper BUY executed successfully!")
            else:
                QMessageBox.warning(self, "Error", "Insufficient Balance for Paper Trade.")

    def execute_sell(self):
        if not self.current_symbol or not self.current_price:
            return
            
        qty = 10
        msg = QMessageBox()
        msg.setWindowTitle("Confirm Paper Trade")
        msg.setText(f"Execute Paper SELL for {qty} shares of {self.current_symbol} at ₹{self.current_price:,.2f}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            self.engine.load_state()
            success = self.engine.execute_sell(self.current_symbol, qty, self.current_price)
            if success:
                QMessageBox.information(self, "Success", f"Paper SELL executed successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to SELL. Portfolio check failed.")
