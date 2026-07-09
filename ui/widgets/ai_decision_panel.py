from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QProgressBar, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.styles import CARD_BG, COLOR_BUY, COLOR_SELL, COLOR_WATCH

class AIDecisionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{ background: transparent; }}
            QFrame#SectionFrame {{ background-color: #202124; border-radius: 8px; border: 1px solid #3D4047; }}
            QProgressBar {{ border: 1px solid #3D4047; border-radius: 3px; text-align: center; color: white; }}
            QProgressBar::chunk {{ background-color: {COLOR_BUY}; border-radius: 2px; }}
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)

    def get_color(self, val_str):
        v = str(val_str).upper()
        if "BUY" in v or "PASS" in v or "ELITE" in v or "HIGH" in v or "STRONG" in v or "GOOD" in v or "BULLISH" in v: return COLOR_BUY
        if "SELL" in v or "FAIL" in v or "REJECTED" in v or "WEAK" in v or "BEARISH" in v: return COLOR_SELL
        return COLOR_WATCH

    def _create_section_frame(self, title, color="#4A90E2"):
        frame = QFrame()
        frame.setObjectName("SectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet(f"color: {color}; margin-bottom: 8px;")
        layout.addWidget(lbl)
        return frame, layout

    def _add_row(self, layout, key, val, color=None):
        r = QHBoxLayout()
        kl = QLabel(str(key))
        kl.setStyleSheet("color: #C4C7C5; font-size: 13px;")
        vl = QLabel(str(val))
        vl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        if color:
            vl.setStyleSheet(f"color: {color};")
        else:
            vl.setStyleSheet("color: white;")
        vl.setAlignment(Qt.AlignRight)
        r.addWidget(kl)
        r.addWidget(vl)
        layout.addLayout(r)

    def update_panel(self, data: dict):
        # Clear existing layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if "error" in data:
            lbl = QLabel(data["error"])
            lbl.setStyleSheet("color: #888; font-size: 16px;")
            self.layout.addWidget(lbl)
            return
            
        decision = data.get("decision", "NO TRADE")

        if decision == "NO TRADE":
            # --------------------------------------------------------
            # NO TRADE DISPLAY
            # --------------------------------------------------------
            f1, l1 = self._create_section_frame("FINAL DECISION", color=COLOR_WATCH)
            self._add_row(l1, "Recommendation", "NO TRADE", COLOR_WATCH)
            self._add_row(l1, "Trade Grade", data.get("trade_grade"), COLOR_SELL)
            self.layout.addWidget(f1)
            
            f2, l2 = self._create_section_frame("REASON FOR REJECTION", color="#E24A4A")
            lbl_reason = QLabel(data.get("no_trade_reason", ""))
            lbl_reason.setWordWrap(True)
            lbl_reason.setStyleSheet("color: #E24A4A; font-weight: bold;")
            l2.addWidget(lbl_reason)
            self.layout.addWidget(f2)
            
            f3, l3 = self._create_section_frame("WEAKNESSES IDENTIFIED", color="#E24A4A")
            for reason in data.get("why_selected", []):
                lbl = QLabel(f"• {reason}")
                lbl.setWordWrap(True)
                l3.addWidget(lbl)
            self.layout.addWidget(f3)
            
        else:
            # --------------------------------------------------------
            # DECISION DISPLAY
            # --------------------------------------------------------
            decision_color = COLOR_BUY if decision == "BULLISH" else COLOR_SELL if decision == "BEARISH" else COLOR_WATCH
            
            # FINAL DECISION Header
            f1, l1 = self._create_section_frame("FINAL DECISION", color=decision_color)
            self._add_row(l1, "Recommendation", decision, decision_color)
            
            grade_color = "#9E9E9E"
            tg = str(data.get("trade_grade", "")).upper()
            if "ELITE" in tg: grade_color = "#4CAF50"
            elif "STRONG" in tg: grade_color = "#2196F3"
            elif "GOOD" in tg: grade_color = "#00BCD4"
            elif "WATCH" in tg: grade_color = "#FFC107"
            self._add_row(l1, "Trade Grade", data.get("trade_grade"), grade_color)
            
            score_val = float(data.get("opportunity_score", 0))
            if score_val >= 80: sc_color = "#4CAF50"
            elif score_val >= 70: sc_color = "#2196F3"
            elif score_val >= 60: sc_color = "#FF9800"
            else: sc_color = "#9E9E9E"
            self._add_row(l1, "Opportunity Score", f"{score_val:.1f}", sc_color)
            
            # Confidence Progress Bar
            conf_val = float(data.get('ai_confidence', 0))
            if conf_val >= 90: bar_color = "#4CAF50" # Green
            elif conf_val >= 75: bar_color = "#CDDC39" # Lime
            elif conf_val >= 60: bar_color = "#FFEB3B" # Yellow
            else: bar_color = "#F44336" # Red
            
            pbar_layout = QHBoxLayout()
            kl = QLabel("AI Confidence")
            kl.setStyleSheet("color: #C4C7C5; font-size: 13px;")
            pbar = QProgressBar()
            pbar.setRange(0, 100)
            pbar.setValue(int(conf_val))
            pbar.setStyleSheet(f"QProgressBar {{ border: 1px solid #3D4047; border-radius: 4px; text-align: center; color: white; font-weight: bold; background-color: #2D2F34; min-height: 18px; max-height: 18px; }} QProgressBar::chunk {{ background-color: {bar_color}; border-radius: 3px; }}")
            pbar_layout.addWidget(kl)
            pbar_layout.addWidget(pbar)
            l1.addLayout(pbar_layout)
            
            self._add_row(l1, "Risk Level", data.get("risk_level"), COLOR_SELL if data.get("risk_level") == "HIGH" else "white")
            self._add_row(l1, "Holding Period", data.get("holding_period"))
            self.layout.addWidget(f1)
            
            # TRADE DETAILS
            f2, l2 = self._create_section_frame("TRADE PLAN")
            details = data.get("trade_details", {})
            if decision == "BULLISH" or decision == "WATCH":
                self._add_row(l2, "Entry Price", f"₹{details.get('entry', 0)}")
                self._add_row(l2, "Stop Loss", f"₹{details.get('sl', 0)}", COLOR_SELL)
                self._add_row(l2, "Target 1", f"₹{details.get('target1', 0)}", COLOR_BUY)
                self._add_row(l2, "Target 2", f"₹{details.get('target2', 0)}", COLOR_BUY)
            else:
                self._add_row(l2, "Exit Price", f"₹{details.get('entry', 0)}")
                self._add_row(l2, "Stop Loss (Buyback)", f"₹{details.get('sl', 0)}", COLOR_BUY)
                self._add_row(l2, "Downside Target 1", f"₹{details.get('target1', 0)}", COLOR_SELL)
            self.layout.addWidget(f2)
            
            # WHY SELECTED
            f3, l3 = self._create_section_frame("WHY SELECTED", color="#4CAF50")
            for reason in data.get("why_selected", []):
                lbl = QLabel(f"✓ {reason}")
                lbl.setWordWrap(True)
                l3.addWidget(lbl)
            self.layout.addWidget(f3)
