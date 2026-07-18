import sys, os, time
sys.path.append(os.getcwd())
from core.relative_strength_engine import RelativeStrengthEngine

rs = RelativeStrengthEngine()
rs._update_rs_cache()
data = rs.get_rs_data()

if data:
    scores = [v['score'] for v in data.values()]
    print(f"Total Stocks: {len(scores)}")
    print(f"Avg Score: {sum(scores)/len(scores):.2f}")
    print(f"Max Score: {max(scores):.2f}")
    print(f"Min Score: {min(scores):.2f}")
else:
    print("No data retrieved.")
