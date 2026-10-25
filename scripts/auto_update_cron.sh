#!/usr/bin/env bash
# ==============================================================================
# RAHUUL_RADAR Enterprise VPS Hardened Auto-Update Script
# ==============================================================================
# Safely synchronizes 'dev' branch from GitHub, takes transactional pre-update
# SQLite database backups, applies fast-forward updates only without clobbering
# runtime data, restarts systemd service 'rahuul_radar.service' via non-interactive
# sudo, and verifies API health before reporting success.
# ==============================================================================
set -eo pipefail

WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORK_DIR"

mkdir -p "$WORK_DIR/logs"
LOG_FILE="$WORK_DIR/logs/auto_update.log"
LOCK_FILE="${AUTO_UPDATE_LOCK_FILE:-/tmp/rahuul_radar_autoupdate.lock}"
INTERVENTION_FILE="$WORK_DIR/logs/auto_update_intervention_required"

# 0. Check for Prior Failed Update Requiring Manual Intervention
if [ -f "$INTERVENTION_FILE" ]; then
    echo "[$(date)] [ERROR] Manual intervention flag exists ($INTERVENTION_FILE). Refusing to auto-update until cleared." >> "$LOG_FILE"
    exit 1
fi

# 1. Process Concurrency Lock (Flock or Atomic Lockdir)
if command -v flock >/dev/null 2>&1; then
    exec 200>"$LOCK_FILE"
    if ! flock -n 200; then
        echo "[$(date)] Auto-update is already running. Exiting." >> "$LOG_FILE"
        exit 0
    fi
else
    LOCK_DIR="${LOCK_FILE}.lockdir"
    if ! mkdir "$LOCK_DIR" 2>/dev/null; then
        echo "[$(date)] Auto-update is already running (lock acquired). Exiting." >> "$LOG_FILE"
        exit 0
    fi
    trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT INT TERM
fi

echo "[$(date)] Checking for GitHub updates on branch dev..." >> "$LOG_FILE"

# 2. Verify Local Git State (Must be on 'dev' branch, never detached HEAD)
CURRENT_BRANCH=$(git symbolic-ref --short -q HEAD || echo "")
if [ "$CURRENT_BRANCH" != "dev" ]; then
    echo "[$(date)] [ERROR] Active branch is '$CURRENT_BRANCH', expected 'dev'. Refusing to auto-update." >> "$LOG_FILE"
    exit 1
fi

# 3. Virtual Environment Detection
VENV_DIR="$WORK_DIR/venv"
if [ ! -d "$VENV_DIR" ] && [ -d "$WORK_DIR/.venv" ]; then
    VENV_DIR="$WORK_DIR/.venv"
fi
VENV_PYTHON="${VENV_PYTHON:-$VENV_DIR/bin/python}"
if [ ! -x "$VENV_PYTHON" ]; then
    echo "[$(date)] [ERROR] Production Python environment not found or not executable at '$VENV_PYTHON'. Aborting." >> "$LOG_FILE"
    exit 1
fi

# 4. Fetch Remote dev and Check for Updates
git fetch origin dev >> "$LOG_FILE" 2>&1
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/dev)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo "[$(date)] System is already up to date ($LOCAL_HASH)." >> "$LOG_FILE"
    exit 0
fi

# 5. Fast-Forward Validation
TARGET_SHA="$REMOTE_HASH"
if ! git merge-base --is-ancestor "$LOCAL_HASH" "$TARGET_SHA"; then
    echo "[$(date)] [ERROR] Remote target $TARGET_SHA is not a fast-forward descendant of $LOCAL_HASH. Aborting." >> "$LOG_FILE"
    exit 1
fi

# 6. Conflict Detection (Do not clobber modified or untracked local paths)
INCOMING_FILES=$(git diff --name-only "$LOCAL_HASH" "$TARGET_SHA")
LOCAL_MODIFIED=$(git diff --name-only)
LOCAL_UNTRACKED=$(git ls-files --others --exclude-standard)

CONFLICT_FOUND=0
for f in $INCOMING_FILES; do
    if echo "$LOCAL_MODIFIED" | grep -qx "$f" || echo "$LOCAL_UNTRACKED" | grep -qx "$f"; then
        echo "[$(date)] [ERROR] Incoming update for '$f' conflicts with local modified or untracked file. Aborting." >> "$LOG_FILE"
        CONFLICT_FOUND=1
    fi
done

if [ "$CONFLICT_FOUND" -ne 0 ]; then
    echo "[$(date)] [ERROR] Refusing to update due to local file conflict. Preserving working tree." >> "$LOG_FILE"
    exit 1
fi

echo "[$(date)] New fast-forward update detected: $LOCAL_HASH -> $TARGET_SHA. Initiating update..." >> "$LOG_FILE"

# 7. Pre-Update SQLite Database Backup
BACKUP_BASE="${AUTO_UPDATE_BACKUP_DIR:-$HOME/backups_auto_update}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE/backup_$TIMESTAMP"

echo "[$(date)] Creating pre-update SQLite database backups in $BACKUP_DIR..." >> "$LOG_FILE"

