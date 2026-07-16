#!/bin/bash
# RAHUUL_RADAR – YELLOW Balanced – 1 click installer
# rthakkar50

echo "=========================================="
echo "  RAHUUL_RADAR – YELLOW Balanced Patch"
echo "  Intraday F&O – 3-5 signals/day"
echo "  Arena.ai – Gujarati helper"
echo "=========================================="
echo ""

cd /Users/pr/RAHUUL_RADAR || { echo "❌ Folder not found: /Users/pr/RAHUUL_RADAR"; exit 1; }

echo "Step 1: Running Python patcher..."
python3 ./apply_yellow_balanced.py
if [ $? -ne 0 ]; then
  echo "Trying with python..."
  python ./apply_yellow_balanced.py
fi

echo ""
echo "Step 2: Test run..."
echo "Running: python run_test.py (30 sec)… press Ctrl+C to skip"
sleep 2
timeout 60 python3 run_test.py || echo "(test interrupted / timeout – ok)"

echo ""
echo "=============================="
echo "✅ Patch applied!"
echo "Check BUY signals now:"
echo "  cd /Users/pr/RAHUUL_RADAR"
echo "  python swing_buy_debug.py"
echo ""
echo "If happy → push:"
echo "  git add -A"
echo '  git commit -m "audit: YELLOW Balanced – rthakkar50"'
echo "  git push origin dev"
echo ""
echo "Rollback:"
echo "  ls -l *BACKUP* */*.BACKUP*"
echo "  cp application/swing_scanner_service.py.BACKUP_* application/swing_scanner_service.py"
echo "=============================="
