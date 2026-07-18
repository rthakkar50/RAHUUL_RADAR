import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83c_validation.py", "r") as f:
    content = f.read()

append_str = """
import math
valid_results = [r for r in results if r.status != "ERROR" and getattr(r, "relative_momentum", None) is not None]

momentums = [getattr(r, "relative_momentum", 50.0) for r in valid_results]
avg_mom = sum(momentums) / len(momentums) if momentums else 0
high_mom = max(momentums) if momentums else 0
low_mom = min(momentums) if momentums else 0
variance = sum((x - avg_mom) ** 2 for x in momentums) / len(momentums) if momentums else 0
std_mom = math.sqrt(variance)
mom_gt_80 = len([x for x in momentums if x > 80])
mom_lt_20 = len([x for x in momentums if x < 20])

print("\\n--- MOMENTUM STATISTICS ---")
print(f"Average Momentum: {avg_mom:.2f}")
print(f"Highest Momentum: {high_mom:.2f}")
print(f"Lowest Momentum: {low_mom:.2f}")
print(f"Standard Deviation: {std_mom:.2f}")
print(f"Momentum > 80: {mom_gt_80}")
print(f"Momentum < 20: {mom_lt_20}")

print("\\n--- TOP 20 MOMENTUM STOCKS ---")
sorted_by_mom = sorted(valid_results, key=lambda x: getattr(x, "relative_momentum", 50.0), reverse=True)
for r in sorted_by_mom[:20]:
    mom = getattr(r, "relative_momentum", 50.0)
    rs = getattr(r, "relative_strength_score", 0.0)
    print(f"{r.symbol}: Mom={mom:.2f}, RS={rs:.2f}, Decision={r.signal.name}, Conf={r.confidence:.2f}")

print("\\n--- BOTTOM 20 MOMENTUM STOCKS ---")
for r in reversed(sorted_by_mom[-20:]):
    mom = getattr(r, "relative_momentum", 50.0)
    rs = getattr(r, "relative_strength_score", 0.0)
    print(f"{r.symbol}: Mom={mom:.2f}, RS={rs:.2f}, Decision={r.signal.name}, Conf={r.confidence:.2f}")

buy_moms = [getattr(r, "relative_momentum", 50.0) for r in valid_results if r.is_buy() or r.is_strong_buy()]
sell_moms = [getattr(r, "relative_momentum", 50.0) for r in valid_results if r.is_sell()]
watch_moms = [getattr(r, "relative_momentum", 50.0) for r in valid_results if r.is_watch()]

print("\\n--- DECISION CORRELATION RAW ---")
print(f"BUY Avg Mom: {sum(buy_moms)/len(buy_moms) if buy_moms else 0:.2f}")
print(f"SELL Avg Mom: {sum(sell_moms)/len(sell_moms) if sell_moms else 0:.2f}")
print(f"WATCH Avg Mom: {sum(watch_moms)/len(watch_moms) if watch_moms else 0:.2f}")
"""

content += append_str

with open("scratch/sprint83c_validation.py", "w") as f:
    f.write(content)

