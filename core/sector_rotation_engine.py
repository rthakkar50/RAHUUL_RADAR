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


    STOCK_SECTOR_MAP = {
        "AARTIIND.NS": "CHEMICAL",
        "ABB.NS": "CAPITAL GOODS",
        "ABBOTINDIA.NS": "PHARMA",
        "ABCAPITAL.NS": "FINANCIAL SERVICES",
        "ABFRL.NS": "UNKNOWN",
        "ACC.NS": "INFRASTRUCTURE",
        "ADANIENT.NS": "UNKNOWN",
        "ADANIPORTS.NS": "INFRASTRUCTURE",
        "ALKEM.NS": "PHARMA",
        "AMBUJACEM.NS": "INFRASTRUCTURE",
        "APOLLOHOSP.NS": "PHARMA",
        "APOLLOTYRE.NS": "AUTO",
        "ASHOKLEY.NS": "AUTO",
        "ASIANPAINT.NS": "UNKNOWN",
        "ASTRAL.NS": "INFRASTRUCTURE",
        "ATUL.NS": "CHEMICAL",
        "AUBANK.NS": "BANKING",
        "AUROPHARMA.NS": "PHARMA",
        "AXISBANK.NS": "BANKING",
        "BAJAJ-AUTO.NS": "AUTO",
        "BAJAJFINSV.NS": "FINANCIAL SERVICES",
        "BAJFINANCE.NS": "FINANCIAL SERVICES",
        "BALKRISIND.NS": "AUTO",
        "BANDHANBNK.NS": "BANKING",
        "BANKBARODA.NS": "BANKING",
        "BATAINDIA.NS": "UNKNOWN",
        "BEL.NS": "CAPITAL GOODS",
        "BERGEPAINT.NS": "UNKNOWN",
        "BHARATFORG.NS": "AUTO",
        "BHARTIARTL.NS": "UNKNOWN",
        "BHEL.NS": "CAPITAL GOODS",
        "BIOCON.NS": "PHARMA",
        "BOSCHLTD.NS": "AUTO",
        "BPCL.NS": "ENERGY",
        "BRITANNIA.NS": "FMCG",
        "BSOFT.NS": "IT",
        "CANBK.NS": "BANKING",
        "CANFINHOME.NS": "FINANCIAL SERVICES",
        "CHAMBLFERT.NS": "CHEMICAL",
        "CHOLAFIN.NS": "FINANCIAL SERVICES",
        "CIPLA.NS": "PHARMA",
        "COALINDIA.NS": "ENERGY",
        "COFORGE.NS": "IT",
        "COLPAL.NS": "FMCG",
        "CONCOR.NS": "UNKNOWN",
        "COROMANDEL.NS": "CHEMICAL",
        "CROMPTON.NS": "UNKNOWN",
        "CUB.NS": "BANKING",
        "CUMMINSIND.NS": "CAPITAL GOODS",
        "DABUR.NS": "FMCG",
        "DALBHARAT.NS": "INFRASTRUCTURE",
        "DEEPAKNTR.NS": "CHEMICAL",
        "DIVISLAB.NS": "PHARMA",
        "DIXON.NS": "UNKNOWN",
        "DLF.NS": "REALTY",
        "DRREDDY.NS": "PHARMA",
        "EICHERMOT.NS": "AUTO",
        "ESCORTS.NS": "AUTO",
        "EXIDEIND.NS": "AUTO",
        "FEDERALBNK.NS": "BANKING",
        "GAIL.NS": "ENERGY",
        "GLENMARK.NS": "PHARMA",
        "GMRINFRA.NS": "INFRASTRUCTURE",
        "GNFC.NS": "CHEMICAL",
        "GODREJCP.NS": "FMCG",
        "GODREJPROP.NS": "REALTY",
        "GRANULES.NS": "PHARMA",
        "GRASIM.NS": "INFRASTRUCTURE",
        "GUJGASLTD.NS": "ENERGY",
        "HAL.NS": "CAPITAL GOODS",
        "HAVELLS.NS": "UNKNOWN",
        "HCLTECH.NS": "IT",
        "HDFCAMC.NS": "FINANCIAL SERVICES",
        "HDFCBANK.NS": "BANKING",
        "HDFCLIFE.NS": "FINANCIAL SERVICES",
        "HEROMOTOCO.NS": "AUTO",
        "HINDALCO.NS": "METAL",
        "HINDCOPPER.NS": "METAL",
        "HINDPETRO.NS": "ENERGY",
        "HINDUNILVR.NS": "FMCG",
        "ICICIBANK.NS": "BANKING",
        "ICICIGI.NS": "FINANCIAL SERVICES",
        "ICICIPRULI.NS": "FINANCIAL SERVICES",
        "IDEA.NS": "UNKNOWN",
        "IDFCFIRSTB.NS": "BANKING",
        "IEX.NS": "FINANCIAL SERVICES",
        "IGL.NS": "ENERGY",
        "INDHOTEL.NS": "UNKNOWN",
        "INDIACEM.NS": "INFRASTRUCTURE",
        "INDIAMART.NS": "IT",
        "INDIGO.NS": "UNKNOWN",
        "INDUSINDBK.NS": "BANKING",
        "INDUSTOWER.NS": "UNKNOWN",
        "INFY.NS": "IT",
        "IOC.NS": "ENERGY",
        "IPCALAB.NS": "PHARMA",
        "IRCTC.NS": "UNKNOWN",
        "ITC.NS": "FMCG",
        "JINDALSTEL.NS": "METAL",
        "JKCEMENT.NS": "INFRASTRUCTURE",
        "JSWSTEEL.NS": "METAL",
        "JUBLFOOD.NS": "UNKNOWN",
        "KOTAKBANK.NS": "BANKING",
        "LALPATHLAB.NS": "PHARMA",
        "LAURUSLABS.NS": "PHARMA",
        "LICHSGFIN.NS": "FINANCIAL SERVICES",
        "LT.NS": "CAPITAL GOODS",
        "LTIM.NS": "IT",
        "LTTS.NS": "IT",
        "LUPIN.NS": "PHARMA",
        "M&M.NS": "AUTO",
        "M&MFIN.NS": "FINANCIAL SERVICES",
        "MANAPPURAM.NS": "FINANCIAL SERVICES",
        "MARICO.NS": "FMCG",
        "MARUTI.NS": "AUTO",
        "MCX.NS": "FINANCIAL SERVICES",
        "METROPOLIS.NS": "PHARMA",
        "MFSL.NS": "FINANCIAL SERVICES",
        "MGL.NS": "ENERGY",
        "MOTHERSON.NS": "AUTO",
        "MPHASIS.NS": "IT",
        "MRF.NS": "AUTO",
        "MUTHOOTFIN.NS": "FINANCIAL SERVICES",
        "NATIONALUM.NS": "METAL",
        "NAUKRI.NS": "IT",
        "NAVINFLUOR.NS": "CHEMICAL",
        "NESTLEIND.NS": "FMCG",
        "NMDC.NS": "METAL",
        "NTPC.NS": "ENERGY",
        "OBEROIRLTY.NS": "REALTY",
        "OFSS.NS": "IT",
        "ONGC.NS": "ENERGY",
        "PAGEIND.NS": "UNKNOWN",
        "PEL.NS": "FINANCIAL SERVICES",
        "PERSISTENT.NS": "IT",
        "PETRONET.NS": "ENERGY",
        "PFC.NS": "FINANCIAL SERVICES",
        "PIDILITIND.NS": "CHEMICAL",
        "PIIND.NS": "CHEMICAL",
        "PNB.NS": "BANKING",
        "POLYCAB.NS": "CAPITAL GOODS",
        "POWERGRID.NS": "ENERGY",
        "PVRINOX.NS": "MEDIA",
        "RAMCOCEM.NS": "INFRASTRUCTURE",
        "RBLBANK.NS": "BANKING",
        "RECLTD.NS": "FINANCIAL SERVICES",
        "RELIANCE.NS": "ENERGY",
        "SAIL.NS": "METAL",
        "SBICARD.NS": "FINANCIAL SERVICES",
        "SBILIFE.NS": "FINANCIAL SERVICES",
        "SBIN.NS": "BANKING",
        "SHREECEM.NS": "INFRASTRUCTURE",
        "SHRIRAMFIN.NS": "FINANCIAL SERVICES",
        "SIEMENS.NS": "CAPITAL GOODS",
        "SRF.NS": "CHEMICAL",
        "SUNTV.NS": "MEDIA",
        "SUNPHARMA.NS": "PHARMA",
        "SYNGENE.NS": "PHARMA",
        "TATACHEM.NS": "CHEMICAL",
        "TATACOMM.NS": "UNKNOWN",
        "TATACONSUM.NS": "FMCG",
        "TATAMOTORS.NS": "AUTO",
        "TATAPOWER.NS": "ENERGY",
        "TATASTEEL.NS": "METAL",
        "TCS.NS": "IT",
        "TECHM.NS": "IT",
        "TITAN.NS": "UNKNOWN",
        "TORNTPHARM.NS": "PHARMA",
        "TRENT.NS": "UNKNOWN",
        "TVSMOTOR.NS": "AUTO",
        "UBL.NS": "FMCG",
        "ULTRACEMCO.NS": "INFRASTRUCTURE",
        "UPL.NS": "CHEMICAL",
        "VEDL.NS": "METAL",
        "VOLTAS.NS": "UNKNOWN",
        "WIPRO.NS": "IT",
        "ZEEL.NS": "MEDIA",
        "ZYDUSLIFE.NS": "PHARMA",
    }
    

    def get_stock_sector(self, symbol):
        """
        Maps a stock to its sector.
        """
        return self.STOCK_SECTOR_MAP.get(symbol.upper(), "UNKNOWN")
        
    def get_sector_symbol(self, sector_name):
        """
        Returns the Yahoo Finance symbol for a given sector name, or None.
        """
        return self.SECTORS.get(sector_name)
