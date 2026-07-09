import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, 
    QGroupBox, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from datetime import datetime

from strategy.intraday_engine import IntradayEngine
from ai.ai_quality_engine import AIQualityEngine

class ProfessionalTradeWindow(QDialog):
    navigate_to_chart = Signal(str)
    
    def __init__(self, symbol: str, result: dict, provider, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.result = result
        self.provider = provider
        self.engine = IntradayEngine()
        self.ai_engine = AIQualityEngine()
        
        self.setWindowTitle(f"Professional Trade Details - {self.symbol}")
        self.setMinimumWidth(850)
        self.setStyleSheet("""
            QDialog { background-color: #1E2028; color: #FFFFFF; }
            QLabel { color: #FFFFFF; font-size: 14px; }
            QGroupBox { border: 1px solid #3D4047; border-radius: 6px; margin-top: 10px; font-weight: bold; padding: 15px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; color: #888; }
            QPushButton { background-color: #2D3035; border: 1px solid #3D4047; padding: 8px 15px; border-radius: 4px; color: white; }
            QPushButton:hover { background-color: #384252; }
        """)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        self.lbl_symbol = QLabel(self.symbol)
        self.lbl_symbol.setStyleSheet("font-size: 28px; font-weight: bold; color: #2196F3;")
        
        self.lbl_signal = QLabel(self.result.get("signal", "WAIT"))
        sig = self.lbl_signal.text()
        if sig == "BUY":
            self.lbl_signal.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50; background: #1B5E20; padding: 5px 15px; border-radius: 4px;")
        elif sig == "SELL":
            self.lbl_signal.setStyleSheet("font-size: 24px; font-weight: bold; color: #F44336; background: #B71C1C; padding: 5px 15px; border-radius: 4px;")
        else:
            self.lbl_signal.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800; background: #E65100; padding: 5px 15px; border-radius: 4px;")
            
        self.lbl_price = QLabel("LTP: Fetching...")
        self.lbl_price.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFF;")
        
        header_layout.addWidget(self.lbl_symbol)
        header_layout.addWidget(self.lbl_signal)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_price)
        main_layout.addLayout(header_layout)
        
        # Grid Info
        info_group = QGroupBox("Trade Parameters")
        info_grid = QGridLayout()
        
        params = [
            ("Entry Price", self.result.get("entry", 0.0)),
            ("Stop Loss", self.result.get("stop_loss", 0.0)),
            ("Target 1", self.result.get("target_1", 0.0)),
            ("Target 2", self.result.get("target_2", 0.0)),
            ("Risk : Reward", self.result.get("risk_reward", "0:0")),
            ("Score", self.result.get("score", 0)),
            ("Confidence", self.result.get("confidence", "Low")),
            ("Timeframe", "Intraday"),
            ("Signal Expiry Time", self.result.get("time_remaining", "00:00")),
            ("Signal Created Time", self.result.get("created_at", "").split("T")[1][:8] if "T" in self.result.get("created_at", "") else ""),
            ("Market Trend", "Aligned" if self.result.get("trend_aligned", False) else "Opposite")
        ]
        
        row, col = 0, 0
        for name, val in params:
            lbl_name = QLabel(f"{name}:")
            lbl_name.setStyleSheet("color: #888;")
            lbl_val = QLabel(str(val))
            lbl_val.setStyleSheet("font-weight: bold;")
            info_grid.addWidget(lbl_name, row, col * 2)
            info_grid.addWidget(lbl_val, row, col * 2 + 1)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        info_group.setLayout(info_grid)
        main_layout.addWidget(info_group)
        
        # Indicators Breakdown
        ind_group = QGroupBox("Indicator Breakdown")
        self.ind_grid = QGridLayout()
        ind_group.setLayout(self.ind_grid)
        main_layout.addWidget(ind_group)
        
        # Trade Checklist
        check_group = QGroupBox("Trade Checklist")
        self.check_grid = QGridLayout()
        check_group.setLayout(self.check_grid)
        main_layout.addWidget(check_group)
        
        # AI Trade Quality
        ai_group = QGroupBox("🧠 AI TRADE QUALITY")
        ai_group.setStyleSheet("""
            QGroupBox { border: 2px solid #9C27B0; border-radius: 8px; margin-top: 15px; font-weight: bold; padding: 15px; background-color: #241432;}
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #E1BEE7; }
        """)
        self.ai_layout = QVBoxLayout()
        
        self.ai_header = QHBoxLayout()
        self.lbl_ai_grade = QLabel("Grade: --")
        self.lbl_ai_prob = QLabel("Prob: --")
        self.lbl_ai_risk = QLabel("Risk: --")
        self.lbl_ai_rec = QLabel("Recommendation: --")
        
        for lbl in [self.lbl_ai_grade, self.lbl_ai_prob, self.lbl_ai_risk, self.lbl_ai_rec]:
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; border-radius: 4px; background: #3D2352; color: #FFF;")
            self.ai_header.addWidget(lbl)
            
        self.ai_layout.addLayout(self.ai_header)
        
        self.lbl_ai_verdict = QLabel("Verdict: --")
        self.lbl_ai_verdict.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFF; margin-top: 10px;")
        self.ai_layout.addWidget(self.lbl_ai_verdict)
        
        self.ai_reasons_layout = QVBoxLayout()
        self.ai_layout.addLayout(self.ai_reasons_layout)
        
        ai_group.setLayout(self.ai_layout)
        main_layout.addWidget(ai_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_chart = QPushButton("📈 Open Chart")
        btn_chart.clicked.connect(self.open_chart)
        btn_watch = QPushButton("⭐ Add to Watchlist")
        btn_copy = QPushButton("📋 Copy Trade")
        btn_copy.clicked.connect(self.copy_trade)
        btn_journal = QPushButton("📒 Save to Journal")
        btn_alert = QPushButton("🔔 Create Alert")
        btn_close = QPushButton("❌ Close")
        btn_close.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_chart)
        btn_layout.addWidget(btn_watch)
        btn_layout.addWidget(btn_copy)
        btn_layout.addWidget(btn_journal)
        btn_layout.addWidget(btn_alert)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        
        main_layout.addLayout(btn_layout)
        
        # Scanner thread lock
        self._is_scanning = False
        
    def _create_badge(self, text, state):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        if state == "PASS":
            lbl.setStyleSheet("background-color: #1B5E20; color: #4CAF50; font-weight: bold; padding: 4px; border-radius: 4px;")
        elif state == "FAIL":
            lbl.setStyleSheet("background-color: #B71C1C; color: #F44336; font-weight: bold; padding: 4px; border-radius: 4px;")
        else:
            lbl.setStyleSheet("background-color: #E65100; color: #FF9800; font-weight: bold; padding: 4px; border-radius: 4px;")
        return lbl

    def load_data(self):
        # Fetch fresh data to calculate indicators
        try:
            ohlcv = self.provider.get_ohlcv(self.symbol, "5m", "2d")
            if not ohlcv or len(ohlcv) < 50:
                self.lbl_price.setText("LTP: No Data")
                return
                
            self.lbl_price.setText(f"LTP: ₹{ohlcv[-1].close:.2f}")
            
            df = pd.DataFrame([{'Open': c.open, 'High': c.high, 'Low': c.low, 'Close': c.close, 'Volume': c.volume} for c in ohlcv])
            
            # Recalculate indicators inline to avoid modifying engine
            df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
            df['VWAP'] = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
            df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            df = self.engine.calculate_adx(df)
            df['ATR'] = self.engine.calculate_atr(df)
            df = self.engine.calculate_supertrend(df)
            df['Vol_MA'] = df['Volume'].rolling(window=20).mean()
            
            latest = df.iloc[-1]
            sig = self.result.get("signal", "WAIT")
            
            # Determine Pass/Fail/Neutral based on the signal generated
            def get_state(cond_buy, cond_sell):
                if sig == "BUY": return "PASS" if cond_buy else "FAIL"
                if sig == "SELL": return "PASS" if cond_sell else "FAIL"
                return "NEUTRAL"
                
            inds = [
                ("EMA 9", get_state(latest['Close'] > latest['EMA9'], latest['Close'] < latest['EMA9'])),
                ("EMA 20", get_state(latest['EMA9'] > latest['EMA20'], latest['EMA9'] < latest['EMA20'])),
                ("VWAP", get_state(latest['Close'] > latest['VWAP'], latest['Close'] < latest['VWAP'])),
                ("MACD", get_state(latest['MACD'] > latest['Signal_Line'], latest['MACD'] < latest['Signal_Line'])),
                ("RSI", get_state(55 <= latest['RSI'] <= 70, latest['RSI'] < 45)),
                ("ADX", get_state(latest['ADX'] > 20, latest['ADX'] > 20)),
                ("ATR", "PASS" if latest['ATR'] > 0 else "FAIL"),
                ("Supertrend", get_state(latest['Supertrend_Direction'] == 1, latest['Supertrend_Direction'] == -1)),
                ("Volume", get_state(latest['Volume'] > latest['Vol_MA'], latest['Volume'] > latest['Vol_MA']))
            ]
            
            r, c = 0, 0
            for name, state in inds:
                lbl_n = QLabel(name)
                lbl_n.setStyleSheet("color: #CCC;")
                self.ind_grid.addWidget(lbl_n, r, c * 2)
                self.ind_grid.addWidget(self._create_badge(state, state), r, c * 2 + 1)
                c += 1
                if c > 2:
                    c = 0
                    r += 1
                    
            # Checklist
            checks = [
                ("Trend Alignment", "PASS" if self.result.get("trend_aligned", False) else "FAIL"),
                ("Momentum", "PASS" if latest['ADX'] > 20 else "FAIL"),
                ("Volume Confirmation", get_state(latest['Volume'] > latest['Vol_MA'], latest['Volume'] > latest['Vol_MA'])),
                ("Risk Acceptable", "PASS" if self.result.get("confidence") in ["High", "Very High"] else "FAIL"),
                ("Market Direction", "PASS" if self.result.get("trend_aligned", False) else "FAIL"),
                ("Overall Trade Quality", "PASS" if self.result.get("score", 0) >= 70 else "FAIL")
            ]
            
            r, c = 0, 0
            for name, state in checks:
                lbl_n = QLabel(name)
                self.check_grid.addWidget(lbl_n, r, c * 2)
                self.check_grid.addWidget(self._create_badge(state, state), r, c * 2 + 1)
                c += 1
                if c > 2:
                    c = 0
                    r += 1
                    
            # AI Validation
            ai_res = self.ai_engine.validate(self.result, latest)
            
            # Colors
            def get_color(grade):
                if grade in ["A+", "A"]: return "#4CAF50" # Green
                if grade == "B": return "#FFC107" # Yellow
                if grade == "C": return "#FF9800" # Orange
                return "#F44336" # Red
                
            c_hex = get_color(ai_res['grade'])
            
            self.lbl_ai_grade.setText(f"Grade: {ai_res['grade']}")
            self.lbl_ai_grade.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 5px; border-radius: 4px; background: {c_hex}; color: #000;")
            
            self.lbl_ai_rec.setText(f"{ai_res['recommendation']}")
            self.lbl_ai_rec.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 5px; border-radius: 4px; background: {c_hex}; color: #000;")
            
            self.lbl_ai_prob.setText(f"Prob: {ai_res['probability']}")
            self.lbl_ai_risk.setText(f"Risk: {ai_res['risk']}")
            
            self.lbl_ai_verdict.setText(f"Overall Verdict: This trade satisfies {ai_res['passed']} / {ai_res['total']} Institutional conditions.")
            
            for reason in ai_res['reasons']:
                lbl_r = QLabel(reason)
                if reason.startswith("✓"):
                    lbl_r.setStyleSheet("color: #4CAF50; font-weight: bold;")
                else:
                    lbl_r.setStyleSheet("color: #F44336;")
                self.ai_reasons_layout.addWidget(lbl_r)
                    
        except Exception as e:
            print(f"Error loading indicators for trade window: {e}")
            
    def open_chart(self):
        self.navigate_to_chart.emit(self.symbol)
        self.accept()
        
    def copy_trade(self):
        trade_str = f"Trade: {self.symbol} | {self.result.get('signal')} | Entry: {self.result.get('entry')} | SL: {self.result.get('stop_loss')} | TP1: {self.result.get('target_1')}"
        QApplication.clipboard().setText(trade_str)
