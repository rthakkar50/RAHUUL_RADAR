import logging
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger("MarketIntelligence")

class MarketIntelligenceEngine:
    """
    SPRINT-94: Pre-scan Market Intelligence Layer.
    Evaluates overarching market conditions before individual stock scanning.
    """
    
    SECTOR_INDICES = {
        "IT": "^CNXIT",
        "BANKING": "^NSEBANK",
        "AUTO": "^CNXAUTO",
        "FMCG": "^CNXFMCG",
        "PHARMA": "^CNXPHARMA",
        "METALS": "^CNXMETAL",
        "ENERGY": "^CNXENERGY",
        "FINANCIAL": "^CNXFIN"
    }

    def __init__(self, data_provider):
        self.provider = data_provider
        
    def evaluate_market_context(self) -> Dict[str, Any]:
        """
        Fetches NIFTY, BANKNIFTY, VIX, and major sectors to determine the Market Regime.
        """
        logger.info("Initializing Market Intelligence Pre-Scan...")
        
        context = {
            "regime": "Sideways",
            "nifty_trend": "Neutral",
            "banknifty_trend": "Neutral",
            "vix_level": 15.0,
            "sector_strength": {},
            "strongest_sectors": [],
            "weakest_sectors": []
        }
        
        try:
            # Helper to convert List[OHLCV] to DataFrame
            def to_df(data):
                if not data:
                    return None
                return pd.DataFrame([{'Close': d.close, 'Open': d.open, 'High': d.high, 'Low': d.low} for d in data])

            # 1. Evaluate NIFTY 50
            nifty_data = self.provider.get_ohlcv("^NSEI", "1d", "3mo")
            nifty_df = to_df(nifty_data)
            if nifty_df is not None and len(nifty_df) > 20:
                nifty_df['EMA20'] = nifty_df['Close'].ewm(span=20, adjust=False).mean()
                latest = nifty_df.iloc[-1]
                if latest['Close'] > latest['EMA20']:
                    context["nifty_trend"] = "Bullish"
                elif latest['Close'] < latest['EMA20']:
                    context["nifty_trend"] = "Bearish"
                    
            # 2. Evaluate BANK NIFTY
            bank_data = self.provider.get_ohlcv("^NSEBANK", "1d", "3mo")
            bank_df = to_df(bank_data)
            if bank_df is not None and len(bank_df) > 20:
                bank_df['EMA20'] = bank_df['Close'].ewm(span=20, adjust=False).mean()
                latest = bank_df.iloc[-1]
                if latest['Close'] > latest['EMA20']:
                    context["banknifty_trend"] = "Bullish"
                elif latest['Close'] < latest['EMA20']:
                    context["banknifty_trend"] = "Bearish"
                    
            # 3. Evaluate INDIA VIX
            vix_data = self.provider.get_ohlcv("^INDIAVIX", "1d", "1mo")
            vix_df = to_df(vix_data)
            if vix_df is not None and len(vix_df) > 0:
                context["vix_level"] = float(vix_df.iloc[-1]['Close'])
                
            # 4. Evaluate Sectors (Proxy for Breadth & Rotation)
            sector_scores = {}
            for sector, symbol in self.SECTOR_INDICES.items():
                s_data = self.provider.get_ohlcv(symbol, "1d", "5d")
                sdf = to_df(s_data)
                if sdf is not None and len(sdf) >= 2:
                    pct_change = ((sdf.iloc[-1]['Close'] - sdf.iloc[-2]['Close']) / sdf.iloc[-2]['Close']) * 100
                    sector_scores[sector] = round(pct_change, 2)
            
            context["sector_strength"] = sector_scores
            
            # Sort sectors
            sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
            if sorted_sectors:
                context["strongest_sectors"] = [s[0] for s in sorted_sectors if s[1] > 0][:3]
                context["weakest_sectors"] = [s[0] for s in sorted_sectors if s[1] < 0][-3:]

            # 5. Determine Market Regime
            vix = context["vix_level"]
            n_trend = context["nifty_trend"]
            b_trend = context["banknifty_trend"]
            
            if vix > 25.0:
                context["regime"] = "High Volatility"
            elif n_trend == "Bullish" and b_trend == "Bullish":
                context["regime"] = "Bull Trend"
            elif n_trend == "Bearish" and b_trend == "Bearish":
                context["regime"] = "Bear Trend"
            elif n_trend == "Bullish" or b_trend == "Bullish":
                context["regime"] = "Sideways Bullish"
            elif n_trend == "Bearish" or b_trend == "Bearish":
                context["regime"] = "Sideways Bearish"
            else:
                context["regime"] = "Sideways"

            logger.info(f"Market Intelligence Completed: {context['regime']} (VIX: {context['vix_level']})")
            
        except Exception as e:
            logger.error(f"Market Intelligence Engine failed: {e}")
            
        return context
