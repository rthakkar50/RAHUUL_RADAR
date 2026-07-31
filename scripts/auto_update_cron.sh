#!/usr/bin/env bash
# Auto-Update Cron Script for RAHUUL RADAR Cloud VPS
set -e

WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORK_DIR"

echo "[$(date)] Checking for GitHub updates on branch dev..." >> "$WORK_DIR/logs/auto_update.log"

git fetch origin dev
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/dev)

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    echo "[$(date)] New update detected! Pulling latest changes..." >> "$WORK_DIR/logs/auto_update.log"
    git pull origin dev >> "$WORK_DIR/logs/auto_update.log" 2>&1
    
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        pip install -r requirements_server.txt >> "$WORK_DIR/logs/auto_update.log" 2>&1 || true
    fi

    # Restart supervisor background process if running
    pkill -f "server_supervisor.py" || true
    sleep 1
    PYTHONPATH=. .venv/bin/python scripts/server_supervisor.py >> "$WORK_DIR/logs/server_supervisor.log" 2>&1 &
    echo "[$(date)] Server & Telegram Bot successfully updated and auto-restarted!" >> "$WORK_DIR/logs/auto_update.log"
else
    echo "[$(date)] System is already up to date." >> "$WORK_DIR/logs/auto_update.log"
fi
