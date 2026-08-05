#!/usr/bin/env python3
import os
import sys
import shutil
import sqlite3
import time
from datetime import datetime

BACKUP_ROOT = "backups"
DB_BACKUP_DIR = os.path.join(BACKUP_ROOT, "db")
CONFIG_BACKUP_DIR = os.path.join(BACKUP_ROOT, "config")
PRIMARY_DB = "data/live_journal.db"

def init_backup_dirs():
    os.makedirs(DB_BACKUP_DIR, exist_ok=True)
    os.makedirs(CONFIG_BACKUP_DIR, exist_ok=True)

def validate_db_integrity(db_path: str) -> bool:
    """Performs SQLite PRAGMA quick_check to verify database structural integrity."""
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist.")
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA quick_check;")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == "ok":
            print(f"✓ Database integrity check PASSED for: {db_path}")
            return True
        else:
            print(f"❌ Database integrity check FAILED: {result}")
            return False
    except Exception as e:
        print(f"❌ SQLite integrity check exception: {e}")
        return False

def create_backup():
    init_backup_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if os.path.exists(PRIMARY_DB):
        if validate_db_integrity(PRIMARY_DB):
            target_db = os.path.join(DB_BACKUP_DIR, f"journal_{timestamp}.db")
            shutil.copy2(PRIMARY_DB, target_db)
            print(f"✓ SQLite database backed up to: {target_db}")
        else:
            print("❌ Skipping DB backup due to integrity check failure!")

    # Backup production configurations
    for cfg in [".env.production", "config.json"]:
        if os.path.exists(cfg):
            target_cfg = os.path.join(CONFIG_BACKUP_DIR, f"{cfg}_{timestamp}")
            shutil.copy2(cfg, target_cfg)
            print(f"✓ Configuration backed up to: {target_cfg}")

def enforce_retention_policy(max_db_backups=30):
    """Enforces 30-day snapshot retention policy on backup directories."""
    init_backup_dirs()
    db_files = sorted(
        [os.path.join(DB_BACKUP_DIR, f) for f in os.listdir(DB_BACKUP_DIR) if f.endswith(".db")],
        key=os.path.getmtime
    )
    while len(db_files) > max_db_backups:
        to_delete = db_files.pop(0)
        try:
            os.remove(to_delete)
            print(f"✓ Purged old backup file per retention policy: {to_delete}")
        except Exception as e:
            print(f"❌ Error deleting old backup: {e}")

if __name__ == "__main__":
    print("=====================================================")
    print("  RAHUUL_RADAR ENTERPRISE BACKUP MANAGER")
    print("=====================================================")
    create_backup()
    enforce_retention_policy()
    print("=====================================================")
