# RAHUUL_RADAR Enterprise v2.0 — Administrator Guide

This guide details configuration, environment variables, database management, logging, monitoring, backup, and disaster recovery procedures.

---

## 1. Environment Configuration

Configuration variables managed via `.env` or system environment:

| Variable | Description | Required | Default / Fallback |
|---|---|---|---|
| `PAYTM_API_KEY` | Paytm Money API Key | Optional | Mock Gateway Fallback |
| `PAYTM_API_SECRET` | Paytm Money Secret | Optional | Mock Gateway Fallback |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | Optional | Plain-text Console Fallback |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | Optional | Console Output |
| `PORT` | Web Service Listener Port | Optional | `10000` / `8000` |
| `ENVIRONMENT` | Environment Mode | Optional | `production` |

---

## 2. Databases & Storage Locations

- `data/radar.db`: Master SQLite database for trades, signals, and live state.
- `data/paper_trading.db`: Paper Trading database (orders, positions, journal, validation results).
- `data/order_audit_log.db`: Immutable SRE order audit trail.
- `data/models/registry.json`: MLOps Model Registry tracking versions, checksums, and rollback lineage.
- `logs/`: Application, system, and SRE audit logs.
- `data/backups/`: Automated backup archives.

---

## 3. Database Maintenance & Vacuuming

```bash
# Optimize and reclaim disk space on SQLite databases
sqlite3 data/paper_trading.db "VACUUM; ANALYZE;"
sqlite3 data/radar.db "VACUUM; ANALYZE;"
```

---

## 4. SRE Monitoring & Health Commands

Run python diagnostic commands directly from the SRE suite:
```bash
# System Health Check
PYTHONPATH=. python3 -c "from ops.health_monitor import SystemHealthMonitor; print(SystemHealthMonitor().check_system_health())"

# System Diagnostics
PYTHONPATH=. python3 -c "from ops.system_diagnostics import SystemDiagnostics; print(SystemDiagnostics().generate_full_diagnostics())"
```
