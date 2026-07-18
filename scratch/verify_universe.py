import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from market.universe import get_all_symbols

symbols = get_all_symbols()
print(f"Total count: {len(symbols)}")
print("First 20 symbols:")
for item in symbols[:20]:
    print(item['symbol'])
