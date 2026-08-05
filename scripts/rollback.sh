#!/usr/bin/env bash
set -eo pipefail

BACKUP_DIR="${1:-backups/latest}"

echo "====================================================="
echo "  RAHUUL_RADAR ENTERPRISE AUTOMATED ROLLBACK"
echo "====================================================="

echo "[ROLLBACK] Reverting git repository to previous release tag..."
git checkout HEAD~1

if [ -f "$BACKUP_DIR/live_journal.db" ]; then
    echo "[ROLLBACK] Restoring SQLite database snapshot from $BACKUP_DIR..."
    cp "$BACKUP_DIR/live_journal.db" "data/live_journal.db"
fi

echo "[ROLLBACK] Re-building and restarting stable Docker containers..."
docker compose up --build -d

echo "====================================================="
echo "  ROLLBACK COMPLETED! STABLE APPLICATION RESTORED."
echo "====================================================="
