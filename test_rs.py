from core.relative_strength_engine import RelativeStrengthEngine
from market.data_provider import MarketDataProvider
from application.data_manager import DataManager
from market.yahoo_provider import YahooFinanceProvider

import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize provider and connect
provider = YahooFinanceProvider()
provider.connect()

# Set provider in DataManager
dm = DataManager.get_instance()
dm.primary_provider = provider

rs = RelativeStrengthEngine()
rs._update_rs_cache()
data = rs.get_rs_data("RELIANCE.NS")
print("RS Data for RELIANCE.NS:", data)