set +e
BACKUP_OUTPUT=$(BACKUP_DIR="$BACKUP_DIR" "$VENV_PYTHON" - << 'PYEOF' 2>&1
import os
import sys
import sqlite3

backup_dir = os.environ.get("BACKUP_DIR")
if not backup_dir:
    sys.exit("BACKUP_DIR environment variable missing")

os.makedirs(backup_dir, mode=0o700, exist_ok=True)
os.chmod(backup_dir, 0o700)

db_targets = [
    ("data/live_journal.db", "data_live_journal.db"),
    ("data/radar.db", "data_radar.db"),
    ("radar.db", "root_radar.db"),
]

# Fail-closed preflight: every required database MUST exist and be readable
for src, _ in db_targets:
    if not os.path.exists(src):
        sys.exit(f"REQUIRED_DATABASE_MISSING:{src}")
    if not os.path.isfile(src):
        sys.exit(f"REQUIRED_DATABASE_NOT_FILE:{src}")
    if not os.access(src, os.R_OK):
        sys.exit(f"REQUIRED_DATABASE_UNREADABLE:{src}")

backed_up_count = 0
for src, dst_name in db_targets:
    dst = os.path.join(backup_dir, dst_name)
    src_conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    dst_conn = sqlite3.connect(dst)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    os.chmod(dst, 0o600)

    # Verify integrity
    v_conn = sqlite3.connect(f"file:{dst}?mode=ro", uri=True)
    cur = v_conn.cursor()
    cur.execute("PRAGMA quick_check;")
    check = cur.fetchall()
    v_conn.close()
    if check != [('ok',)]:
        sys.exit(f"Integrity check failed for {dst}: {check}")
    backed_up_count += 1

if backed_up_count != len(db_targets):
    sys.exit(f"Expected {len(db_targets)} backups, but completed {backed_up_count}")

print(f"BACKUP_SUCCESS:{backed_up_count}")
PYEOF
)
BACKUP_STATUS=$?
set -e

if [ "$BACKUP_STATUS" -ne 0 ] || ! echo "$BACKUP_OUTPUT" | grep -q "BACKUP_SUCCESS"; then
    echo "[$(date)] [ERROR] Pre-update database backup failed ($BACKUP_OUTPUT). Aborting update before git merge." >> "$LOG_FILE"
    exit 1
fi
echo "[$(date)] Database backups successfully created and verified ($BACKUP_OUTPUT)." >> "$LOG_FILE"

# 8. Perform Controlled Fast-Forward Merge
if ! git merge --ff-only "$TARGET_SHA" >> "$LOG_FILE" 2>&1; then
    echo "[$(date)] [ERROR] Git fast-forward merge failed. Preserving working tree and exiting." >> "$LOG_FILE"
    exit 1
fi
echo "[$(date)] Git fast-forward to $TARGET_SHA completed." >> "$LOG_FILE"

# 9. Optional Dependency Installation
REQ_FILE=""
if [ -f "requirements_server.txt" ]; then
    REQ_FILE="requirements_server.txt"
elif [ -f "requirements.txt" ]; then
    REQ_FILE="requirements.txt"
fi

if [ -n "$REQ_FILE" ] && echo "$INCOMING_FILES" | grep -qx "$REQ_FILE"; then
    echo "[$(date)] Requirements file '$REQ_FILE' modified in update. Installing dependencies..." >> "$LOG_FILE"
    if ! "$VENV_PYTHON" -m pip install -r "$REQ_FILE" >> "$LOG_FILE" 2>&1; then
        echo "[$(date)] [ERROR] Dependency installation failed! Manual intervention required." >> "$LOG_FILE"
        touch "$INTERVENTION_FILE"
        exit 1
    fi
fi

# 10. Service Restart
SYSTEMCTL_CMD="${SYSTEMCTL_CMD:-sudo -n systemctl}"
SERVICE_NAME="rahuul_radar.service"

echo "[$(date)] Restarting service $SERVICE_NAME..." >> "$LOG_FILE"
if ! $SYSTEMCTL_CMD restart "$SERVICE_NAME" >> "$LOG_FILE" 2>&1; then
    echo "[$(date)] [ERROR] Failed to restart $SERVICE_NAME via $SYSTEMCTL_CMD. Manual intervention required." >> "$LOG_FILE"
    touch "$INTERVENTION_FILE"
    exit 1
fi

# Verify service is active
if ! $SYSTEMCTL_CMD is-active --quiet "$SERVICE_NAME" >> "$LOG_FILE" 2>&1; then
    echo "[$(date)] [ERROR] Service $SERVICE_NAME is not active after restart. Manual intervention required." >> "$LOG_FILE"
    touch "$INTERVENTION_FILE"
    exit 1
fi

# 11. Bounded Health Check Verification
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/api/v1/health}"
HEALTH_PASSED=0

echo "[$(date)] Verifying API health on $HEALTH_URL..." >> "$LOG_FILE"
for i in {1..6}; do
    sleep 2
    HEALTH_RESP=$(curl -s -m 5 "$HEALTH_URL" || echo "")
    if echo "$HEALTH_RESP" | grep -q '"status":"online"'; then
        HEALTH_PASSED=1
        break
    fi
done

if [ "$HEALTH_PASSED" -eq 1 ]; then
    echo "[$(date)] Service $SERVICE_NAME updated to $TARGET_SHA and verified HEALTHY!" >> "$LOG_FILE"
    exit 0
else
    echo "[$(date)] [ERROR] Health check failed or timed out on $HEALTH_URL. Manual intervention required." >> "$LOG_FILE"
    touch "$INTERVENTION_FILE"
    exit 1
fi
