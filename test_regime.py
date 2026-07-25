from core.market_regime_engine import MarketRegimeEngine
import logging

logging.basicConfig(level=logging.DEBUG)
engine = MarketRegimeEngine()
print(engine.get_current_regime())
