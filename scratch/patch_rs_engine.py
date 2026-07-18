import sys, os
sys.path.append(os.getcwd())

with open("core/relative_strength_engine.py", "r") as f:
    content = f.read()

# Add weights
if "MARKET_ALPHA_WEIGHT" not in content:
    content = content.replace(
        "    _lock = threading.Lock()",
        "    _lock = threading.Lock()\n    MARKET_ALPHA_WEIGHT = 0.70\n    SECTOR_ALPHA_WEIGHT = 0.30"
    )

# Replacement logic for _update_rs_cache
old_logic = """            nifty_ret = calc_returns(nifty_df)
            
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
                    
                    # Calculate comparative alpha (difference in returns)
                    # We heavily weight shorter term momentum for breakout detection, but need long term for structural RS
                    rs_1d = (stock_ret["1d"] - nifty_ret.get("1d", 0)) * 100
                    rs_5d = (stock_ret["5d"] - nifty_ret.get("5d", 0)) * 100
                    rs_20d = (stock_ret["20d"] - nifty_ret.get("20d", 0)) * 100
                    rs_50d = (stock_ret["50d"] - nifty_ret.get("50d", 0)) * 100
                    rs_100d = (stock_ret["100d"] - nifty_ret.get("100d", 0)) * 100
                    
                    # Composite RS Score (0-100 scale)
                    # Weights: 100D (30%), 50D (30%), 20D (20%), 5D (10%), 1D (10%)
                    composite = (rs_100d * 0.3) + (rs_50d * 0.3) + (rs_20d * 0.2) + (rs_5d * 0.1) + (rs_1d * 0.1)"""

new_logic = """            nifty_ret = calc_returns(nifty_df)
            
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
                    composite = (rs_100d * 0.3) + (rs_50d * 0.3) + (rs_20d * 0.2) + (rs_5d * 0.1) + (rs_1d * 0.1)"""

content = content.replace(old_logic, new_logic)

with open("core/relative_strength_engine.py", "w") as f:
    f.write(content)

print("Patched relative strength engine")
