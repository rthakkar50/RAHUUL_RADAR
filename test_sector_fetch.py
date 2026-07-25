from application.data_manager import DataManager
dm = DataManager.get_instance()
df = dm.get_historical_data("^NSEI", period="3mo", interval="1d")
print("Fetched rows:", len(df))
