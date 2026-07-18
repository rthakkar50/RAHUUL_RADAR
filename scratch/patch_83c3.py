import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83c_validation.py", "r") as f:
    content = f.read()

run_str = """fno = get_fno_symbols()
stocks = [Stock(s) for s in fno]"""

good_run_str = """fno = get_fno_symbols()
stocks = [Stock(s["symbol"]) for s in fno]"""

content = content.replace(run_str, good_run_str)

with open("scratch/sprint83c_validation.py", "w") as f:
    f.write(content)

