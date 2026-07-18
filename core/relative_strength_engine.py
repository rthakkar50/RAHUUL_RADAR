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
    MARKET_ALPHA_WEIGHT = 0.70
    SECTOR_ALPHA_WEIGHT = 0.30
    SHORT_TERM_WEIGHT_5D = 0.60
    SHORT_TERM_WEIGHT_20D = 0.40
    LONG_TERM_WEIGHT_50D = 0.60
    LONG_TERM_WEIGHT_100D = 0.40
    MOMENTUM_MAX_SPREAD = 10.0
    
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
            "momentum": 50,
            "trend_persistence": 50.0,
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
            nifty_df = self.data_manager.get_stock_data("^NSEI", period="6mo", interval="1d")
            bank_df = self.data_manager.get_stock_data("^NSEBANK", period="6mo", interval="1d")
            
            if nifty_df is None or nifty_df.empty:
                rs_logger.warning("Failed to fetch NIFTY baseline. Aborting RS update.")
                self.is_updating = False
                return
                
            # Precompute NIFTY daily returns for persistence
            nifty_daily_returns = nifty_df['Close'].pct_change()
                
            def calc_returns(df):
                if df is None or df.empty or len(df) < 100: return {}
                return {
                    "1d": df['Close'].pct_change(1).iloc[-1],
                    "5d": df['Close'].pct_change(5).iloc[-1],
                    "20d": df['Close'].pct_change(20).iloc[-1],
                    "50d": df['Close'].pct_change(50).iloc[-1],
                    "100d": df['Close'].pct_change(100).iloc[-1]
                }
                
            nifty_ret = calc_returns(nifty_df)
            
            # 1.5 Precompute Sector Returns
            sector_returns = {}
            for sec_name, sec_symbol in self.sector_engine.SECTORS.items():
                sec_df = self.data_manager.get_stock_data(sec_symbol, period="6mo", interval="1d")
                if sec_df is not None and not sec_df.empty and len(sec_df) >= 100:
                    sector_returns[sec_name] = calc_returns(sec_df)
            
            # 2. Iterate through F&O universe
            universe = get_fno_symbols()
            if not universe:
                universe = [{"symbol": s} for s in ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS"]]
                
            temp_rs_data = {}
            for item in universe:
                sym = item["symbol"]
                try:
                    df = self.data_manager.get_stock_data(sym, period="6mo", interval="1d")
                    if df is None or df.empty or len(df) < 100:
                        continue
                        
                    stock_ret = calc_returns(df)
                    
                    # Determine Sector Return
                    stock_sector = self.sector_engine.get_stock_sector(sym)
                    sec_ret = sector_returns.get(stock_sector, nifty_ret) # Fallback to Nifty if unknown/missing
                    
                    # Calculate Market Alpha
                    market_rs_1d = (stock_ret["1d"] - nifty_ret.get("1d", 0)) * 100
                    market_rs_5d = (stock_ret["5d"] - nifty_ret.get("5d", 0)) * 100
                    market_rs_20d = (stock_ret["20d"] - nifty_ret.get("20d", 0)) * 100
                    market_rs_50d = (stock_ret["50d"] - nifty_ret.get("50d", 0)) * 100
                    market_rs_100d = (stock_ret["100d"] - nifty_ret.get("100d", 0)) * 100
                    
                    # Calculate Sector Alpha
                    sector_rs_1d = (stock_ret["1d"] - sec_ret.get("1d", 0)) * 100
                    sector_rs_5d = (stock_ret["5d"] - sec_ret.get("5d", 0)) * 100
                    sector_rs_20d = (stock_ret["20d"] - sec_ret.get("20d", 0)) * 100
                    sector_rs_50d = (stock_ret["50d"] - sec_ret.get("50d", 0)) * 100
                    sector_rs_100d = (stock_ret["100d"] - sec_ret.get("100d", 0)) * 100
                    
                    # Blend Market and Sector Alpha
                    rs_1d = (market_rs_1d * self.MARKET_ALPHA_WEIGHT) + (sector_rs_1d * self.SECTOR_ALPHA_WEIGHT)
                    rs_5d = (market_rs_5d * self.MARKET_ALPHA_WEIGHT) + (sector_rs_5d * self.SECTOR_ALPHA_WEIGHT)
                    rs_20d = (market_rs_20d * self.MARKET_ALPHA_WEIGHT) + (sector_rs_20d * self.SECTOR_ALPHA_WEIGHT)
                    rs_50d = (market_rs_50d * self.MARKET_ALPHA_WEIGHT) + (sector_rs_50d * self.SECTOR_ALPHA_WEIGHT)
                    rs_100d = (market_rs_100d * self.MARKET_ALPHA_WEIGHT) + (sector_rs_100d * self.SECTOR_ALPHA_WEIGHT)
                    
                    # Composite RS Score (0-100 scale)
                    # Weights: 100D (30%), 50D (30%), 20D (20%), 5D (10%), 1D (10%)
                    composite = (rs_100d * 0.3) + (rs_50d * 0.3) + (rs_20d * 0.2) + (rs_5d * 0.1) + (rs_1d * 0.1)
                    
                    # Normalize raw composite roughly into 0-100
                    # Assuming a +/- 50% relative outperformance is the absolute extreme limit
                    normalized_score = max(0, min(100, (composite + 25) * 2))
                    
                    # Calculate Relative Momentum
                    short_term_rs = (rs_5d * self.SHORT_TERM_WEIGHT_5D) + (rs_20d * self.SHORT_TERM_WEIGHT_20D)
                    long_term_rs = (rs_50d * self.LONG_TERM_WEIGHT_50D) + (rs_100d * self.LONG_TERM_WEIGHT_100D)
                    
                    raw_momentum = short_term_rs - long_term_rs
                    
                    # Normalize raw momentum to 0-100 scale using MOMENTUM_MAX_SPREAD (10.0 => 50% swing per 10 spread)
                    momentum_score = max(0, min(100, (raw_momentum + self.MOMENTUM_MAX_SPREAD) * (100 / (2 * self.MOMENTUM_MAX_SPREAD))))
                    
                    # Calculate Trend Persistence (50 days lookback)
                    stock_daily_returns = df['Close'].pct_change()
                    aligned_df = pd.concat([stock_daily_returns, nifty_daily_returns], axis=1).dropna()
                    aligned_df.columns = ['Stock', 'Nifty']
                    
                    # Lookback of 50 days
                    lookback_df = aligned_df.tail(50)
                    if len(lookback_df) < 10:
                        persistence_score = 50.0
                    else:
                        hits = (lookback_df['Stock'] > lookback_df['Nifty']).sum()
                        persistence_score = (hits / len(lookback_df)) * 100.0
                    
                    classification = "Neutral"
                    if normalized_score >= 95: classification = "Market Leader"
                    elif normalized_score >= 85: classification = "Strong Leader"
                    elif normalized_score >= 70: classification = "Outperforming"
                    elif normalized_score >= 55: classification = "Neutral"
                    elif normalized_score >= 40: classification = "Weak"
                    else: classification = "Underperformer"
                    
                    temp_rs_data[sym] = {
                        "score": round(normalized_score, 1),
                        "momentum": round(momentum_score, 1),
                        "trend_persistence": round(persistence_score, 1),
                        "sector_alpha": round(sector_rs_50d, 2), # Export 50d sector alpha as the representative sector alpha
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
