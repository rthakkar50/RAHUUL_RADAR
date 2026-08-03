import re

log_file = "/Users/pr/.gemini/antigravity/brain/a9dd36de-f5df-4156-9805-b7006b6a9e5a/.system_generated/tasks/task-9554.log"

with open(log_file, "r") as f:
    text = f.read()

symbols = re.findall(r"ENGINE SYMBOL\s+:\s+(.+)", text)
scores = re.findall(r"ENGINE SCORE\s+:\s+([0-9.]+)", text)
decisions = re.findall(r"ENGINE DECISION:\s+(.+)", text)

print(f"Total symbols found: {len(symbols)}")
buy_candidates = []
for sym, score, dec in zip(symbols, scores, decisions):
    if dec.strip() == "BUY":
        buy_candidates.append((sym.strip(), float(score)))

print(f"Total BUY candidates found: {len(buy_candidates)}")
for b in buy_candidates:
    print(b)
