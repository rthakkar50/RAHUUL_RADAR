# RAHUUL_RADAR Enterprise v2.0 — Backup & Restore Guide

Automated backup and disaster recovery procedures.

---

## 1. Backup Schedule & Strategy

- **Frequency:** Automated daily snapshot + pre-deployment backup.
- **Artifacts Included:**
  - `data/paper_trading.db`
  - `data/radar.db`
  - `data/order_audit_log.db`
  - `data/models/registry.json`
  - `config.json`

---

## 2. Triggering Manual Backup

```bash
PYTHONPATH=. python3 -c "from ops.backup_manager import BackupManager; b = BackupManager().create_full_backup(); print('Backup Created:', b)"
```

---

## 3. Disaster Recovery Restore Procedure

```bash
# Verify and execute restore from latest backup
PYTHONPATH=. python3 -c "from ops.backup_manager import BackupManager; from ops.restore_manager import RestoreManager; b = BackupManager().create_full_backup(); r = RestoreManager().verify_and_restore(b); print('Restore Status:', r)"
```
