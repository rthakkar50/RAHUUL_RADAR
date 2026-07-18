"""
Sector Strength Engine for RAHUUL_RADAR.
Accuracy Sprint - Stage 6
Evaluates sector ETF performance to assign a sector score.
"""
from loguru import logger

# Map sector names to NSE ETF / Index symbols
SECTOR_ETF_MAP = {
    "IT": "^CNXIT",           # Nifty IT
    "FINANCIAL SERVICES": "^NSEBANK", # Nifty Bank
    "BANKS": "^NSEBANK",
    "PHARMA": "^CNXPHARMA",   # Nifty Pharma
    "AUTO": "^CNXAUTO",       # Nifty Auto
    "FMCG": "^CNXFMCG",       # Nifty FMCG
    "METALS": "^CNXMETAL",    # Nifty Metal
    "ENERGY": "^CNXENERGY",   # Nifty Energy
    "REALTY": "^CNXREALTY",   # Nifty Realty
}

class SectorEngine:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        # Cache for sector evaluations so we don't fetch same ETF 100 times
        self._sector_cache = {}

    def get_sector_score_and_detail(self, sector_name: str) -> tuple[float, str]:
        """
        Evaluate sector strength.
        Returns:
            (score, detail_string)
            Score is out of max sector weight (e.g. 5.0)
        """
        if not sector_name or sector_name.upper() == "N/A" or sector_name.upper() == "UNKNOWN":
            return (0.0, "No sector data")

        sector_upper = sector_name.upper()
        
        # Check cache
        if sector_upper in self._sector_cache:
            return self._sector_cache[sector_upper]

        etf_symbol = SECTOR_ETF_MAP.get(sector_upper)
        if not etf_symbol:
            return (2.5, f"Sector {sector_name} (No ETF map)") # Neutral middle score

        try:
            # Fetch recent data for ETF
            ohlcv = self.data_provider.get_ohlcv(etf_symbol, interval="1d", period="5d")
            if ohlcv is None or len(ohlcv) < 2:
                return (2.5, f"{etf_symbol} data unavailable")

            # Simple momentum check (Last close vs previous close)
            last_close = ohlcv['Close'].iloc[-1]
            prev_close = ohlcv['Close'].iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            
            # Rate strength
            if pct_change >= 1.0:
                score = 5.0
                detail = f"Strong (+{pct_change:.1f}%)"
            elif pct_change >= 0.0:
                score = 3.5
                detail = f"Positive (+{pct_change:.1f}%)"
            elif pct_change >= -1.0:
                score = 1.5
                detail = f"Weak ({pct_change:.1f}%)"
            else:
                score = 0.0
                detail = f"Very Weak ({pct_change:.1f}%)"
            
            result = (score, f"{etf_symbol}: {detail}")
            self._sector_cache[sector_upper] = result
            return result
            
        except Exception as e:
            logger.warning(f"Failed to fetch sector data for {sector_upper}: {e}")
            return (2.5, "Data fetch error")
