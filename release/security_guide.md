# RAHUUL_RADAR Enterprise v2.0 — Security Guide

Security policies, secret management, audit logging, and input validation policies.

---

## 1. Secrets Management

- **No Hardcoded Keys:** Secrets must strictly be loaded via environment variables (`PAYTM_API_KEY`, `TELEGRAM_BOT_TOKEN`).
- **Redaction Policy:** `ops/audit_center.py` automatically redacts sensitive keys in audit trails with `[REDACTED_CREDENTIAL]`.

---

## 2. Parameterized Database Queries

- 100% of SQLite database operations use prepared statements to prevent SQL injection vulnerabilities.

---

## 3. Mandatory Human Promotion Gate

- **AI Model Deployment Safety:** No offline trained AI candidate can replace the production Champion model without explicit human/CTO approval (`explicit_approval=True`).
