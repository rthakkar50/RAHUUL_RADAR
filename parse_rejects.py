import re

log_file = "/Users/pr/.gemini/antigravity/brain/4a7389b1-8fc9-45e5-b25f-ff595911c4db/.system_generated/tasks/task-2557.log"

rejections = 0
with open(log_file) as f:
    for line in f:
        if "REJECTED" in line or "Skipping" in line or "Failed" in line:
            pass

# Since pipeline doesn't log REJECTED, let's just grep "DEBUG: current_trend is " which is printed for every call to pipeline.
# Wait, "DEBUG: current_trend is " is printed when `not signals` (mock signals).
