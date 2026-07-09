import os
import logging
import threading
from datetime import datetime
import pandas as pd
from application.data_manager import DataManager
from core.sector_rotation_engine import SectorRotationEngine
from market.universe import get_fno_symbols

# Configure a specific file handler for RS Engine logs
rs_log_path = os.path.join(os.getcwd(), "logs", "relative_strength.log")
os.makedirs(os.path.dirname(rs_log_path), exist_ok=True)
rs_logger = logging.getLogger("relative_strength")
rs_logger.setLevel(logging.INFO)
fh = logging.FileHandler(rs_log_path)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
rs_logger.addHandler(fh)

class RelativeStrengthEngine:
    """
    Evaluates the Relative Strength of every F&O stock against NIFTY, BANKNIFTY, and its Sector.
    Caches results and updates in a background thread every 5 minutes.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RelativeStrengthEngine, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized: return
        self.data_manager = DataManager.get_instance()
        self.sector_engine = SectorRotationEngine()
        
        self.rs_data = {}  # Dict mapping symbol -> RS Metrics
        self.top_leaders = []
        self.top_weakest = []
        
        self.last_update = None
        self.is_updating = False
        self._initialized = True
        
    def get_rs_data(self, symbol=None):
        """Returns the cached RS data for a symbol or the entire dictionary."""
        # Trigger background update if stale
        if self.last_update is None or (datetime.now() - self.last_update).total_seconds() > 300:
            if not self.is_updating:
                threading.Thread(target=self._update_rs_cache, daemon=True).start()
                
        if symbol:
            return self.rs_data.get(symbol, self._default_rs_data())
        return self.rs_data

    def _default_rs_data(self):
        return {
            "score": 50,
            "classification": "Neutral",
            "rs_rank": "--",
            "market_rank": "--",
            "sector_rank": "--",
            "1d": 0, "5d": 0, "20d": 0, "50d": 0, "100d": 0
        }

    def _update_rs_cache(self):
        self.is_updating = True
        try:
            rs_logger.info("Starting background Relative Strength cache update...")
            
            # 1. Fetch baselines
            nifty_df = self.data_manager.get_historical_data("^NSEI", period="6mo", interval="1d")
            bank_df = self.data_manager.get_historical_data("^NSEBANK", period="6mo", interval="1d")
            
            if nifty_df.empty:
                rs_logger.warning("Failed to fetch NIFTY baseline. Aborting RS update.")
                self.is_updating = False
                return
                
            def calc_returns(df):
                if df.empty or len(df) < 100: return {}
                return {
                    "1d": df['Close'].pct_change(1).iloc[-1],
                    "5d": df['Close'].pct_change(5).iloc[-1],
                    "20d": df['Close'].pct_change(20).iloc[-1],
                    "50d": df['Close'].pct_change(50).iloc[-1],
                    "100d": df['Close'].pct_change(100).iloc[-1]
                }
                
            nifty_ret = calc_returns(nifty_df)
            
            # 2. Iterate through F&O universe
            universe = get_fno_symbols()
            if not universe:
                universe = [{"symbol": s} for s in ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS"]]
                
            temp_rs_data = {}
            for item in universe:
                sym = item["symbol"]
                try:
                    df = self.data_manager.get_historical_data(sym, period="6mo", interval="1d")
                    if df.empty or len(df) < 100:
                        continue
                        
                    stock_ret = calc_returns(df)
                    
                    # Calculate comparative alpha (difference in returns)
                    # We heavily weight shorter term momentum for breakout detection, but need long term for structural RS
                    rs_1d = (stock_ret["1d"] - nifty_ret.get("1d", 0)) * 100
                    rs_5d = (stock_ret["5d"] - nifty_ret.get("5d", 0)) * 100
                    rs_20d = (stock_ret["20d"] - nifty_ret.get("20d", 0)) * 100
                    rs_50d = (stock_ret["50d"] - nifty_ret.get("50d", 0)) * 100
                    rs_100d = (stock_ret["100d"] - nifty_ret.get("100d", 0)) * 100
                    
                    # Composite RS Score (0-100 scale)
                    # Weights: 100D (30%), 50D (30%), 20D (20%), 5D (10%), 1D (10%)
                    composite = (rs_100d * 0.3) + (rs_50d * 0.3) + (rs_20d * 0.2) + (rs_5d * 0.1) + (rs_1d * 0.1)
                    
                    # Normalize raw composite roughly into 0-100
                    # Assuming a +/- 50% relative outperformance is the absolute extreme limit
                    normalized_score = max(0, min(100, (composite + 25) * 2))
                    
                    classification = "Neutral"
                    if normalized_score >= 95: classification = "Market Leader"
                    elif normalized_score >= 85: classification = "Strong Leader"
                    elif normalized_score >= 70: classification = "Outperforming"
                    elif normalized_score >= 55: classification = "Neutral"
                    elif normalized_score >= 40: classification = "Weak"
                    else: classification = "Underperformer"
                    
                    temp_rs_data[sym] = {
                        "score": round(normalized_score, 1),
                        "classification": classification,
                        "1d": round(rs_1d, 2),
                        "5d": round(rs_5d, 2),
                        "20d": round(rs_20d, 2),
                        "50d": round(rs_50d, 2),
                        "100d": round(rs_100d, 2),
                        "sector": self.sector_engine.get_stock_sector(sym)
                    }
                except Exception as e:
                    rs_logger.error(f"Error processing RS for {sym}: {e}")
                    
            # 3. Calculate Rankings
            # Sort all by score descending
            sorted_symbols = sorted(temp_rs_data.keys(), key=lambda x: temp_rs_data[x]['score'], reverse=True)
            
            # Group by sector for sector rank
            sector_groups = {}
            for sym, data in temp_rs_data.items():
                sec = data['sector']
                if sec not in sector_groups: sector_groups[sec] = []
                sector_groups[sec].append((sym, data['score']))
                
            for sec in sector_groups:
                sector_groups[sec].sort(key=lambda x: x[1], reverse=True)
                
            # Assign ranks
            for rank, sym in enumerate(sorted_symbols, 1):
                temp_rs_data[sym]['market_rank'] = f"{rank}/{len(sorted_symbols)}"
                temp_rs_data[sym]['rs_rank'] = rank
                
                # Find sector rank
                sec = temp_rs_data[sym]['sector']
                sec_list = sector_groups[sec]
                sec_rank = next(i for i, v in enumerate(sec_list, 1) if v[0] == sym)
                temp_rs_data[sym]['sector_rank'] = f"{sec_rank}/{len(sec_list)}"
                
            self.rs_data = temp_rs_data
            self.top_leaders = sorted_symbols[:10]
            self.top_weakest = sorted_symbols[-10:]
            
            self.last_update = datetime.now()
            rs_logger.info(f"RS Engine updated successfully. Processed {len(self.rs_data)} stocks.")
            
        except Exception as e:
            rs_logger.error(f"Critical error in RS Engine update: {e}")
        finally:
            self.is_updating = False
