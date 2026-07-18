import sys, os
sys.path.append(os.getcwd())

with open("core/sector_rotation_engine.py", "r") as f:
    content = f.read()

with open("scratch/stock_sector_map.py", "r") as f:
    map_code = f.read()

# Replace the get_stock_sector method
old_method = """    def get_stock_sector(self, symbol):
        \"\"\"
        Maps a stock to its sector.
        For a production system, this should query a local DB or static map.
        As a placeholder, we return IT for TCS/INFY, BANKING for HDFCBANK, etc.
        \"\"\"
        symbol = symbol.upper()
        if any(x in symbol for x in ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM']):
            return "IT"
        if any(x in symbol for x in ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK']):
            return "BANKING"
        if any(x in symbol for x in ['TATAMOTORS', 'MARUTI', 'M&M', 'HEROMOTOCO', 'BAJAJ-AUTO']):
            return "AUTO"
        if any(x in symbol for x in ['RELIANCE', 'ONGC', 'NTPC', 'POWERGRID']):
            return "ENERGY"
        if any(x in symbol for x in ['ITC', 'HINDUNILVR', 'NESTLEIND', 'BRITANNIA']):
            return "FMCG"
        if any(x in symbol for x in ['TATASTEEL', 'JSWSTEEL', 'HINDALCO']):
            return "METAL"
        if any(x in symbol for x in ['SUNPHARMA', 'CIPLA', 'DRREDDY', 'DIVISLAB']):
            return "PHARMA"
            
        return "UNKNOWN"
"""

new_method = f"""
    {map_code.replace(chr(10), chr(10) + '    ')}

    def get_stock_sector(self, symbol):
        \"\"\"
        Maps a stock to its sector.
        \"\"\"
        return self.STOCK_SECTOR_MAP.get(symbol.upper(), "UNKNOWN")
        
    def get_sector_symbol(self, sector_name):
        \"\"\"
        Returns the Yahoo Finance symbol for a given sector name, or None.
        \"\"\"
        return self.SECTORS.get(sector_name)
"""

new_content = content.replace(old_method, new_method)

with open("core/sector_rotation_engine.py", "w") as f:
    f.write(new_content)

print("Patched sector rotation engine")
