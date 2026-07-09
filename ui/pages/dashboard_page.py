from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar, QComboBox
from PySide6.QtCore import Qt, QTimer, Signal
from ui.widgets.cards import BestTradeCard, ScanStatsCard
from ui.widgets.tables import TopBuyTable
from ui.scanner_wrapper import ScannerWrapperThread
from datetime import datetime, time
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from config.config import AppConfig
from core.market_regime_engine import MarketRegimeEngine
from core.sector_rotation_engine import SectorRotationEngine
from application.dashboard_service import DashboardService
import os
import logging
from utils.platform_actions import show_notification

logger = logging.getLogger(__name__)

def get_market_status():
    now = datetime.now().time()
    if time(9, 0) <= now < time(9, 15):
        return "🟡 Market Status : PRE-OPEN"
    elif time(9, 15) <= now < time(15, 30):
        return "🟢 Market Status : OPEN"
    else:
        return "🔴 Market Status : CLOSED"

class MarketBreadthCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("Market Breadth (Nifty 50)")
        lbl_title.setStyleSheet("color: #888; font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(lbl_title)
        
        self.lbl_val = QLabel("Waiting for Scan")
        self.lbl_val.setStyleSheet("color: #FFF; font-weight: bold; font-size: 24px; border: none;")
        self.lbl_val.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_val)
        
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 14px; border: none;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet("QProgressBar { border: none; background: #3D4047; border-radius: 4px; } QProgressBar::chunk { background: #FF9800; border-radius: 4px; }")
        layout.addWidget(self.progress)
        
    def update_breadth(self, strength: int):
        self.lbl_val.setText(str(strength))
        self.progress.setValue(strength)
        
        if strength <= 30:
            status = "Extremely Bearish"
            color = "#F44336"
        elif strength <= 45:
            status = "Bearish"
            color = "#FF5722"
        elif strength <= 55:
            status = "Neutral"
            color = "#FF9800"
        elif strength <= 70:
            status = "Bullish"
            color = "#8BC34A"
        else:
            status = "Extremely Bullish"
            color = "#4CAF50"
            
        self.lbl_status.setText(status)
        self.lbl_status.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px; border: none;")
        self.progress.setStyleSheet(f"QProgressBar {{ border: none; background: #3D4047; border-radius: 4px; }} QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}")

class MarketRegimeCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("Market Regime & Sectors")
        lbl_title.setStyleSheet("color: #888; font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(lbl_title)
        
        self.lbl_regime = QLabel("Waiting for Scan")
        self.lbl_regime.setStyleSheet("color: #FFF; font-weight: bold; font-size: 18px; border: none;")
        self.lbl_regime.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_regime)
        
        self.lbl_details = QLabel("Leader: Waiting for Scan\nWeakest: Waiting for Scan")
        self.lbl_details.setStyleSheet("color: #AAA; font-size: 12px; border: none;")
        self.lbl_details.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_details)
        
    def update_data(self, regime: str, leader: str, weakest: str):
        if regime is None or regime == "Error" or regime == "Unknown":
            regime = "No Data"
        if leader is None or leader == "--" or leader == "Unknown":
            leader = "No Data"
        if weakest is None or weakest == "--" or weakest == "Unknown":
            weakest = "No Data"
            
        color = "#4CAF50" if "Bull" in regime else "#F44336" if "Bear" in regime else "#FF9800" if regime != "No Data" else "#A0A5B1"
        self.lbl_regime.setText(regime.upper())
        self.lbl_regime.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px; border: none;")
        
        self.lbl_details.setText(f"Leader: {leader}\nWeakest: {weakest}")

class AdaptiveStrategyCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("Adaptive Strategy Engine")
        lbl_title.setStyleSheet("color: #888; font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(lbl_title)
        
        self.lbl_env = QLabel("Waiting for Scan")
        self.lbl_env.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 16px; border: none;")
        self.lbl_env.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_env)
        
        self.lbl_strat = QLabel("Strategy: Waiting for Scan\nStyle: Waiting for Scan")
        self.lbl_strat.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px; border: none;")
        self.lbl_strat.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_strat)
        
    def update_data(self, strat_info):
        if not strat_info:
            self.lbl_env.setText("No Data")
            self.lbl_strat.setText("Strategy: No Data\nStyle: No Data")
            return
            
        env = strat_info.get("environment", "No Data") or "No Data"
        strat = strat_info.get("strategy", "No Data") or "No Data"
        style = strat_info.get("style", "No Data") or "No Data"
        
        if env == "Unknown": env = "No Data"
        if strat == "--": strat = "No Data"
        if style == "--": style = "No Data"
        
        self.lbl_env.setText(env)
        self.lbl_strat.setText(f"{strat}\nStyle: {style}")

class Dashboard(QWidget):
    navigate_to_chart = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.service = DashboardService()
        self.scanner_status_lbl = None
        self.config = AppConfig()
        self.config.load()
        
        self.auto_scan_timer = QTimer(self)
        self.auto_scan_timer.timeout.connect(self.start_scan)
        self.is_auto_scan_active = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Market Status Row
        status_layout = QHBoxLayout()
        self.market_status = QLabel(get_market_status())
        self.market_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.last_scan = QLabel("Last Scan:\n--")
        self.last_scan.setObjectName("Secondary")
        self.last_scan.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        status_layout.addWidget(self.market_status)
        status_layout.addStretch()
        status_layout.addWidget(self.last_scan)
        layout.addLayout(status_layout)
        
        # Cards Row
        cards_layout = QHBoxLayout()
        self.best_trade_card = BestTradeCard()
        self.scan_stats_card = ScanStatsCard()
        self.market_breadth_card = MarketBreadthCard()
        self.market_regime_card = MarketRegimeCard()
        self.adaptive_strategy_card = AdaptiveStrategyCard()
        cards_layout.addWidget(self.best_trade_card)
        cards_layout.addWidget(self.scan_stats_card)
        cards_layout.addWidget(self.market_breadth_card)
        cards_layout.addWidget(self.market_regime_card)
        cards_layout.addWidget(self.adaptive_strategy_card)
        layout.addLayout(cards_layout)
        
        # Top Buy Table
        self.top_buy_table = TopBuyTable()
        layout.addWidget(self.top_buy_table)
        
        # Connect Signals for Navigation
        self.best_trade_card.clicked.connect(self.navigate_to_chart.emit)
        self.top_buy_table.symbol_clicked.connect(self.navigate_to_chart.emit)
        self.top_buy_table.add_to_watchlist.connect(self._add_to_watchlist)
        
        # Progress Bar Layout
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        # Bottom Action
        action_layout = QHBoxLayout()
        
        self.btn_diagnostics = QPushButton("Diagnostics")
        self.btn_diagnostics.setStyleSheet("background-color: #3D4047; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
        
        self.btn_auto_scan = QPushButton("Auto Scan: OFF")
        self.btn_auto_scan.setStyleSheet("background-color: #3D4047; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
        self.btn_auto_scan.clicked.connect(self.toggle_auto_scan)
        
        self.btn_scan = QPushButton("Scan Market")
        self.btn_scan.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
        self.btn_scan.clicked.connect(self.start_scan)
        
        action_layout.addStretch()
        action_layout.addWidget(self.btn_diagnostics)
        action_layout.addSpacing(10)
        action_layout.addWidget(self.btn_auto_scan)
        action_layout.addSpacing(10)
        action_layout.addWidget(self.btn_scan)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.scanner = None

    def toggle_auto_scan(self):
        self.is_auto_scan_active = not self.is_auto_scan_active
        if self.is_auto_scan_active:
            self.btn_auto_scan.setText("Auto Scan: ON")
            self.btn_auto_scan.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
            interval_ms = self.config.scan_interval * 1000
            self.auto_scan_timer.start(interval_ms)
            self.start_scan()
        else:
            self.btn_auto_scan.setText("Auto Scan: OFF")
            self.btn_auto_scan.setStyleSheet("background-color: #3D4047; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
            self.auto_scan_timer.stop()
            if not (self.scanner and self.scanner.isRunning()):
                self.market_status.setText(get_market_status())

    def start_scan(self):
        if self.scanner and self.scanner.isRunning():
            return
            
        from market.universe import get_fno_symbols
        fno_count = len(get_fno_symbols())
            
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Scanning... 0%")
        self.market_status.setText(f"🔵 Market Status : SCANNING {fno_count} F&O STOCKS")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.scanner = ScannerWrapperThread()
        self.scanner.progress.connect(self.update_progress)
        self.scanner.finished.connect(self.scan_finished)
        self.scanner.start()
        
    def update_progress(self, val):
        self.btn_scan.setText(f"Scanning... {val}%")
        self.progress_bar.setValue(val)
        
    def scan_finished(self, results):
        self.last_results = results
        logger.info("Dashboard Updated")
        
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Scan Market")
        self.market_status.setText(get_market_status())
        
        dt_now = datetime.now()
        self.last_scan.setText(f"{dt_now.strftime('%d-%b-%Y')}\n{dt_now.strftime('%H:%M:%S')}")
        
        self.progress_bar.hide()
        
        if self.scanner_status_lbl:
            self.scanner_status_lbl.setText(" Scanner : Ready ")
        
        self.best_trade_card.update_data(results.get("best_trade", {}))
        self.scan_stats_card.update_data(results)
        
        # Market Health
        mkt_health_str = results.get("market_health", "Neutral (50/100)")
        try:
            strength_val = int(mkt_health_str.split("(")[1].split("/")[0])
            self.market_breadth_card.update_breadth(strength_val)
        except Exception:
            pass
            
        # Refresh dashboard stats via service (Sprint 73 / Sprint 76 Integration Fix)
        try:
            db_data = self.service.refresh_data()
            self.market_regime_card.update_data(
                db_data.get("market_regime"),
                db_data.get("leader_sector"),
                db_data.get("weakest_sector")
            )
        except Exception as e:
            logger.exception("Error updating Market Regime Card")
            self.market_regime_card.update_data("No Data", "No Data", "No Data")
            
        try:
            from core.adaptive_strategy_engine import AdaptiveStrategyEngine
            ase = AdaptiveStrategyEngine.get_instance()
            strat_info = ase.get_current_strategy()
            self.adaptive_strategy_card.update_data(strat_info)
        except Exception as e:
            logger.exception("Error updating Adaptive Strategy Card")
            self.adaptive_strategy_card.update_data(None)
            
        self.top_buy_table.update_data(results.get("top_buys", []), results.get("detail_map", {}))
        
        # Notifications logic
        best = results.get("best_trade", {})
        sig = best.get("signal", "--")
        sym = best.get("symbol", "--")
        if self.is_auto_scan_active and sig in ["BUY", "STRONG_BUY"]:
            try:
                show_notification("RAHUUL RADAR PRO", f"Best Trade: {sym} ({sig})", subtitle="Auto-Scanner found a setup!")
            except Exception as e:
                print("Notification failed:", e)
                
            from utils.telegram_bot import TelegramBot
            bot = TelegramBot()
            bot.send_alert(sym, sig, best.get("score", 0))

    def _add_to_watchlist(self, symbol: str):
        try:
            from ui.watchlist import load_watchlist, save_watchlist
            wl = load_watchlist()
            if symbol not in wl:
                wl.append(symbol)
                save_watchlist(wl)
        except Exception as e:
            print("Watchlist add error:", e)

# Define DashboardPage alias to ensure compatibility with unit tests referencing DashboardPage
DashboardPage = Dashboard
