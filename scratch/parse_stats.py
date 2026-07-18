import re

log_path = "/Users/pr/.gemini/antigravity/brain/4a7389b1-8fc9-45e5-b25f-ff595911c4db/.system_generated/tasks/task-3771.log"

buy_scores = []
sell_scores = []
watch_scores = []

with open(log_path, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ENGINE SCORE   :" in line:
        score = float(line.split(":")[1].strip())
        decision_line = lines[i+1]
        decision = decision_line.split(":")[1].strip()
        
        if decision == "BUY":
            buy_scores.append(score)
        elif decision == "SELL":
            sell_scores.append(score)
        elif decision == "WATCH":
            watch_scores.append(score)

total_scanned = 178  # Known from F&O Universe count
wait_count = total_scanned - (len(buy_scores) + len(sell_scores) + len(watch_scores))

print(f"Total scanned: {total_scanned}")
print(f"BUY count: {len(buy_scores)}")
print(f"SELL count: {len(sell_scores)}")
print(f"WATCH count: {len(watch_scores)}")
print(f"WAIT count: {wait_count}")

def print_stats(name, scores):
    if not scores:
        print(f"\n{name} Stats: N/A")
        return
    avg = sum(scores) / len(scores)
    min_s = min(scores)
    max_s = max(scores)
    print(f"\nAverage {name} score: {avg:.2f}")
    print(f"Lowest {name} score: {min_s:.2f}")
    print(f"Highest {name} score: {max_s:.2f}")

print_stats("BUY", buy_scores)
print_stats("SELL", sell_scores)
print_stats("WATCH", watch_scores)
