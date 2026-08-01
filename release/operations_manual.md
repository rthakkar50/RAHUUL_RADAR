# RAHUUL_RADAR Enterprise v2.0 — Operations Manual

Daily, weekly, and monthly operational checklists for SRE leads and system administrators.

---

## 1. Daily Operations Checklist

- [ ] Check system health status via `GET /api/v1/health` or `ops.health_monitor`.
- [ ] Verify active alerts in `AlertManager`.
- [ ] Check Paper Trading Daily P&L and Trade Journal entries.

---

## 2. Weekly Operations Checklist

- [ ] Execute full database backup via `BackupManager`.
- [ ] Review Quant Lab performance reports and strategy rankings.
- [ ] Monitor PSI feature & prediction drift in `DriftMonitor`.

---

## 3. Monthly Maintenance

- [ ] Execute SQLite database `VACUUM` and `ANALYZE`.
- [ ] Review AI Model Registry and evaluate offline candidate models.
