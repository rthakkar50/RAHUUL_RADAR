import sys, os, time
sys.path.append(os.getcwd())
from core.relative_strength_engine import RelativeStrengthEngine

rs = RelativeStrengthEngine()
rs.get_rs_data()
while rs.is_updating:
    time.sleep(1)

rs_data = rs.get_rs_data()

for sym, data in list(rs_data.items())[:10]:
    print(f"{sym}: Score={data.get('score')}, Momentum={data.get('momentum')}")
