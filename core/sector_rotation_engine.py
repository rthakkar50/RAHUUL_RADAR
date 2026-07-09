import os
import logging
import threading
from datetime import datetime
import pandas as pd
from application.data_manager import DataManager

# Configure a specific file handler for Sector Rotation logs
sector_log_path = os.path.join(os.getcwd(), "logs", "sector_rotation.log")
os.makedirs(os.path.dirname(sector_log_path), exist_ok=True)
sector_logger = logging.getLogger("sector_rotation")
sector_logger.setLevel(logging.INFO)
fh = logging.FileHandler(sector_log_path)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
sector_logger.addHandler(fh)

class SectorRotationEngine:
    """
    Evaluates the strength of 14 major NSE sectors relative to NIFTY.
    Implements a 5-minute background caching system.
    """
    
    SECTORS = {
        "BANKING": "^NSEBANK",
        "FINANCIAL SERVICES": "^CNXFIN",
        "IT": "^CNXIT",
        "AUTO": "^CNXAUTO",
        "PHARMA": "^CNXPHARMA",
        "FMCG": "^CNXFMCG",
        "METAL": "^CNXMETAL",
        "ENERGY": "^CNXENERGY",
        "REALTY": "^CNXREALTY",
        "MEDIA": "^CNXMEDIA",
        "PSU": "^CNXPSUBANK",
        "CHEMICAL": "^CNXCOMM",  # Proxy for commodities/chemicals if exact index not easily available via yfinance, CNXCOMM works
        "CAPITAL GOODS": "^CNXINFRA", # Proxy
        "INFRASTRUCTURE": "^CNXINFRA"
    }

    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SectorRotationEngine, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized: return
        self.data_manager = DataManager.get_instance()
        self.sector_data = {}
        self.last_update = None
        self.is_updating = False
        self._initialized = True
        
    def get_sector_data(self):
        """Returns the cached sector rankings, or triggers an update."""
        if self.last_update is None or (datetime.now() - self.last_update).total_seconds() > 300:
            if not self.is_updating:
                # Trigger background update
                threading.Thread(target=self._update_sectors, daemon=True).start()
        return self.sector_data

    def _update_sectors(self):
        self.is_updating = True
        try:
            sector_logger.info("Starting background sector rotation update...")
            
            # Get Nifty Baseline
            nifty_df = self.data_manager.get_historical_data("^NSEI", period="3mo", interval="1d")
            if nifty_df.empty:
                sector_logger.warning("Failed to fetch NIFTY baseline.")
                self.is_updating = False
                return
                
            nifty_ret = nifty_df['Close'].pct_change().rolling(20).sum().iloc[-1]
            
            new_data = {}
            for name, symbol in self.SECTORS.items():
                try:
                    df = self.data_manager.get_historical_data(symbol, period="3mo", interval="1d")
                    if df.empty or len(df) < 50:
                        continue
                        
                    close = df['Close'].iloc[-1]
                    ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
                    ema_50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
                    
                    # 1. Trend Score (0-30)
                    trend_score = 0
                    if close > ema_20: trend_score += 10
                    if close > ema_50: trend_score += 10
                    if ema_20 > ema_50: trend_score += 10
                    
                    # 2. Relative Strength vs Nifty (0-40)
                    sec_ret = df['Close'].pct_change().rolling(20).sum().iloc[-1]
                    rs = sec_ret - nifty_ret
                    rs_score = max(0, min(40, (rs * 100) + 20)) # Normalize
                    
                    # 3. Momentum (0-30)
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs_rsi = gain / loss
                    rsi = 100 - (100 / (1 + rs_rsi)).iloc[-1]
                    
                    mom_score = max(0, min(30, (rsi - 30) * 1.5)) if not pd.isna(rsi) else 15
                    
                    final_score = round(trend_score + rs_score + mom_score, 1)
                    final_score = min(max(final_score, 0), 100)
                    
                    trend_status = "Bullish" if close > ema_20 else "Bearish"
                    
                    new_data[name] = {
                        "score": final_score,
                        "trend": trend_status,
                        "rsi": rsi if not pd.isna(rsi) else 50
                    }
                    
                except Exception as e:
                    sector_logger.error(f"Error processing sector {name}: {e}")
                    
            # Sort by score descending
            self.sector_data = dict(sorted(new_data.items(), key=lambda x: x[1]['score'], reverse=True))
            self.last_update = datetime.now()
            sector_logger.info(f"Sector rotation updated. Leader: {list(self.sector_data.keys())[0] if self.sector_data else 'None'}")
            
        except Exception as e:
            sector_logger.error(f"Critical error in sector rotation: {e}")
        finally:
            self.is_updating = False

    def get_stock_sector(self, symbol):
        """
        Maps a stock to its sector.
        For a production system, this should query a local DB or static map.
        As a placeholder, we return IT for TCS/INFY, BANKING for HDFCBANK, etc.
        """
        symbol = symbol.upper()
        if any(x in symbol for x in ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM']):
            return "IT"
        if any(x in symbol for x in ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK']):
            return "BANKING"
        if any(x in symbol for x in ['TATAMOTORS', 'MARUTI', 'M&M', 'HEROMOTOCO', 'BAJAJ-AUTO']):
            return "AUTO"
        if any(x in symbol for x in ['RELIANCE', 'ONGC', 'NTPC', 'POWERGRID']):
            return "ENERGY"
        if any(x in symbol for x in ['ITC', 'HINDUNILVR', 'NESTLEIND', 'BRITANNIA']):
            return "FMCG"
        if any(x in symbol for x in ['TATASTEEL', 'JSWSTEEL', 'HINDALCO']):
            return "METAL"
        if any(x in symbol for x in ['SUNPHARMA', 'CIPLA', 'DRREDDY', 'DIVISLAB']):
            return "PHARMA"
            
        return "UNKNOWN"
