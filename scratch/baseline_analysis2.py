import sys, os, json
from collections import Counter
sys.path.append(os.getcwd())
from application.swing_scanner_service import SwingScannerService

stats_data = []
service = SwingScannerService()

# We will patch the part of execute_swing_scan that applies the Quality Gates!
# Actually, the easiest way is to let execute_swing_scan finish, and just intercept the print statements or intercept process_post_scan.

# Let's override the `process_post_scan` and the threshold block.
# Even better, we can just patch `logger.info` or `print` to capture the output, but wait, 
# `SwingScannerService.execute_swing_scan` has a loop over `processed_results` where it does:
# downgrade_reasons.append("...")
# So we can patch `processed_results`? No, it's a local variable.

# We will just patch MasterSignalPipeline.process
original_process = service.pipeline.process
def hooked_process(r):
    res = original_process(r)
    # The actual score used in threshold is r.adjusted_score or r.total_score
    engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
    # We store it in res
    res["original_engine_score"] = engine_score
    res["raw_decision"] = r.decision
    return res
service.pipeline.process = hooked_process

# Now we need to capture the downgrade reasons.
# execute_swing_scan returns `qualified_results`. It doesn't return the ones that were downgraded and dropped!
# Wait, if a trade is downgraded to WATCH, it IS returned as a WATCH.
# If it is dropped (e.g. score < 50), it is not returned.

# Let's just redefine the whole execute_swing_scan temporarily in the script, or just patch the threshold values to 0 so nothing is dropped, and then manually apply the thresholds to see what WOULD have been dropped.
