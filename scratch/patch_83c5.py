import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83c_validation.py", "r") as f:
    content = f.read()

run_str = "print(\"Running F&O Scan...\")"
good_run_str = "scanner.data_provider.connect()\nprint(\"Running F&O Scan...\")"

content = content.replace(run_str, good_run_str)

with open("scratch/sprint83c_validation.py", "w") as f:
    f.write(content)
