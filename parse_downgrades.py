import re

with open("/Users/pr/.gemini/antigravity/brain/4a7389b1-8fc9-45e5-b25f-ff595911c4db/.system_generated/tasks/task-3008.log", "r") as f:
    content = f.read()

blocks = content.split("Threshold Downgrade")[1:]
count_score_only = 0
count_conf_only = 0
count_both = 0
count_neither = 0

additional_passes = 0
additional_still_rejected = 0

for b in blocks:
    score_match = re.search(r"Score:\s*([\d\.]+)", b)
    conf_match = re.search(r"Confidence:\s*([\d\.]+)", b)
    reasons_match = re.search(r"Reasons:\s*\[(.*?)\]", b)
    
    if not score_match or not conf_match or not reasons_match:
        continue
        
    score = float(score_match.group(1))
    conf = float(conf_match.group(1))
    reasons = reasons_match.group(1)
    
    has_score = "Score below directional threshold" in reasons
    has_conf = "Confidence below directional threshold" in reasons
    
    if has_score and has_conf:
        count_both += 1
    elif has_score:
        count_score_only += 1
    elif has_conf:
        count_conf_only += 1
    else:
        count_neither += 1
        
    # How many additional trades would pass if Score reduced from 75 to 65?
    # This means score >= 65 is passing.
    # Currently, they were rejected because score < 75.
    if has_score: # It failed the 75 threshold
        if score >= 65:
            # It now passes the score threshold!
            additional_passes += 1
            # But would it still be rejected by confidence (conf < 70)?
            if conf < 70:
                additional_still_rejected += 1

print("Rejected because Score < 75:", count_score_only)
print("Rejected because Confidence < 70:", count_conf_only)
print("Rejected because BOTH:", count_both)
print("Additional trades passing Score threshold (65):", additional_passes)
print("Of those, still rejected by Confidence (70):", additional_still_rejected)

