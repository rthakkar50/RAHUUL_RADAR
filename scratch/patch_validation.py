import sys, os
sys.path.append(os.getcwd())

with open("scratch/sprint83b_validation.py", "r") as f:
    content = f.read()

old_print = """for sym, (score, decision, conf) in top_20:
    print(f"{sym}: RS={score:.2f}, Decision={decision}, Conf={conf:.2f}")"""

new_print = """for sym, (score, decision, conf) in top_20:
    # We need momentum. Let's look it up from the engine
    rs_data = rs_engine.get_rs_data(sym)
    mom = rs_data.get("momentum", 50.0)
    print(f"{sym}: RS={score:.2f}, Momentum={mom:.2f}, Decision={decision}, Conf={conf:.2f}")"""

content = content.replace(old_print, new_print)

old_print_bot = """for sym, (score, decision, conf) in bottom_20:
    print(f"{sym}: RS={score:.2f}, Decision={decision}, Conf={conf:.2f}")"""

new_print_bot = """for sym, (score, decision, conf) in bottom_20:
    rs_data = rs_engine.get_rs_data(sym)
    mom = rs_data.get("momentum", 50.0)
    print(f"{sym}: RS={score:.2f}, Momentum={mom:.2f}, Decision={decision}, Conf={conf:.2f}")"""

content = content.replace(old_print_bot, new_print_bot)

with open("scratch/sprint83b_validation.py", "w") as f:
    f.write(content)

