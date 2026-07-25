from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar, QComboBox
from PySide6.QtCore import Qt, QTimer, Signal
from ui.widgets.cards import BestTradeCard, ScanStatsCard
from ui.widgets.tables import TopBuyTable
from datetime import datetime, time
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from config.config import AppConfig
from core.market_regime_engine import MarketRegimeEngine
from core.sector_rotation_engine import SectorRotationEngine
import os
from utils.platform_actions import show_notification

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
        
        lbl_title = QLabel("Market Health Score (%)")
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
        
        self.lbl_regime = QLabel("Waiting...")
        self.lbl_regime.setStyleSheet("color: #FFF; font-weight: bold; font-size: 18px; border: none;")
        self.lbl_regime.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_regime)
        
        self.lbl_details = QLabel("Leader: --\nWeakest: --")
        self.lbl_details.setStyleSheet("color: #AAA; font-size: 12px; border: none;")
        self.lbl_details.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_details)
        
    def update_data(self, regime: str, leader: str, weakest: str):
        color = "#4CAF50" if "Bull" in regime else "#F44336" if "Bear" in regime else "#FF9800"
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
        
        self.lbl_env = QLabel("Waiting...")
        self.lbl_env.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 16px; border: none;")
        self.lbl_env.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_env)
        
        self.lbl_strat = QLabel("--\n--")
        self.lbl_strat.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px; border: none;")
        self.lbl_strat.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_strat)
        
    def update_data(self, strat_info):
        env = strat_info.get("environment", "Unknown")
        strat = strat_info.get("strategy", "--")
        style = strat_info.get("style", "--")
        
        self.lbl_env.setText(env)
        self.lbl_strat.setText(f"{strat}\nStyle: {style}")

class CapitalProtectionCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("Capital Protection (CPE)")
        lbl_title.setStyleSheet("color: #888; font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(lbl_title)
        
        self.lbl_score = QLabel("Safety: --")
        self.lbl_score.setStyleSheet("color: #FFF; font-weight: bold; font-size: 16px; border: none;")
        self.lbl_score.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_score)
        
        self.lbl_status = QLabel("Status: --")
        self.lbl_status.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px; border: none;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)
        
    def update_data(self, cpe_stats):
        score = cpe_stats.get("safety_score", 100)
        cooldown = cpe_stats.get("cooldown_active", False)
        
        self.lbl_score.setText(f"Safety: {score}/100")
        if cooldown:
            self.lbl_score.setStyleSheet("color: #F44336; font-weight: bold; font-size: 16px; border: none;")
            self.lbl_status.setText("Status: BLOCKED (COOLDOWN)")
            self.lbl_status.setStyleSheet("color: #F44336; font-weight: bold; font-size: 14px; border: none;")
        else:
            self.lbl_score.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px; border: none;")
            self.lbl_status.setText("Status: ACTIVE")
            self.lbl_status.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px; border: none;")


from PySide6.QtCore import QThread, Signal

class DashboardScannerWorker(QThread):
    progress = Signal(int)
    finished = Signal(dict)
    
    def run(self):
        try:
            from application.swing_scanner_service import SwingScannerService
            service = SwingScannerService()
            scan_dict = service.execute_swing_scan(progress_callback=self.progress.emit)
            qual = scan_dict.get("qualified_results", [])
            rej = scan_dict.get("rejected_count", 0)
            total = scan_dict.get("total_scanned", 0)
            
            buys = [x for x in qual if "BUY" in x.get("Signal", "")]
            best_trade = buys[0] if buys else {}
            
            market_health = "Neutral (50/100)"
            if total > 0:
                health_score = int((len(buys) / total) * 100) * 2
                health_score = min(100, health_score)
                if health_score > 70:
                    market_health = f"Bullish ({health_score}/100)"
                elif health_score < 30:
                    market_health = f"Bearish ({health_score}/100)"
                else:
                    market_health = f"Neutral ({health_score}/100)"
                    
            self.finished.emit({
                "best_trade": best_trade,
                "top_buys": buys[:5],
                "market_health": market_health,
                "total_scanned": total,
                "qualified": len(qual)
            })
        except Exception as e:
            import traceback
            import logging
            logging.getLogger(__name__).error(f"Dashboard scan error: {e}\n{traceback.format_exc()}")
            self.finished.emit({})


