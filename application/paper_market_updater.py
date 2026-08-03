from PySide6.QtCore import QObject, QTimer, Signal
from application.paper_trading_service import PaperTradingEngine
from market.market_data_manager import MarketDataManager
from market.paytm_websocket import PaytmLiveBroadcast
from config.config import AppConfig

class PaperMarketUpdater(QObject):
    # Signal to safely cross thread boundary from websocket to UI thread
    tick_received = Signal(str, float)
    
    def __init__(self, interval_ms=5000):
        super().__init__()
        self.interval_ms = interval_ms
        self.paper = PaperTradingEngine.get_instance()
        self.provider = MarketDataManager()
        
        config = AppConfig()
        config.load()
        self.market_provider = getattr(config, 'market_provider', getattr(config, 'data_provider', 'yahoo'))
        
        self.broadcast = None
        if self.market_provider == 'paytm':
            self.broadcast = PaytmLiveBroadcast.get_instance()
            paytm_config = getattr(config, 'paytm', {})
            self.broadcast.set_token(paytm_config.get('public_access_token', ''))
            self.broadcast.add_callback(self._on_ws_tick)
            self.tick_received.connect(self._handle_tick_main_thread)
            
        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self.update_all)
        
    def start(self):
        self.provider.connect()
        if self.broadcast:
            self.broadcast.connect()
        self.timer.start()
        
    def stop(self):
        self.timer.stop()
        self.provider.disconnect()
        if self.broadcast:
            # We don't disconnect broadcast entirely as other components might use it
            self.broadcast.remove_callback(self._on_ws_tick)
        
    def _on_ws_tick(self, data):
        items = data.get('data', [])
        for item in items:
            sec_id = item.get('security_id')
            ltp = item.get('last_price', item.get('lastPrice', item.get('ltp')))
            if sec_id and ltp is not None:
                # We need to map sec_id back to symbol. Since our positions have symbols,
                # we just loop through open positions.
                open_positions = self.paper.engine.open_positions
                for pos in open_positions.values():
                    # Simplified mapping: symbol without .NS == sec_id 
                    if pos.symbol.replace('.NS', '') == str(sec_id):
                        self.tick_received.emit(pos.symbol, float(ltp))
                        break
                        
    def _handle_tick_main_thread(self, symbol: str, cmp: float):
        if cmp > 0:
            self.paper.update_market_price(symbol, cmp)
        
    def update_all(self):
        open_positions = self.paper.engine.open_positions
        if not open_positions:
            return
            
        symbols = [pos.symbol for pos in open_positions.values()]
        
        if self.broadcast and self.broadcast.is_connected():
            sec_ids = [s.replace('.NS', '') for s in symbols]
            self.broadcast.subscribe(sec_ids)
            # Ticks will arrive asynchronously, no need to poll Yahoo here
            return
            
        # Fallback to polling
        for position_id, position in open_positions.items():
            try:
                cmp = self.provider.get_last_price(position.symbol)
                if cmp > 0:
                    self.paper.update_market_price(position.symbol, cmp)
            except Exception as e:
                print(f"[PaperUpdater] {position.symbol} {str(e)}")
