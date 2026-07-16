import json

log_file = "/Users/pr/.gemini/antigravity/brain/4a7389b1-8fc9-45e5-b25f-ff595911c4db/.system_generated/tasks/task-2557.log"

reasons = {
    "No market data (Yahoo timeout)": [],
    "Weak Setup (Score/Conf < 50)": [],
    "Signal WAIT (Pipeline dropped)": [],
    "Risk filter (Invalid entry/sl)": [],
    "RR filter (Downgraded & Filtered)": [],
    "Other": []
}

from collections import defaultdict
decisions = defaultdict(int)

# We can actually just grep the output of the task!
with open(log_file) as f:
    lines = f.readlines()
    
# Let's count ENGINE DECISION
# ENGINE DECISION is output by scanner_engine, NOT pipeline.
import re
for line in lines:
    m = re.search(r"ENGINE DECISION:\s*(.+)", line)
    if m:
        decisions[m.group(1).strip()] += 1
        
print("Scanner Engine Decisions:")
for k, v in decisions.items():
    print(f"{k}: {v}")
    
# Let's count Threshold Downgrade
downgrades = 0
for i, line in enumerate(lines):
    if "Threshold Downgrade" in line:
        downgrades += 1
print(f"Total threshold downgrades: {downgrades}")

