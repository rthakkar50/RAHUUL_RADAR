import sys, os
sys.path.append(os.getcwd())
from market.universe import get_fno_symbols

mapping = {
    'Banking': 'BANKING',
    'Financial': 'FINANCIAL SERVICES',
    'IT': 'IT',
    'Auto': 'AUTO',
    'Auto Ancillary': 'AUTO',
    'Pharma': 'PHARMA',
    'Healthcare': 'PHARMA',
    'FMCG': 'FMCG',
    'Metal': 'METAL',
    'Energy': 'ENERGY',
    'Realty': 'REALTY',
    'Media': 'MEDIA',
    'Chemicals': 'CHEMICAL',
    'Fertilizers': 'CHEMICAL',
    'Capital Goods': 'CAPITAL GOODS',
    'Infrastructure': 'INFRASTRUCTURE',
    'Cement': 'INFRASTRUCTURE', # Can be mapped here or unknown
    'Building Materials': 'INFRASTRUCTURE'
}

symbols = get_fno_symbols()
out = "STOCK_SECTOR_MAP = {\n"
for s in symbols:
    sym = s['symbol']
    sec = s.get('sector', 'UNKNOWN')
    mapped_sec = mapping.get(sec, 'UNKNOWN')
    
    # manual overrides for PSUs since universe doesn't split PSU vs Pvt bank easily unless we check name
    if 'BANK' in sym and mapped_sec == 'BANKING':
        # Just use BANKING for all banks for simplicity, or split to PSU if needed
        pass
    out += f'    "{sym}": "{mapped_sec}",\n'
out += "}\n"

with open("scratch/stock_sector_map.py", "w") as f:
    f.write(out)

print("Map generated")
