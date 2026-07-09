import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ChartService:
    def __init__(self):
        pass

    def get_chart_data(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        from core.market_data_service import MarketDataService
        
        svc = MarketDataService()
        df = svc.get_historical_data(symbol, period="1mo", interval="1d")
        
        candles = []
        if df is not None and not df.empty:
            for idx, row in df.iterrows():
                candles.append({
                    "timestamp": idx.strftime("%Y-%m-%d"),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"]
                })
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": candles,
            "overlays": {
                "ema": True,
                "vwap": False
            }
        }
