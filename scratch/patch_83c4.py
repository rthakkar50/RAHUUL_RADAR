import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83c_validation.py", "r") as f:
    content = f.read()

bad_str = 'stocks = [Stock(s["symbol"]) for s in fno]'
good_str = 'stocks = [Stock(s["symbol"], "", s.get("sector", ""), True, False) for s in fno]'

content = content.replace(bad_str, good_str)

with open("scratch/sprint83c_validation.py", "w") as f:
    f.write(content)
