"""
Stock Detail Popup — shows full trade setup (Entry, SL, Targets, RR)
with option to add to Watchlist and open chart.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette


class StockDetailPopup(QDialog):
    open_chart = Signal(str)
    add_to_watchlist = Signal(str)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.symbol = data.get("symbol", "--")
        self.setWindowTitle(f"Trade Setup — {self.symbol}")
        self.setFixedSize(850, 650)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1C23;
                color: white;
            }
            QLabel { color: white; }
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Symbol + Signal header ─────────────────────────────────────────
        header = QHBoxLayout()
        sym_lbl = QLabel(self.symbol)
        sym_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF9800;")

        signal = data.get("signal", "--")
        sig_lbl = QLabel(f"  {signal}")
        if signal in ("BUY", "STRONG_BUY"):
            sig_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        elif signal == "SELL":
            sig_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #F44336;")
        else:
            sig_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800;")

        header.addWidget(sym_lbl)
        header.addWidget(sig_lbl)
        header.addStretch()
        layout.addLayout(header)

        # ── Setup TabWidget ────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3D4047; border-radius: 4px; }
            QTabBar::tab {
                background: #1A1C23;
                color: #888;
                padding: 8px 16px;
                border: 1px solid transparent;
            }
            QTabBar::tab:selected {
                color: white;
                border-bottom: 2px solid #2196F3;
                font-weight: bold;
            }
        """)
        
        tab_setup = QWidget()
        tab_breakdown = QWidget()
        tabs.addTab(tab_setup, "Trade Setup")
        tabs.addTab(tab_breakdown, "Radar Analysis")
        
        from PySide6.QtWidgets import QScrollArea
        
        # ── Trade Setup Tab ───────────────────────────────────────────────
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        setup_layout = QHBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        setup_layout.addLayout(left_col)
        setup_layout.addLayout(right_col)
        
        tab_setup_layout = QVBoxLayout(tab_setup)
        tab_setup_layout.setContentsMargins(0, 0, 0, 0)
        tab_setup_layout.addWidget(scroll_area)
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #22242D;
                border: 1px solid #3D4047;
                border-radius: 8px;
                padding: 8px;
            }
            QLabel { color: #CCC; }
        """)
        grid = QGridLayout(card)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        def row(grid_layout, r, label, value, val_color=None):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #888; font-size: 13px;")
            val = QLabel(str(value))
            style = "font-size: 14px; font-weight: bold;"
            if val_color:
                style += f" color: {val_color};"
            val.setStyleSheet(style)
            grid_layout.addWidget(lbl, r, 0)
            grid_layout.addWidget(val, r, 1)

        entry  = data.get("entry",   "N/A")
        sl     = data.get("sl",      "N/A")
        t1     = data.get("target1", "N/A")
        t2     = data.get("target2", "N/A")
        score  = data.get("score",   "N/A")
        rr     = data.get("rr",      "1:2")
        grade  = data.get("quality_grade", "N/A")

        row(grid, 0, "Entry Price",  f"₹ {entry}",  "#FFFFFF")
        row(grid, 1, "Stop Loss",    f"₹ {sl}",     "#F44336")
        row(grid, 2, "Target 1",     f"₹ {t1}",     "#4CAF50")
        row(grid, 3, "Target 2",     f"₹ {t2}",     "#00BCD4")
        row(grid, 4, "Risk/Reward",  rr,             "#FF9800")
        row(grid, 5, "Radar Score",  score,          "#9C27B0")
        
        grade_color = "#4CAF50" if grade in ("A+", "A") else "#FF9800" if grade == "B" else "#F44336"
        row(grid, 6, "Quality Grade", grade, grade_color)
        
        rs_score = data.get("rs_score", "--")
        rs_color = "#4CAF50" if rs_score != "--" and float(rs_score) >= 80 else "#F44336" if rs_score != "--" and float(rs_score) <= 40 else "#FF9800"
        row(grid, 7, "Relative Strength", f"{rs_score} / 100", rs_color)
        row(grid, 8, "Ranks (RS / Mkt / Sec)", f"{data.get('rs_rank', '--')} / {data.get('market_rank', '--')} / {data.get('sector_rank', '--')}", "#00BCD4")

        left_col.addWidget(card)

        # AI Trading Assistant: "Why BUY?" Checklist (Sprint 50)
        reasons = data.get("reasons", [])
        if reasons:
            ai_lbl = QLabel(f"🤖 Why {signal}? (AI Assistant)")
            ai_lbl.setStyleSheet("color: #FF9800; font-size: 14px; font-weight: bold; margin-top: 10px;")
            setup_layout.addWidget(ai_lbl)
            
            reasons_card = QFrame()
            reasons_card.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px; padding: 4px;")
            r_layout = QVBoxLayout(reasons_card)
            r_layout.setSpacing(4)
            r_layout.setContentsMargins(10, 10, 10, 10)
            
            # Display up to 6 key reasons to avoid clutter
            display_reasons = [r for r in reasons if "Weight" not in r and "Score" not in r and "Decision" not in r]
            for r in display_reasons[:6]:
                r_lbl = QLabel(f"✓ {r}")
                r_lbl.setStyleSheet("color: #CCC; font-size: 12px;")
                r_layout.addWidget(r_lbl)
                
            right_col.addWidget(ai_lbl)
            right_col.addWidget(reasons_card)

        # ── Option Chain Intelligence (Sprint 47) ──
        oi_activity = data.get("oi_activity")
        if oi_activity:
            oi_lbl = QLabel("📊 Option Chain Intelligence")
            oi_lbl.setStyleSheet("color: #00BCD4; font-size: 14px; font-weight: bold; margin-top: 10px;")
            right_col.addWidget(oi_lbl)
            
            oi_card = QFrame()
            oi_card.setStyleSheet(card.styleSheet())
            oi_grid = QGridLayout(oi_card)
            oi_grid.setHorizontalSpacing(24)
            oi_grid.setVerticalSpacing(8)
            
            row(oi_grid, 0, "Max Pain Strike", f"₹ {oi_activity.get('max_pain', 'N/A')}", "#FF9800")
            row(oi_grid, 1, "PCR (OI)", f"{oi_activity.get('pcr_oi', 'N/A')}", "#4CAF50" if oi_activity.get('pcr_oi', 1) < 0.8 else "#F44336")
            row(oi_grid, 2, "Activity Detection", f"{oi_activity.get('emoji', '')} {oi_activity.get('activity', 'N/A')}", "#FFF")
            
            fno_score = oi_activity.get('fno_strength', 50)
            fno_color = "#4CAF50" if fno_score >= 70 else "#F44336" if fno_score <= 30 else "#FF9800"
            row(oi_grid, 3, "F&O Strength", f"{fno_score} / 100", fno_color)
            
            right_col.addWidget(oi_card)

        # ── Professional Risk Manager (Sprint 75) ──
        try:
            e_p = float(entry) if entry != "N/A" else 0
            s_l = float(sl) if sl != "N/A" else 0
            
            if e_p > 0 and s_l > 0:
                risk_data = data.get("risk_data")
                if not risk_data:
                    from core.risk_manager import RiskManager
                    risk_data = RiskManager.get_instance().position_engine.calculate_size(e_p, s_l, "SWING")
                    
                actual_risk = risk_data.get("risk_amount", 0)
                suggested_qty = risk_data.get("recommended_qty", 0)
                cap_req = risk_data.get("capital_required", 0)
                classification = risk_data.get("classification", "N/A")
                
                class_color = "#4CAF50"
                if classification == "Medium Risk": class_color = "#FF9800"
                elif classification in ["High Risk", "Very High Risk"]: class_color = "#F44336"
                
                risk_lbl = QLabel("🛡️ Professional Risk Manager")
                risk_lbl.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold; margin-top: 10px;")
                right_col.addWidget(risk_lbl)
                
                risk_card = QFrame()
                risk_card.setStyleSheet(card.styleSheet())
                risk_grid = QGridLayout(risk_card)
                risk_grid.setHorizontalSpacing(24)
                risk_grid.setVerticalSpacing(8)
                
                row(risk_grid, 0, "Capital Required", f"₹ {cap_req:,.0f}", "#888")
                row(risk_grid, 1, "Risk Amount (Loss)", f"₹ {actual_risk:,.0f}", "#F44336")
                row(risk_grid, 2, "Recommended Qty", f"{suggested_qty} Shares", "#4CAF50")
                row(risk_grid, 3, "Risk Classification", classification, class_color)
                
                right_col.addWidget(risk_card)
        except Exception as e:
            pass

        tip = QLabel("💡 Tip: Buy ATM Call option. Use 30-40% premium drop as SL.")
        tip.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        tip.setWordWrap(True)
        left_col.addWidget(tip)
        
        left_col.addStretch()
        right_col.addStretch()

        # ── Radar Analysis Tab (Sprint 46) ───────────────────────────────────────────
        breakdown_layout = QVBoxLayout(tab_breakdown)
        bd_card = QFrame()
        bd_card.setStyleSheet(card.styleSheet())
        bd_grid = QGridLayout(bd_card)
        bd_grid.setHorizontalSpacing(20)
        bd_grid.setVerticalSpacing(12)
        
        bd_data = data.get("breakdown_detail", {})
        radar_data = bd_data.get("Radar_Analysis", {})
        
        row_idx = 0
        if not radar_data:
            bd_grid.addWidget(QLabel("No radar analysis data available."), 0, 0)
        else:
            for cat, status in radar_data.items():
                cat_lbl = QLabel(cat)
                cat_lbl.setStyleSheet("color: #CCC; font-size: 13px; font-weight: bold;")
                
                status_lbl = QLabel(str(status))
                status_lbl.setStyleSheet("color: #FFF; font-size: 13px; font-weight: bold;")
                
                bd_grid.addWidget(cat_lbl, row_idx, 0)
                bd_grid.addWidget(status_lbl, row_idx, 1, Qt.AlignLeft)
                row_idx += 1
                
        # Also show the Engine weights breakdown at the bottom
        weights_lbl = QLabel("Engine Scores")
        weights_lbl.setStyleSheet("color: #888; font-size: 12px; font-weight: bold; margin-top: 10px;")
        bd_grid.addWidget(weights_lbl, row_idx, 0, 1, 2)
        row_idx += 1
        
        for cat, details in bd_data.items():
            if cat == "Radar_Analysis":
                continue
            cat_lbl = QLabel(cat)
            cat_lbl.setStyleSheet("color: #888; font-size: 12px;")
            score_str = f"{details.get('got', 0)} / {details.get('max', 0)} {details.get('status', '')}"
            score_lbl = QLabel(score_str)
            score_lbl.setStyleSheet("color: #888; font-size: 12px;")
            bd_grid.addWidget(cat_lbl, row_idx, 0)
            bd_grid.addWidget(score_lbl, row_idx, 1, Qt.AlignLeft)
            row_idx += 1
                
        breakdown_layout.addWidget(bd_card)
        
        confidence = data.get("confidence", 0.0)
        conf_lbl = QLabel(f"Confidence: {confidence}%")
        conf_lbl.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;" if confidence >= 60 else "color: #FF9800; font-size: 14px; font-weight: bold;")
        breakdown_layout.addWidget(conf_lbl)
        
        breakdown_layout.addStretch()

        layout.addWidget(tabs)

        # ── Buttons ────────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()

        btn_watchlist = QPushButton("⭐ Add to Watchlist")
        btn_watchlist.setStyleSheet("background-color: #FF9800; color: white;")
        btn_watchlist.clicked.connect(self._on_add_watchlist)

        btn_chart = QPushButton("📈 Open Chart")
        btn_chart.setStyleSheet("background-color: #2196F3; color: white;")
        btn_chart.clicked.connect(self._on_open_chart)

        btn_close = QPushButton("Close")
        btn_close.setStyleSheet("background-color: #3D4047; color: white;")
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(btn_watchlist)
        btn_layout.addWidget(btn_chart)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def _on_add_watchlist(self):
        self.add_to_watchlist.emit(self.symbol)
        QMessageBox.information(self, "Watchlist", f"{self.symbol} added to Watchlist! ⭐")

    def _on_open_chart(self):
        self.open_chart.emit(self.symbol)
        self.accept()
