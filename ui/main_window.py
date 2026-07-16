import logging
from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QStackedWidget, QMessageBox, QScrollArea
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QRect
from ui.dashboard import Dashboard
from ui.backtest import BacktestWindow
from ui.journal import JournalScreen
from ui.settings import SettingsScreen
from ui.diagnostics import DiagnosticsScreen
from ui.charts import ChartScreen
from ui.portfolio import PortfolioPage
from ui.heatmap import HeatmapScreen
from ui.analytics_screen import AnalyticsScreen
from ui.pages.swing_scanner_page import SwingScannerPage
from ui.pages.intraday_scanner_page import IntradayScannerPage
from ui.option_chain_page import OptionChainPage
from ui.trfa_page import TRFAPage
from ui.ptve_page import PTVEPage
from ui.watchlist import WatchlistScreen
from ui.performance_screen import PerformanceScreen
from ui.live_trades_page import LiveTradesPage
from ui.pages.active_trading_scanner_page import ActiveTradingScannerPage
from ui.pages.paper_trading_dashboard import PaperTradingDashboard
from strategy.swing_engine import SwingEngine
from strategy.intraday_engine import IntradayEngine
from strategy.option_scalping_engine import OptionScalpingEngine
from application.navigation_manager import NavigationManager
from ui.styles import GLOBAL_STYLE, CARD_BG, BTN_BLUE, BG_COLOR
import os
import sys
import platform

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from config.config import AppConfig
        self.config = AppConfig()
        self.config.load()
        
        self.is_pro = True # Hardcoded to PRO mode permanently
        
        if self.is_pro:
            self.setWindowTitle("RAHUUL RADAR PRO")
        else:
            self.setWindowTitle("RAHUUL RADAR (Free Edition)")
        self.resize(1000, 700)
        self.setStyleSheet(GLOBAL_STYLE)
        
        from config.settings import resource_path
        icon_path = resource_path(os.path.join('ui', 'assets', 'logo.jpg'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create Menu Bar
        self.create_menus()
        
        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setFixedWidth(200)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setStyleSheet("QScrollArea { border: none; border-right: 1px solid #3D4047; }")
        
        sidebar = QFrame()
        sidebar.setStyleSheet(f"background-color: {CARD_BG};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        logo_lbl = QLabel("RAHUUL RADAR")
        logo_lbl.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 20px;")
        logo_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_lbl)
        
        # Highlight Indicator (Animated Background)
        self.indicator = QFrame(sidebar)
        self.indicator.setStyleSheet(f"background-color: {BTN_BLUE}; border-left: 4px solid #64B5F6; border-radius: 4px;")
        self.indicator.hide() # Hide until first layout calculation
        
        # Sidebar buttons
        self.btn_dashboard = self.create_nav_btn("Dashboard")
        self.btn_swing = self.create_nav_btn("Swing Scanner")
        self.btn_intraday = self.create_nav_btn("Active Trading Scanner")
        self.btn_option_chain = self.create_nav_btn("Option Chain")
        self.btn_trfa = self.create_nav_btn("Forensic Analysis")
        self.btn_ptve = self.create_nav_btn("Paper Trading Validation")
        self.btn_heatmap = self.create_nav_btn("Heatmap")
        self.btn_charts = self.create_nav_btn("Charts")
        self.btn_portfolio = self.create_nav_btn("Portfolio")
        self.btn_analytics = self.create_nav_btn("Analytics")
        self.btn_watchlist = self.create_nav_btn("Watchlist")
        self.btn_journal = self.create_nav_btn("Journal")
        self.btn_backtest = self.create_nav_btn("Backtest")
        self.btn_performance = self.create_nav_btn("Performance")
        self.btn_diagnostics = self.create_nav_btn("Diagnostics")
        self.btn_settings = self.create_nav_btn("Settings")
        self.btn_live_trades = self.create_nav_btn("Live Trades")
        self.btn_paper_dashboard = self.create_nav_btn("Paper Dashboard")
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_swing)
        sidebar_layout.addWidget(self.btn_intraday)
        sidebar_layout.addWidget(self.btn_option_chain)
        sidebar_layout.addWidget(self.btn_trfa)
        sidebar_layout.addWidget(self.btn_ptve)
        sidebar_layout.addWidget(self.btn_heatmap)
        sidebar_layout.addWidget(self.btn_charts)
        sidebar_layout.addWidget(self.btn_portfolio)
        sidebar_layout.addWidget(self.btn_analytics)
        sidebar_layout.addWidget(self.btn_watchlist)
        sidebar_layout.addWidget(self.btn_journal)
        sidebar_layout.addWidget(self.btn_backtest)
        sidebar_layout.addWidget(self.btn_performance)
        sidebar_layout.addWidget(self.btn_diagnostics)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addWidget(self.btn_live_trades)
        sidebar_layout.addWidget(self.btn_paper_dashboard)
        sidebar_layout.addStretch()
        
        sidebar_scroll.setWidget(sidebar)
        main_layout.addWidget(sidebar_scroll)
        
        # Stacked Widget for screens
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Initialize Screens
        self.dashboard = Dashboard()
        self.swing_page = SwingScannerPage()
        self.intraday_page = ActiveTradingScannerPage()
        self.option_chain = OptionChainPage()
        self.trfa_page = TRFAPage()
        self.ptve_page = PTVEPage()
        self.heatmap = HeatmapScreen()
        self.charts = ChartScreen()
        self.portfolio = PortfolioPage(self)
        self.analytics = AnalyticsScreen()
        self.watchlist = WatchlistScreen()
        self.journal = JournalScreen()
        self.backtest = BacktestWindow()
        self.performance = PerformanceScreen()
        self.diagnostics = DiagnosticsScreen()
        self.settings = SettingsScreen()
        self.live_trades = LiveTradesPage(self)
        self.paper_dashboard = PaperTradingDashboard(self)
        
        self.stack.addWidget(self.dashboard)      # 0
        self.stack.addWidget(self.swing_page)     # 1
        self.stack.addWidget(self.intraday_page)  # 2
        self.stack.addWidget(self.option_chain)   # 3
        self.stack.addWidget(self.trfa_page)      # 4
        self.stack.addWidget(self.ptve_page)      # 5
        self.stack.addWidget(self.heatmap)        # 6
        self.stack.addWidget(self.charts)         # 7
        self.stack.addWidget(self.portfolio)      # 8
        self.stack.addWidget(self.analytics)      # 9
        self.stack.addWidget(self.watchlist)      # 10
        self.stack.addWidget(self.journal)        # 11
        self.stack.addWidget(self.backtest)       # 12
        self.stack.addWidget(self.performance)    # 13
        self.stack.addWidget(self.diagnostics)    # 14
        self.stack.addWidget(self.settings)       # 15
        self.stack.addWidget(self.live_trades)    # 16
        self.stack.addWidget(self.paper_dashboard)# 17
        
        # Connect buttons to NavigationManager
        self.btn_dashboard.clicked.connect(lambda: NavigationManager.navigate_to("Dashboard"))
        self.btn_swing.clicked.connect(lambda: NavigationManager.navigate_to("Swing Scanner"))
        self.btn_intraday.clicked.connect(lambda: NavigationManager.navigate_to("Active Trading Scanner"))
        self.btn_option_chain.clicked.connect(lambda: NavigationManager.navigate_to("Option Chain"))
        self.btn_trfa.clicked.connect(lambda: NavigationManager.navigate_to("Forensic Analysis"))
        self.btn_ptve.clicked.connect(lambda: NavigationManager.navigate_to("Paper Trading Validation"))
        self.btn_heatmap.clicked.connect(lambda: NavigationManager.navigate_to("Heatmap"))
        self.btn_charts.clicked.connect(lambda: NavigationManager.navigate_to("Charts"))
        self.btn_portfolio.clicked.connect(lambda: NavigationManager.navigate_to("Portfolio"))
        self.btn_analytics.clicked.connect(lambda: NavigationManager.navigate_to("Analytics"))
        self.btn_watchlist.clicked.connect(lambda: NavigationManager.navigate_to("Watchlist"))
        self.btn_journal.clicked.connect(lambda: NavigationManager.navigate_to("Journal"))
        self.btn_backtest.clicked.connect(lambda: NavigationManager.navigate_to("Backtest"))
        self.btn_performance.clicked.connect(lambda: NavigationManager.navigate_to("Performance"))
        self.btn_diagnostics.clicked.connect(lambda: NavigationManager.navigate_to("Diagnostics"))
        self.btn_settings.clicked.connect(lambda: NavigationManager.navigate_to("Settings"))
        self.btn_live_trades.clicked.connect(lambda: NavigationManager.navigate_to("Live Trades"))
        self.btn_paper_dashboard.clicked.connect(lambda: NavigationManager.navigate_to("Paper Dashboard"))
        
        # Connect dashboard buttons
        self.dashboard.navigate_to_chart.connect(self.navigate_to_chart)
        self.heatmap.navigate_to_chart.connect(self.navigate_to_chart)
        
        # Connect swing scanner stats to footer
        self.swing_page.scan_completed_stats.connect(self._update_footer_stats)

        # Status Bar
        statusbar = self.statusBar()
        statusbar.setStyleSheet(f"background-color: {CARD_BG}; border-top: 1px solid #3D4047;")
        
        self.market_status_lbl = QLabel(" 🔴 Market: Closed |")
        self.market_status_lbl.setStyleSheet("color: #D1D4DC;")
        
        provider_name = getattr(self.config, 'data_provider', 'yahoo')
        self.api_status_lbl = QLabel(f" 🟢 API: {provider_name.title()} |")
        self.api_status_lbl.setStyleSheet("color: #D1D4DC;")
        
        self.universe_lbl = QLabel(" 🌐 Universe: F&O |")
        self.universe_lbl.setStyleSheet("color: #D1D4DC;")
        self.symbols_lbl = QLabel(" 📊 Scanned: 0 |")
        self.symbols_lbl.setStyleSheet("color: #D1D4DC;")
        self.exec_time_lbl = QLabel(" ⏱ Exec Time: -- |")
        self.exec_time_lbl.setStyleSheet("color: #D1D4DC;")
        self.mem_usage_lbl = QLabel(" 🧠 Memory: -- MB |")
        self.mem_usage_lbl.setStyleSheet("color: #D1D4DC;")
        self.cpu_usage_lbl = QLabel(" ⚡ CPU: --% ")
        self.cpu_usage_lbl.setStyleSheet("color: #D1D4DC;")
        
        statusbar.addWidget(self.market_status_lbl)
        statusbar.addWidget(self.api_status_lbl)
        statusbar.addWidget(self.universe_lbl)
        statusbar.addWidget(self.symbols_lbl)
        statusbar.addWidget(self.exec_time_lbl)
        statusbar.addWidget(self.mem_usage_lbl)
        statusbar.addWidget(self.cpu_usage_lbl)
        
        # Performance updater
        from PySide6.QtCore import QTimer
        self.perf_timer = QTimer(self)
        self.perf_timer.timeout.connect(self._update_sys_perf)
        self.perf_timer.start(5000)
        
        # Connect to dashboard if it needed scanner_status_lbl
        self.dashboard.scanner_status_lbl = self.exec_time_lbl
        
        # PAGES Mapping
        self.PAGES = {
            "Dashboard": (0, "btn_dashboard"),
            "Swing Scanner": (1, "btn_swing"),
            "Active Trading Scanner": (2, "btn_intraday"),
            "Option Chain": (3, "btn_option_chain"),
            "Forensic Analysis": (4, "btn_trfa"),
            "Paper Trading Validation": (5, "btn_ptve"),
            "Heatmap": (6, "btn_heatmap"),
            "Charts": (7, "btn_charts"),
            "Portfolio": (8, "btn_portfolio"),
            "Analytics": (9, "btn_analytics"),
            "Watchlist": (10, "btn_watchlist"),
            "Journal": (11, "btn_journal"),
            "Backtest": (12, "btn_backtest"),
            "Performance": (13, "btn_performance"),
            "Diagnostics": (14, "btn_diagnostics"),
            "Settings": (15, "btn_settings"),
            "Live Trades": (16, "btn_live_trades"),
            "Paper Dashboard": (17, "btn_paper_dashboard"),
        }
        self.INDEX_TO_PAGE = {v[0]: k for k, v in self.PAGES.items()}
        
        # Set active initial screen with Persistence
        from PySide6.QtCore import QSettings
        settings = QSettings("RAHUUL_RADAR", "Pro")
        last_index = settings.value("last_active_index", 0, type=int)
        
        # Subscribe to NavigationManager
        self.nav_manager = NavigationManager()
        self.nav_manager.navigation_requested.connect(self._handle_navigation)
        
        # Restore window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1000, 700)
            
        page_name = self.INDEX_TO_PAGE.get(last_index, "Dashboard")
        
        self.active_btn = None
        self.set_active_page(page_name)
        
        # Restore Chart settings
        last_symbol = settings.value("last_symbol", "RELIANCE.NS", type=str)
        last_tf = settings.value("last_timeframe", "1d", type=str)
        if hasattr(self, 'charts'):
            self.charts.search_box.setText(last_symbol)
            self.charts.current_tf = last_tf
                
        # Restore Option Chain settings
        last_index_sym = settings.value("last_option_index", "NIFTY", type=str)
        if hasattr(self, 'option_chain'):
            idx = self.option_chain.combo_index.findText(last_index_sym)
            if idx >= 0:
                self.option_chain.combo_index.setCurrentIndex(idx)

    def create_nav_btn(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("active", False)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 10px 10px 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                color: #A0A5B1;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
                color: #FFFFFF;
            }}
            QPushButton[active="true"] {{
                color: #FFFFFF;
                font-weight: bold;
            }}
        """)
        return btn
        
    def _update_sys_perf(self):
        try:
            import psutil, os
            process = psutil.Process(os.getpid())
            mem_mb = process.memory_info().rss / 1024 / 1024
            cpu_pct = psutil.cpu_percent(interval=None)
            self.mem_usage_lbl.setText(f" 🧠 Mem: {mem_mb:.1f} MB ")
            self.cpu_usage_lbl.setText(f" ⚡ CPU: {cpu_pct:.1f}% ")
        except Exception as _e:
            logging.getLogger(__name__).debug("Suppressed exception in main_window.py:321: %s", _e)

    def _update_footer_stats(self, stats: dict):
        universe = stats.get("universe", 0)
        processed = stats.get("scanned", 0)
        qualified = stats.get("qualified", 0)
        wait_cnt = stats.get("wait_count", 0)
        no_data = stats.get("no_data_count", 0)
        errors = stats.get("errors", 0)
        exec_t = stats.get("exec_time", 0.0)
        
        self.symbols_lbl.setText(f" 📊 Universe: {universe} | Processed: {processed} | Qualified: {qualified} | WAIT: {wait_cnt} | No Data: {no_data} | Errors: {errors} |")
            
        self.exec_time_lbl.setText(f" ⏱ Exec Time: {exec_t:.1f}s |")

    def _handle_navigation(self, page_name: str, payload: dict):
        """
        Global handler triggered by NavigationManager.
        """
        self.set_active_page(page_name)
        
        # Handle payload (e.g. symbol routing)
        if page_name == "Charts" and "symbol" in payload:
            self.charts.load_chart_with_symbol(payload["symbol"])

    def set_active_page(self, page_name):
        if page_name not in self.PAGES:
            return
            
        index, btn_name = self.PAGES[page_name]
        
        if page_name == "Backtest" and not getattr(self, 'is_pro', True):
            QMessageBox.warning(self, "PRO Feature", "Backtest Engine is available in PRO version only.\nPlease upgrade to scan historical data.")
            return
            
        self.stack.setCurrentIndex(index)
        
        if page_name == "Portfolio":
            if hasattr(self.portfolio, "refresh_ui"):
                self.portfolio.refresh_ui()
            elif hasattr(self.portfolio, "refresh_data"):
                self.portfolio.refresh_data()
        elif page_name == "Journal":
            if hasattr(self.journal, "load_data"):
                self.journal.load_data()
        elif page_name == "Diagnostics":
            pass # diagnostics handles its own logic
        elif page_name == "Settings":
            if hasattr(self.settings, "load_settings"):
                self.settings.load_settings()
            
        # SECURITY: Remove active style from ALL sidebar buttons
        for p_name, (idx, b_name) in self.PAGES.items():
            btn = getattr(self, b_name, None)
            if btn:
                btn.setProperty("active", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
                
        # Highlight ONLY the current page
        target_btn = getattr(self, btn_name, None)
        if target_btn:
            target_btn.setProperty("active", True)
            target_btn.style().unpolish(target_btn)
            target_btn.style().polish(target_btn)
            self.active_btn = target_btn
            
            # Animate indicator (Avoid flashing full sidebar by checking height)
            geom = target_btn.geometry()
            if geom.width() > 0 and geom.height() < 100:
                if not self.indicator.isVisible():
                    self.indicator.setGeometry(geom)
                    self.indicator.show()
                    self.indicator.lower()
                else:
                    self.anim = QPropertyAnimation(self.indicator, b"geometry")
                    self.anim.setDuration(150)
                    self.anim.setEasingCurve(QEasingCurve.InOutQuad)
                    self.anim.setEndValue(geom)
                    self.anim.start()
                    
        # Save to QSettings
        from PySide6.QtCore import QSettings
        settings = QSettings("RAHUUL_RADAR", "Pro")
        settings.setValue("last_active_index", index)

    def navigate_to_chart(self, symbol):
        # Kept for backward compatibility with older direct signals, 
        # though NavigationManager handles this globally now.
        NavigationManager.navigate_to("Charts", symbol=symbol)

    def create_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar { background-color: #1A1C23; color: white; } QMenuBar::item:selected { background-color: #3D4047; } QMenu { background-color: #1A1C23; color: white; border: 1px solid #3D4047; } QMenu::item:selected { background-color: #2196F3; }")
        
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        py_version = sys.version.split(' ')[0]
        os_info = platform.platform()
        
        title_str = "RAHUUL RADAR PRO" if self.is_pro else "RAHUUL RADAR (Free Edition)"
        
        QMessageBox.about(self, f"About {title_str}", 
                          f"<b>{title_str}</b><br><br>"
                          "Version : 1.0 RC<br>"
                          "Build : 2026.07<br>"
                          f"Platform : {os_info}<br>"
                          f"Python Version : {py_version}<br>"
                          "Developer : Rahul")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'active_btn') and self.active_btn:
            geom = self.active_btn.geometry()
            # Sanity check height to prevent full-sidebar blue flash bug on startup
            if geom.width() > 0 and geom.height() < 100:
                self.indicator.setGeometry(geom)
                if not self.indicator.isVisible():
                    self.indicator.show()
                    self.indicator.lower()

    def closeEvent(self, event):
        from PySide6.QtCore import QSettings
        settings = QSettings("RAHUUL_RADAR", "Pro")
        settings.setValue("geometry", self.saveGeometry())
        
        # Save specific states if widgets are initialized
        if hasattr(self, 'charts'):
            self.charts.search_box = getattr(self.charts, 'search_box', None)
            if self.charts.search_box:
                settings.setValue("last_symbol", self.charts.search_box.text().strip())
            settings.setValue("last_timeframe", getattr(self.charts, 'current_tf', "1d"))
            
        if hasattr(self, 'option_chain'):
            settings.setValue("last_option_index", self.option_chain.combo_index.currentText())
            
        event.accept()
