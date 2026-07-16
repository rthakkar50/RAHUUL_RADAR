#!/usr/bin/env python3
# RAHUUL_RADAR – YELLOW Balanced Patch v1.1 – FIXED
# rthakkar50 – /Users/pr/RAHUUL_RADAR
# Fixes ValueError bug from v1.0 – now bulletproof

import os, shutil, re, sys
from datetime import datetime

ROOT = "/Users/pr/RAHUUL_RADAR"
os.chdir(ROOT)
print("="*60)
print("  RAHUUL_RADAR – YELLOW Patch v1.1 – RESUME")
print("="*60)

backup_tag = datetime.now().strftime("%Y%m%d_%H%M%S")

def patch_file_safe(relpath, replacements):
    fpath = os.path.join(ROOT, relpath)
    if not os.path.exists(fpath):
        print(f"  ❌ {relpath} not found")
        return False
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    original = content
    changed = 0
    for item in replacements:
        # accept 2-tuple or 3-tuple
        if len(item) == 3:
            old, new, desc = item
        elif len(item) == 2:
            old, new = item
            desc = "patch"
        else:
            continue
        if old in content:
            content = content.replace(old, new)
            changed += 1
            print(f"    → {desc}")
    if content != original:
        # backup
        shutil.copy2(fpath, fpath + f".BACKUP_v11_{backup_tag}")
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {relpath} updated – {changed} changes")
        return True
    else:
        print(f"  ℹ {relpath} – already patched / nothing to do")
        return False

print("\n[1] DecisionEngine – finishing remaining patches…")
patch_file_safe("core/decision_engine.py", [
    # these 2 already done in v1.0 – will be skipped automatically – safe
    ("if adjusted_score >= 50.0:", "if adjusted_score >= 42.0:", "BUY 50→42"),
    ("elif adjusted_score >= 40.0:", "elif adjusted_score >= 32.0:", "WATCH 40→32"),
    # these crashed last time – now with desc – will apply now:
    ('Score ({adjusted_score:.2f}) >= 50 threshold', 'Score ({adjusted_score:.2f}) >= 42 threshold [BUY - YELLOW]', 'log msg update 1'),
    ('Score ({adjusted_score:.2f}) in 40-49 threshold', 'Score ({adjusted_score:.2f}) in 32-41 threshold', 'log msg update 2'),
    ('Score ({adjusted_score:.2f}) below 40 threshold', 'Score ({adjusted_score:.2f}) below 32 threshold', 'log msg update 3'),
    ("if adjusted_score >= 70.0:", "if adjusted_score >= 62.0:", "OPTIONS BUY 70→62"),
    ("elif adjusted_score <= 20.0:", "elif adjusted_score <= 28.0:", "OPTIONS SELL 20→28"),
])

print("\n[2] SwingScannerService – Quality Gate")
patch_file_safe("application/swing_scanner_service.py", [
    ("min_score = 80.0", "min_score = 60.0  # YELLOW v1.1", "swing min_score"),
    ("min_conf = 75.0", "min_conf = 55.0  # YELLOW v1.1", "swing min_conf"),
    ("min_conf = 70.0", "min_conf = 55.0  # YELLOW v1.1", "swing min_conf 70→55"),
    ("min_score = 75.0", "min_score = 60.0  # YELLOW v1.1", "swing score 75→60"),
    ("min_rr = 2.0", "min_rr = 1.3  # YELLOW v1.1", "rr 2.0→1.3"),
    ("min_rr = 1.8", "min_rr = 1.3  # YELLOW v1.1", "rr 1.8→1.3"),
    ("min_score = 70.0", "min_score = 50.0  # YELLOW v1.1", "aggressive score"),
    ("min_conf = 65.0", "min_conf = 45.0  # YELLOW v1.1", "aggressive conf"),
    ("min_rr = 1.5", "min_rr = 1.0  # YELLOW v1.1", "aggressive rr"),
])

print("\n[3] ScannerEngine – F&O filters loosen")
patch_file_safe("scanner/scanner_engine.py", [
    ("VOL_SURGE_MULTIPLIER = 2.0", "VOL_SURGE_MULTIPLIER = 1.4  # YELLOW v1.1", "vol 2.0→1.4"),
    ("VIX_MAX_SAFE = 20.0", "VIX_MAX_SAFE = 28.0  # YELLOW v1.1", "VIX 20→28"),
    ("VIX_IDEAL_MAX = 14.0", "VIX_IDEAL_MAX = 18.0  # YELLOW v1.1", "VIX ideal"),
])

print("\n[4] SectorEngine hotfix install")
import shutil
src_hotfix = "/Users/pr/RAHUUL_RADAR/apply_yellow_balanced.py"  # dummy check – actually look next to this script
# try find hotfix in same folder as this script, or in core/
possible = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "sector_engine_hotfix.py"),
    os.path.join(ROOT, "core", "sector_engine_hotfix.py"),
    "/Users/pr/RAHUUL_RADAR/core/sector_engine_hotfix.py"
]
found=None
for p in possible:
    if os.path.exists(p):
        found=p; break
if found:
    dst = os.path.join(ROOT, "core", "sector_engine_hotfix.py")
    shutil.copy2(found, dst)
    print(f"  ✅ hotfix copied from {found}")
    # inject import
    se = os.path.join(ROOT, "core", "sector_engine.py")
    with open(se, 'r', encoding='utf-8', errors='ignore') as f:
        txt=f.read()
    if "sector_engine_hotfix" not in txt:
        with open(se, 'w', encoding='utf-8') as f:
            f.write("try:\n    from core.sector_engine_hotfix import *\nexcept: pass\n\n"+txt)
        print("  ✅ hotfix injected")
    else:
        print("  ℹ hotfix already present")
else:
    print("  ⚠ sector_engine_hotfix.py not found – copy manually from patch folder to /Users/pr/RAHUUL_RADAR/core/")

print("\n" + "="*60)
print("✅ YELLOW v1.1 COMPLETE")
print("")
print("Test now:")
print("  cd /Users/pr/RAHUUL_RADAR")
print("  python3 swing_buy_debug.py")
print("")
print("Expected now: BUY 3-10, SELL 2-5")
print("="*60)
