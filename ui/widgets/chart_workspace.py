from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QSplitter, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from ui.styles import BG_COLOR, CARD_BG, COLOR_BUY, COLOR_SELL, COLOR_WATCH

from ui.widgets.chart_toolbar import ChartToolbar
from ui.widgets.trade_levels_overlay import TradeLevelsOverlay
from application.chart_workspace_service import ChartWorkspaceService

class MockCandlestickChart(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: #121315; border: 1px solid #3D4047;")
        self.overlay = TradeLevelsOverlay(self)
        self.overlay.move(10, 10)
        self.overlay.hide()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not hasattr(self, 'has_data') or not self.has_data:
            painter.setPen(QColor("#555"))
            painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, "No chart data available")
            return
            
        # Draw grid
        painter.setPen(QPen(QColor("#222"), 1, Qt.DashLine))
        for x in range(0, self.width(), 50):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 50):
            painter.drawLine(0, y, self.width(), y)
            
        # Draw mock candles
        w = self.width()
        h = self.height()
        painter.setPen(QPen(QColor(COLOR_BUY), 1))
        painter.setBrush(QColor(COLOR_BUY))
        
        # Just drawing 3 dummy candles to represent chart
        painter.drawLine(w//2 - 40, h//2 - 20, w//2 - 40, h//2 + 20)
        painter.drawRect(w//2 - 45, h//2 - 10, 10, 20)
        
        painter.setPen(QPen(QColor(COLOR_SELL), 1))
        painter.setBrush(QColor(COLOR_SELL))
        painter.drawLine(w//2, h//2 - 30, w//2, h//2 + 10)
        painter.drawRect(w//2 - 5, h//2 - 20, 10, 30)

    def set_data(self, data):
        self.has_data = True if data else False
        if self.has_data:
            self.overlay.update_overlays(data)
            self.overlay.show()
        else:
            self.overlay.hide()
        self.update()


class ChartWorkspace(QWidget):
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = ChartWorkspaceService()
        self._init_ui()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet(f"background-color: {CARD_BG}; border-bottom: 1px solid #3D4047;")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        self.lbl_company = QLabel("Company")
        self.lbl_company.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.lbl_company.setStyleSheet("color: white;")
        
        self.lbl_symbol = QLabel("SYMBOL")
        self.lbl_symbol.setStyleSheet("color: #aaa;")
        
        self.lbl_sector = QLabel("Sector")
        self.lbl_sector.setStyleSheet("color: #888;")
        
        self.lbl_price = QLabel("₹0.00")
        self.lbl_price.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_price.setStyleSheet("color: white;")
        
        self.lbl_signal = QLabel("WAIT")
        self.lbl_signal.setStyleSheet(f"background-color: {COLOR_WATCH}; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold;")
        
        self.lbl_confidence = QLabel("Conf: 0%")
        self.lbl_confidence.setStyleSheet("color: #aaa;")
        
        self.lbl_market = QLabel("Market: N/A")
        self.lbl_market.setStyleSheet("color: #888;")
        
        self.btn_close = QPushButton("✕ Close Workspace")
        self.btn_close.setStyleSheet("background: transparent; color: #aaa; border: 1px solid #555; padding: 4px 10px; border-radius: 4px;")
        self.btn_close.clicked.connect(self.close_requested.emit)
        
        header_layout.addWidget(self.lbl_company)
        header_layout.addWidget(QLabel("•"))
        header_layout.addWidget(self.lbl_symbol)
        header_layout.addWidget(QLabel("•"))
        header_layout.addWidget(self.lbl_sector)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_price)
        header_layout.addWidget(self.lbl_signal)
        header_layout.addWidget(self.lbl_confidence)
        header_layout.addWidget(self.lbl_market)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.btn_close)
        
        self.main_layout.addWidget(self.header_frame)

        # Toolbar
        self.toolbar = ChartToolbar()
        self.main_layout.addWidget(self.toolbar)

        # Splitter for Chart and Side Panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Left: Chart Area
        self.chart_area = MockCandlestickChart()
        self.splitter.addWidget(self.chart_area)

        # Right: Panels Area
        self.panels_scroll = QScrollArea()
        self.panels_scroll.setWidgetResizable(True)
        self.panels_scroll.setFixedWidth(300)
        self.panels_scroll.setStyleSheet(f"QScrollArea {{ border: none; border-left: 1px solid #3D4047; background-color: {CARD_BG}; }}")
        
        self.panels_container = QWidget()
        self.panels_layout = QVBoxLayout(self.panels_container)
        self.panels_layout.setAlignment(Qt.AlignTop)
        
        self.ai_panel_layout = self._create_panel("AI PANEL")
        self.trade_plan_layout = self._create_panel("TRADE PLAN")
        self.watch_panel_layout = self._create_panel("WATCH PANEL")
        
        self.panels_scroll.setWidget(self.panels_container)
        self.splitter.addWidget(self.panels_scroll)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)

    def _create_panel(self, title):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: #202124; border-radius: 6px; border: 1px solid #3D4047;")
        layout = QVBoxLayout(frame)
        
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet("color: #4A90E2;")
        layout.addWidget(lbl)
        
        self.panels_layout.addWidget(frame)
        return layout

    def _clear_layout(self, layout):
        # Clear all widgets except the first one (the title)
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _add_row(self, layout, key, val, color=None):
        r = QHBoxLayout()
        kl = QLabel(str(key))
        kl.setStyleSheet("color: #aaa;")
        vl = QLabel(str(val))
        vl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        if color:
            vl.setStyleSheet(f"color: {color};")
        else:
            vl.setStyleSheet("color: white;")
        vl.setAlignment(Qt.AlignRight)
        r.addWidget(kl)
        r.addWidget(vl)
        layout.addLayout(r)

    def get_color(self, val_str):
        v = str(val_str).upper()
        if "BUY" in v or "PASS" in v or "APPROVED" in v: return COLOR_BUY
        if "SELL" in v or "FAIL" in v or "REJECTED" in v: return COLOR_SELL
        return COLOR_WATCH

    def load_workspace(self, scan_data: dict):
        parsed = self.service.process_chart_data(scan_data)
        if "error" in parsed:
            self.chart_area.set_data(None)
            return

        h = parsed["header"]
        self.lbl_company.setText(h["company"])
        self.lbl_symbol.setText(h["symbol"])
        self.lbl_sector.setText(h["sector"])
        self.lbl_price.setText(f"₹{h['price']:.2f}")
        self.lbl_signal.setText(h["signal"])
        self.lbl_signal.setStyleSheet(f"background-color: {self.get_color(h['signal'])}; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold;")
        self.lbl_confidence.setText(f"Conf: {h['confidence']}%")
        self.lbl_market.setText(f"Market: {h['market_status']}")

        # AI Panel
        ai = parsed["ai_panel"]
        self._clear_layout(self.ai_panel_layout)
        self._add_row(self.ai_panel_layout, "Trend Score", ai["trend_score"])
        self._add_row(self.ai_panel_layout, "Momentum Score", ai["momentum_score"])
        self._add_row(self.ai_panel_layout, "Structure Score", ai["structure_score"])
        self._add_row(self.ai_panel_layout, "Volume Score", ai["volume_score"])
        self._add_row(self.ai_panel_layout, "Confidence", f"{ai['confidence']}%")
        self._add_row(self.ai_panel_layout, "Institution Grade", ai["institution_grade"])
        self._add_row(self.ai_panel_layout, "Master AI Decision", ai["master_ai"], self.get_color(ai["master_ai"]))

        # Trade Plan
        tp = parsed["trade_plan"]
        self._clear_layout(self.trade_plan_layout)
        self._add_row(self.trade_plan_layout, "Entry", f"₹{tp['entry']:.2f}")
        self._add_row(self.trade_plan_layout, "Stop Loss", f"₹{tp['stop_loss']:.2f}", COLOR_SELL)
        self._add_row(self.trade_plan_layout, "Target-1", f"₹{tp['target_1']:.2f}", COLOR_BUY)
        self._add_row(self.trade_plan_layout, "Target-2", f"₹{tp['target_2']:.2f}", COLOR_BUY)
        self._add_row(self.trade_plan_layout, "Target-3", f"₹{tp['target_3']:.2f}", COLOR_BUY)
        self._add_row(self.trade_plan_layout, "Risk Reward", tp["risk_reward"])
        self._add_row(self.trade_plan_layout, "Position Size Factor", tp["position_size"])

        # Watch Panel
        wp = parsed["watch_panel"]
        self._clear_layout(self.watch_panel_layout)
        self._add_row(self.watch_panel_layout, "Latest Signal", wp["latest_signal"], self.get_color(wp["latest_signal"]))
        self._add_row(self.watch_panel_layout, "Previous Signal", wp["previous_signal"])
        self._add_row(self.watch_panel_layout, "Win Rate", wp["win_rate"])
        self._add_row(self.watch_panel_layout, "Average Return", wp["average_return"])
        self._add_row(self.watch_panel_layout, "Signal Quality", wp["signal_quality"])

        # Set Chart Data
        self.chart_area.set_data(parsed)
