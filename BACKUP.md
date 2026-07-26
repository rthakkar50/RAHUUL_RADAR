# RAHUUL RADAR PRO - BACKUP STRATEGY & DATA PRESERVATION GUIDE

## 1. Overview
Ensuring high durability and rapid catastrophe recovery for RAHUUL RADAR PRO Version `1.0.0` requires strict schedules for configuration preservation, SQLite relational database snapshots, trading journal annotation archiving, and automated log rotation.

---

## 2. Configuration Backup

### 2.1 Target Assets
- `config.json` (Primary engine parameterization, watchlist definitions, broker API keys)
- `ui_settings.json` (PySide6 layout geometry, dark mode state, window preferences)
- `config.json.example` (Reference factory baseline)

### 2.2 Backup Procedure & Frequency
- **Frequency**: Triggered automatically upon any structural modification to settings via the GUI Settings dialog, or scheduled daily during post-market hours (17:00 IST).
- **Storage Location**: Local external backup directory (`/opt/rahuul_radar_backups/config/` or system cloud vault).
- **Execution Script Example**:
  ```bash
  mkdir -p backups/config/$(date +%F)
  cp -a config.json ui_settings.json backups/config/$(date +%F)/
  ```

---

## 3. Database Backup Strategy

### 3.1 Target Data Stores
All core operational engines write atomically to localized SQLite database files:
- `radar.db` (Historical scanner snapshots and multi-timeframe scoring records)
- `paper_trading.db` (Open and closed paper trading simulation portfolio positions)
- `trade_forensics.db` (AI decision engine rationale logs and walk-forward validation history)

### 3.2 Safe Backup Execution (Online SQLite Backup)
- **Rule**: NEVER perform raw OS filesystem file copying while active background scanner writes are underway to avoid corrupting SQLite database header locks.
- **Procedure**: Execute safe SQLite backup API dumps or enforce a graceful read-lock snapshot during offline market hours (e.g., midnight IST).
- **Backup Command Example**:
  ```bash
  for db in radar.db paper_trading.db trade_forensics.db; do
    if [ -f "$db" ]; then
      sqlite3 "$db" ".backup 'backups/db/${db}_$(date +%F).sqlite'"
    fi
  done
  ```

---

## 4. Trading Journal & Annotation Backup

### 4.1 Annotation Integrity
User-entered trade journal notes, exit reasons, and manual performance annotations represent high-value analytical intellectual property and are preserved independently from automated scanner databases.
- **Export Backup Protocol**: Automatically export trading journal records to standard open formats (`CSV` and `JSON`) weekly into the `/exports/` directory.
- **Archiving**: Zip and encrypt weekly journal exports to prevent accidental data modification or data loss during minor patch upgrades.

---

## 5. Log Rotation & Retention Policy

### 5.1 Production Logging Management
Production operations generate detailed diagnostic output inside `/logs/` and root `output.log`. While all sensitive access tokens and personal API credentials are automatically stripped and sanitized in v1.0.0, excessive log growth can saturate available disk space.
- **Max File Size**: Cap individual log file sizes at **10 MB** via standard Python `RotatingFileHandler`.
- **Backup Count (Rotations)**: Maintain a maximum of **5 archived backup log volumes** (`output.log.1`, `output.log.2`, ..., `output.log.5`).
- **Retention Period**: Automatically purge log files older than **30 days**.
- **Systemd / Logrotate Custom Configuration**:
  ```text
  /path/to/RAHUUL_RADAR/logs/*.log {
      daily
      rotate 14
      compress
      delaycompress
      missingok
      notifempty
      copytruncate
  }
  ```
