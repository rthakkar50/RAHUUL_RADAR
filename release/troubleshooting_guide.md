# RAHUUL_RADAR Enterprise v2.0 — Troubleshooting Guide

Common operational issues, diagnostic steps, and recovery procedures.

---

## 1. PySide6 / Display Environment Warning

- **Symptom:** `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"` in headless server environments.
- **Resolution:** RAHUUL_RADAR includes an automated headless fallback mode (`core/master_window.py`). The system operates seamlessly in CLI/API mode without Qt GUI displays on Linux/Render.

---

## 2. High Memory / CPU Usage Alert

- **Symptom:** `AlertManager` triggers `High Memory Usage` alert.
- **Resolution:** Re-run SQLite `VACUUM` and clear in-memory option chain cache if memory exceeds 85%.

---

## 3. Database Lock Timeout

- **Symptom:** `sqlite3.OperationalError: database is locked`.
- **Resolution:** SQLite WAL (Write-Ahead Logging) mode is enabled by default. All transactions release locks using `try...finally` blocks.
