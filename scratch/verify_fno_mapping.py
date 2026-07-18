import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market.universe import get_all_symbols, get_fno_symbols
from data.stocks import Stock

fno_data = get_all_symbols()
fno_symbols_set = {item["symbol"] for item in get_fno_symbols()}

stock_list = []
fno_count = 0
non_fno_count = 0

for item in fno_data:
    sym = item["symbol"]
    sector = item.get("sector", "N/A")
    is_fno = sym in fno_symbols_set
    if is_fno:
        fno_count += 1
    else:
        non_fno_count += 1
    stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=is_fno, is_nifty50=False))

print(f"Total Symbols: {len(stock_list)}")
print(f"F&O Symbols: {fno_count}")
print(f"Non-F&O Symbols: {non_fno_count}")
print("\nSample Output:")
for s in stock_list:
    if s.symbol in ["RELIANCE.NS", "SBIN.NS", "TCS.NS", "ZOMATO.NS"]:
        print(f"{s.symbol.replace('.NS', '')}\nis_fno={s.is_fno}\n")
