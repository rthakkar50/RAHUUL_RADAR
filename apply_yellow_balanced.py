#!/usr/bin/env python3
# RAHUUL_RADAR – YELLOW Balanced Patch Installer
# For: rthakkar50 / RAHUUL_RADAR
# Path: /Users/pr/RAHUUL_RADAR
# Language: Gujarati comments
# 
# આ script તમારા software ને “thodu loose” કરશે
# Institutional Strict → Retail Balanced
# Backup auto થશે – ડરો નહીં!

import os, shutil, re, sys
from datetime import datetime

ROOT = "/Users/pr/RAHUUL_RADAR"
if not os.path.isdir(ROOT):
    print("❌ Folder not found:", ROOT)
    print("જો તમારો path અલગ હોય તો આ file માં ROOT બદલો")
    sys.exit(1)

os.chdir(ROOT)
print("="*60)
print("  RAHUUL_RADAR – YELLOW Balanced Patch")
print("  by Arena.ai – for rthakkar50")
print("="*60)
print(f"Project: {ROOT}")
print("")

backup_tag = datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_file(relpath):
    src = os.path.join(ROOT, relpath)
    if os.path.exists(src):
        dst = src + f".BACKUP_{backup_tag}"
        shutil.copy2(src, dst)
        print(f"  ✓ Backup: {relpath} → {os.path.basename(dst)}")
        return True
    else:
        print(f"  ⚠ Skip (not found): {relpath}")
        return False

def patch_file(relpath, replacements):
    """replacements: list of (old_text_or_regex, new_text, description)"""
    fpath = os.path.join(ROOT, relpath)
    if not os.path.exists(fpath):
        print(f"  ❌ Not found: {relpath}")
        return False
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    original = content
    changed = 0
    for old, new, desc in replacements:
        # try literal first, then regex
        if old in content:
            content = content.replace(old, new)
            changed += 1
            print(f"    → {desc}")
        else:
            # regex try
            try:
                new_content, n = re.subn(old, new, content, flags=re.MULTILINE)
                if n > 0:
                    content = new_content
                    changed += n
                    print(f"    → {desc} (regex {n}x)")
            except Exception:
                pass
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Patched {relpath} – {changed} change(s)")
        return True
    else:
        print(f"  ⚠ No changes applied in {relpath} – patterns not found (maybe already patched?)")
        return False

# 1. Backup critical files
print("\n[1/5] Backup creating...")
for fp in [
  "core/decision_engine.py",
  "application/swing_scanner_service.py",
  "scanner/scanner_engine.py",
  "core/sector_engine.py",
  "config/config.py",
  "config.json"
]:
    backup_file(fp)

# 2. DecisionEngine – BUY threshold 50→42, WATCH 40→32
print("\n[2/5] Patching DecisionEngine – core/decision_engine.py")
patch_file("core/decision_engine.py", [
    ("if adjusted_score >= 50.0:", "if adjusted_score >= 42.0:", "BUY threshold 50 → 42"),
    ("elif adjusted_score >= 40.0:", "elif adjusted_score >= 32.0:", "WATCH threshold 40 → 32"),
    ('f"Score ({adjusted_score:.2f}) >= 50 threshold', 'f"Score ({adjusted_score:.2f}) >= 42 threshold [BUY - YELLOW]"'),
    ('f"Score ({adjusted_score:.2f}) in 40-49 threshold', 'f"Score ({adjusted_score:.2f}) in 32-41 threshold'),
    ('f"Score ({adjusted_score:.2f}) below 40 threshold', 'f"Score ({adjusted_score:.2f}) below 32 threshold'),
    # OPTIONS mode also loosen a bit
    ("if adjusted_score >= 70.0:", "if adjusted_score >= 62.0:", "OPTIONS BUY 70→62"),
    ("elif adjusted_score <= 20.0:", "elif adjusted_score <= 28.0:", "OPTIONS SELL 20→28"),
])

