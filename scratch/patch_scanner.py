import sys, os
sys.path.append(os.getcwd())

with open("scanner/scanner_engine.py", "r") as f:
    content = f.read()

old_rs_block = """                rs_score = 0.0
                if getattr(self, 'rs_engine', None):
                    rs_data = self.rs_engine.get_rs_data(stock.symbol)
                    rs_score = float(rs_data.get("score", 0.0)) if rs_data else 0.0"""

new_rs_block = """                rs_score = 0.0
                rs_momentum = 50.0
                if getattr(self, 'rs_engine', None):
                    rs_data = self.rs_engine.get_rs_data(stock.symbol)
                    if rs_data:
                        rs_score = float(rs_data.get("score", 0.0))
                        rs_momentum = float(rs_data.get("momentum", 50.0))"""

content = content.replace(old_rs_block, new_rs_block)

old_setattr_block = """                setattr(scan_result, "raw_score", getattr(decision_result, "raw_score", 0))
                setattr(scan_result, "adjusted_score", getattr(decision_result, "adjusted_score", decision_result.total_score))
                setattr(scan_result, "confidence", decision_result.confidence)"""

new_setattr_block = """                setattr(scan_result, "raw_score", getattr(decision_result, "raw_score", 0))
                setattr(scan_result, "adjusted_score", getattr(decision_result, "adjusted_score", decision_result.total_score))
                setattr(scan_result, "confidence", decision_result.confidence)
                setattr(scan_result, "relative_momentum", rs_momentum)"""

content = content.replace(old_setattr_block, new_setattr_block)

with open("scanner/scanner_engine.py", "w") as f:
    f.write(content)

print("Patched scanner engine")
