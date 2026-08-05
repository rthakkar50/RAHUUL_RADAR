#!/usr/bin/env bash
set -eo pipefail

echo "====================================================="
echo "  RAHUUL_RADAR ENTERPRISE VPS AUTOMATED DEPLOYMENT"
echo "====================================================="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/deploy_$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

if [ -f "data/live_journal.db" ]; then
    echo "[DEPLOY] Creating pre-deployment SQLite backup..."
    cp "data/live_journal.db" "$BACKUP_DIR/live_journal.db"
fi

echo "[DEPLOY] Pulling latest production commit from Git..."
git pull origin main

echo "[DEPLOY] Building and starting updated Docker containers..."
docker compose up --build -d

echo "[DEPLOY] Waiting for backend service health check verification..."
sleep 5

HEALTH_STATUS=$(curl -s http://127.0.0.1:8000/api/v1/health | grep -o '"status":"online"' || true)

if [ -n "$HEALTH_STATUS" ]; then
    echo "====================================================="
    echo "  DEPLOYMENT SUCCESSFUL! API IS HEALTHY AND ONLINE."
    echo "====================================================="
    exit 0
else
    echo "====================================================="
    echo "❌ HEALTH CHECK FAILED! TRIGGERING AUTOMATIC ROLLBACK..."
    echo "====================================================="
    bash scripts/rollback.sh "$BACKUP_DIR"
    exit 1
fi
