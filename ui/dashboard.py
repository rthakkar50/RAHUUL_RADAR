from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QProgressBar, QComboBox, QScrollArea, QGridLayout
from PySide6.QtCore import Qt, QTimer, Signal
from ui.widgets.cards import BestTradeCard, ScanStatsCard
from ui.widgets.tables import TopBuyTable, TopSellTable, TopWatchTable
from ui.widgets.portfolio_summary import PortfolioSummary
from ui.widgets.ai_decision_panel import AIDecisionPanel
from ui.widgets.system_health_widget import SystemHealthWidget
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
            
            buys = [x for x in qual if "BUY" in str(x.get("Signal", x.get("signal", ""))).upper()]
            strong_buys = [x for x in qual if "STRONG" in str(x.get("Signal", x.get("signal", ""))).upper()]
            sells = [x for x in qual if "SELL" in str(x.get("Signal", x.get("signal", ""))).upper()]
            watches = [x for x in qual if any(w in str(x.get("Signal", x.get("signal", ""))).upper() for w in ["WATCH", "HOLD", "NEUTRAL", "NO TRADE"])]
            
            best_trade = buys[0] if buys else (qual[0] if qual else {})
            
            scores = [float(x.get("Score", x.get("score", 0))) for x in qual if x.get("Score", x.get("score")) is not None]
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0
            
            scan_stats = {
                "total": total if total > 0 else "No Data",
                "buy": len(buys) if total > 0 else "No Data",
                "strong_buy": len(strong_buys) if total > 0 else "No Data",
                "watch": len(watches) if total > 0 else "No Data",
                "sell": len(sells) if total > 0 else "No Data",
                "avg_score": avg_score if total > 0 else "No Data"
            }
            
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
                "top_sells": sells[:5],
                "top_watches": watches[:5],
                "scan_stats": scan_stats,
                "market_health": market_health,
                "total_scanned": total,
                "qualified": len(qual),
                "detail_map": scan_dict.get("detail_map", {})
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
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 1. Market Status Row
        status_layout = QHBoxLayout()
        self.market_status = QLabel(get_market_status())
        self.market_status.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.last_scan = QLabel("Last Scan:\n--")
        self.last_scan.setObjectName("Secondary")
        self.last_scan.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        status_layout.addWidget(self.market_status)
        status_layout.addStretch()
        status_layout.addWidget(self.last_scan)
        main_layout.addLayout(status_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 2. Cards Row (Scanner Summary & Overview)
        cards_grid = QGridLayout()
        self.scan_stats_card = ScanStatsCard()
        self.best_trade_card = BestTradeCard()
        self.market_breadth_card = MarketBreadthCard()
        self.market_regime_card = MarketRegimeCard()
        self.adaptive_strategy_card = AdaptiveStrategyCard()
        self.cpe_card = CapitalProtectionCard()
        
        cards_grid.addWidget(self.scan_stats_card, 0, 0)
        cards_grid.addWidget(self.best_trade_card, 0, 1)
        cards_grid.addWidget(self.market_breadth_card, 0, 2)
        cards_grid.addWidget(self.market_regime_card, 1, 0)
        cards_grid.addWidget(self.adaptive_strategy_card, 1, 1)
        cards_grid.addWidget(self.cpe_card, 1, 2)
        layout.addLayout(cards_grid)
        
        # 3. Top BUY Table
        self.top_buy_table = TopBuyTable()
        layout.addWidget(self.top_buy_table)
        
        # 4. Top SELL Table
        self.top_sell_table = TopSellTable()
        layout.addWidget(self.top_sell_table)
        
        # 5. Top WATCH Table
        self.top_watch_table = TopWatchTable()
        layout.addWidget(self.top_watch_table)
        
        # Connect Signals for Navigation
        for table in (self.top_buy_table, self.top_sell_table, self.top_watch_table):
            table.symbol_clicked.connect(self.navigate_to_chart.emit)
            table.add_to_watchlist.connect(self._add_to_watchlist)
            
        # 6. Portfolio Summary & 7. AI Summary
        summary_row = QHBoxLayout()
        summary_row.setSpacing(20)
        
        port_frame = QFrame()
        port_frame.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        port_layout = QVBoxLayout(port_frame)
        port_title = QLabel("PORTFOLIO SUMMARY")
        port_title.setStyleSheet("color: #888; font-weight: bold; font-size: 14px; border: none;")
        port_layout.addWidget(port_title)
        self.portfolio_summary = PortfolioSummary()
        port_layout.addWidget(self.portfolio_summary)
        summary_row.addWidget(port_frame, 1)
        
        ai_frame = QFrame()
        ai_frame.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px;")
        ai_layout = QVBoxLayout(ai_frame)
        ai_title = QLabel("AI SUMMARY")
        ai_title.setStyleSheet("color: #888; font-weight: bold; font-size: 14px; border: none;")
        ai_layout.addWidget(ai_title)
        self.ai_summary_panel = AIDecisionPanel()
        ai_layout.addWidget(self.ai_summary_panel)
        summary_row.addWidget(ai_frame, 1)
        
        layout.addLayout(summary_row)
        
        # 8. System Health
        health_frame = QFrame()
        health_frame.setStyleSheet("background-color: #22242D; border: 1px solid #3D4047; border-radius: 8px; padding: 10px;")
        health_layout = QHBoxLayout(health_frame)
        self.system_health = SystemHealthWidget()
        health_layout.addWidget(self.system_health)
        layout.addWidget(health_frame)
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
        
        # Progress Bar Layout
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)
        
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
        
        main_layout.addLayout(action_layout)
        
        self.scanner = None
        self.refresh_backend_services()

    def refresh_backend_services(self):
        if hasattr(self, 'portfolio_summary'):
            try:
                from application.portfolio_service import PortfolioService
                ps = PortfolioService()
                self.portfolio_summary.update_summary(ps.get_summary())
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error updating Portfolio Summary: {e}")
                self.portfolio_summary.update_summary({})
                
        if hasattr(self, 'system_health'):
            try:
                self.system_health.refresh_health()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error updating System Health: {e}")

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
            self.scan_stats_card.update_data(results.get("scan_stats", results))
        
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
                
            if hasattr(self, 'market_regime_card'):
                self.market_regime_card.update_data(regime, leader, weakest)
        except Exception as e:
            logger.error(f"Error updating Market Regime Card: {e}")
            
        # Adaptive Strategy Engine (Sprint 76)
        try:
            from core.adaptive_strategy_engine import AdaptiveStrategyEngine
            ase = AdaptiveStrategyEngine() if not hasattr(AdaptiveStrategyEngine, 'get_instance') else AdaptiveStrategyEngine.get_instance()
            strat_info = ase.get_current_strategy()
            if hasattr(self, 'adaptive_strategy_card'):
                self.adaptive_strategy_card.update_data(strat_info)
        except Exception as e:
            logger.error(f"Error updating Adaptive Strategy Card: {e}")
            
        # Capital Protection Engine (CPE)
        try:
            from strategy.cpe_engine import CapitalProtectionEngine
            cpe = CapitalProtectionEngine.get_instance()
            if hasattr(self, 'cpe_card'):
                self.cpe_card.update_data(cpe.get_dashboard_stats())
        except Exception as e:
            logger.error(f"Error updating CPE Card: {e}")
            
        self.top_buy_table.update_data(results.get("top_buys", []), results.get("detail_map", {}))
        if hasattr(self, 'top_sell_table'):
            self.top_sell_table.update_data(results.get("top_sells", []), results.get("detail_map", {}))
        if hasattr(self, 'top_watch_table'):
            self.top_watch_table.update_data(results.get("top_watches", []), results.get("detail_map", {}))
            
        best = results.get("best_trade", {})
        if best and hasattr(self, 'ai_summary_panel'):
            try:
                from application.decision_explanation_service import DecisionExplanationService
                des = DecisionExplanationService()
                parsed = des.extract_decision_data(best)
                self.ai_summary_panel.update_panel(parsed)
            except Exception as e:
                logger.error(f"Error updating AI Summary: {e}")
                self.ai_summary_panel.update_panel({})
        elif hasattr(self, 'ai_summary_panel'):
            self.ai_summary_panel.update_panel({})
            
        self.refresh_backend_services()
        
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