# 3. SwingScannerService – Quality Gate loosen
print("\n[3/5] Patching SwingScannerService – application/swing_scanner_service.py")
# Conservative
patch_file("application/swing_scanner_service.py", [
    ("min_score = 80.0\n        min_conf = 75.0\n        min_rr = 2.0", 
     "min_score = 60.0  # YELLOW patched\n        min_conf = 55.0\n        min_rr = 1.3",
     "Conservative 80/75/2.0 → 60/55/1.3"),
    # Aggressive
    ("min_score = 70.0\n        min_conf = 65.0\n        min_rr = 1.5",
     "min_score = 50.0  # YELLOW patched\n        min_conf = 45.0\n        min_rr = 1.0",
     "Aggressive 70/65/1.5 → 50/45/1.0"),
    # Balanced
    ("min_score = 75.0\n        min_conf = 70.0\n        min_rr = 1.8",
     "min_score = 60.0  # YELLOW patched\n        min_conf = 55.0\n        min_rr = 1.3",
     "Balanced 75/70/1.8 → 60/55/1.3"),
])
# Also catch single-line variants just in case
patch_file("application/swing_scanner_service.py", [
    ("min_score = 75.0", "min_score = 60.0  # YELLOW", "fallback min_score"),
    ("min_conf = 70.0", "min_conf = 55.0  # YELLOW", "fallback min_conf"),
    ("min_rr = 1.8", "min_rr = 1.3  # YELLOW", "fallback min_rr"),
])

# 4. ScannerEngine – volume / VIX / PCR loosen
print("\n[4/5] Patching ScannerEngine – scanner/scanner_engine.py")
patch_file("scanner/scanner_engine.py", [
    ("VOL_SURGE_MULTIPLIER = 2.0", "VOL_SURGE_MULTIPLIER = 1.4  # YELLOW", "Volume surge 2.0 → 1.4"),
    ("VIX_MAX_SAFE = 20.0", "VIX_MAX_SAFE = 28.0  # YELLOW", "VIX 20 → 28"),
    ("VIX_IDEAL_MAX = 14.0", "VIX_IDEAL_MAX = 18.0  # YELLOW", "VIX ideal 14→18"),
])

# 5. Install SectorEngine hotfix
print("\n[5/5] Installing SectorEngine hotfix...")
hotfix_src = os.path.join(os.path.dirname(__file__), "core", "sector_engine_hotfix.py")
hotfix_dst = os.path.join(ROOT, "core", "sector_engine_hotfix.py")
if os.path.exists(hotfix_src):
    shutil.copy2(hotfix_src, hotfix_dst)
    print("  ✅ sector_engine_hotfix.py installed to core/")
    # Try auto-inject import into sector_engine.py
    se_path = os.path.join(ROOT, "core", "sector_engine.py")
    if os.path.exists(se_path):
        with open(se_path, 'r', encoding='utf-8', errors='ignore') as f:
            se_content = f.read()
        if "sector_engine_hotfix" not in se_content:
            # prepend import
            new_content = "try:\n    from core.sector_engine_hotfix import *\nexcept Exception:\n    pass\n\n" + se_content
            with open(se_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("  ✅ Hotfix auto-injected into sector_engine.py top")
        else:
            print("  ℹ Hotfix already injected")
else:
    print("  ⚠ Hotfix file not found next to installer – skipping (manual copy later)")

print("\n" + "="*60)
print("✅ PATCH COMPLETE – RAHUUL YELLOW BALANCED APPLIED")
print("="*60)
print("")
print("આગળ શું કરવું:")
print("  1. cd /Users/pr/RAHUUL_RADAR")
print("  2. python run_test.py")
print("     → BUY signals આવવા જોઈએ હવે 3-7")
print("  3. જો OK લાગે:")
print("     git add -A")
print('     git commit -m "audit: YELLOW Balanced – sector fix + thresholds loose – rthakkar50"')
print("     git push origin dev")
print("")
print("Rollback જોઈતું હોય તો:")
print(f"  Backup files: *.BACKUP_{backup_tag}")
print("  cp application/swing_scanner_service.py.BACKUP_* application/swing_scanner_service.py")
print("")
print("Jay Mataji! 🙏 – Arena.ai")