class Dashboard(QWidget):
    navigate_to_chart = Signal(str)
    
    def __init__(self):
        super().__init__()
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
        self.market_breadth_card = MarketBreadthCard()
        self.market_regime_card = MarketRegimeCard()
        
        cards_layout.addWidget(self.market_breadth_card)
        cards_layout.addWidget(self.market_regime_card)
        cards_layout.addStretch()
        layout.addLayout(cards_layout)
        
        # Top Buy Table
        self.top_buy_table = TopBuyTable()
        layout.addWidget(self.top_buy_table)
        
        # Connect Signals for Navigation
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
        
        self.btn_auto_scan = QPushButton("Auto Scan: OFF")
        self.btn_auto_scan.setStyleSheet("background-color: #3D4047; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
        self.btn_auto_scan.clicked.connect(self.toggle_auto_scan)
        
        self.btn_scan = QPushButton("Scan Market")
        self.btn_scan.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px;")
        self.btn_scan.clicked.connect(self.start_scan)
        
        action_layout.addStretch()
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
            self.start_scan() # Trigger immediately
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
        
        self.scanner = DashboardScannerWorker()
        self.scanner.progress.connect(self.update_progress)
        self.scanner.finished.connect(self.scan_finished)
        self.scanner.start()
        
    def update_progress(self, val):
        self.btn_scan.setText(f"Scanning... {val}%")
        self.progress_bar.setValue(val)
        
    def scan_finished(self, results):
        self.last_results = results
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Dashboard Updated")
        logger.info(f"Best Trade: {results.get('best_trade', {}).get('symbol', '--')}")
        logger.info(f"Top BUY Loaded: {len(results.get('top_buys', []))}")
        
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Scan Market")
        self.market_status.setText(get_market_status())
        
        dt_now = datetime.now()
        self.last_scan.setText(f"{dt_now.strftime('%d-%b-%Y')}\n{dt_now.strftime('%H:%M:%S')}")
        
        self.progress_bar.hide()
        
        if self.scanner_status_lbl:
            self.scanner_status_lbl.setText(" Scanner : Ready ")
        
        if hasattr(self, 'best_trade_card'):
            self.best_trade_card.update_data(results.get("best_trade", {}))
        if hasattr(self, 'scan_stats_card'):
            self.scan_stats_card.update_data(results)
        
        # Market Health (Sprint 49)
        mkt_health_str = results.get("market_health", "Neutral (50/100)")
        try:
            strength_val = int(mkt_health_str.split("(")[1].split("/")[0])
            if hasattr(self, 'market_breadth_card'):
                self.market_breadth_card.update_breadth(strength_val)
        except Exception as _e:
            logging.getLogger(__name__).debug("Suppressed exception in dashboard.py:354: %s", _e)
            
        # Market Regime (Sprint 73)
        try:
            regime_engine = MarketRegimeEngine()
            sector_engine = SectorRotationEngine()
            
            regime_obj = regime_engine.get_current_regime()
            if isinstance(regime_obj, dict):
                regime = regime_obj.get("Market Regime", "Unknown")
            else:
                regime = str(regime_obj)
            sector_data = sector_engine.get_sector_data()
            
            if sector_data:
                sectors_sorted = list(sector_data.keys())
                leader = sectors_sorted[0]
                weakest = sectors_sorted[-1]
            else:
                leader = "--"
                weakest = "--"
                
            self.market_regime_card.update_data(regime, leader, weakest)
        except Exception as e:
            logger.error(f"Error updating Market Regime Card: {e}")
            
        # Adaptive Strategy Engine (Sprint 76)
        try:
            from core.adaptive_strategy_engine import AdaptiveStrategyEngine
            ase = AdaptiveStrategyEngine() if not hasattr(AdaptiveStrategyEngine, 'get_instance') else AdaptiveStrategyEngine.get_instance()
            strat_info = ase.get_current_strategy()
            self.adaptive_strategy_card.update_data(strat_info)
        except Exception as e:
            logger.error(f"Error updating Adaptive Strategy Card: {e}")
            
        # Capital Protection Engine (CPE)
        try:
            from strategy.cpe_engine import CapitalProtectionEngine
            cpe = CapitalProtectionEngine.get_instance()
            self.cpe_card.update_data(cpe.get_dashboard_stats())
        except Exception as e:
            logger.error(f"Error updating CPE Card: {e}")
            
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
        """Save symbol to F&O watchlist file."""
        try:
            from ui.watchlist import load_watchlist, save_watchlist
            wl = load_watchlist()
            if symbol not in wl:
                wl.append(symbol)
                save_watchlist(wl)
        except Exception as e:
            print("Watchlist add error:", e)
