import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83c_validation.py", "r") as f:
    content = f.read()

import_str = "from ranking.score_engine import ScoreEngine\nfrom core.relative_strength_engine import RelativeStrengthEngine\n"
content = content.replace("from ranking.score_engine import ScoreEngine\n", import_str)

init_str = "scanner = ScannerEngine("
good_init_str = """
rs_engine = RelativeStrengthEngine()
rs_engine.get_rs_data() # force cache trigger
import time
time.sleep(2)
scanner = ScannerEngine(
"""
content = content.replace(init_str, good_init_str)

run_str = "scanner.data_provider.connect()"
good_run_str = "scanner.rs_engine = rs_engine\nscanner.data_provider.connect()"
content = content.replace(run_str, good_run_str)

with open("scratch/sprint83c_validation.py", "w") as f:
    f.write(content)
