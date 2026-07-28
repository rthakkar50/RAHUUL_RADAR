# RELEASE CANDIDATE 1 (RC1) — RELEASE NOTES

## System Overview
- **Application Name**: RAHUUL_RADAR
- **Version**: `v1.0.0-rc1` (Production Release Candidate 1)
- **Target Platforms**: Mobile (Flutter Android APK), Desktop (PyQt5), Remote (Telegram Bot), Backend (FastAPI REST API)
- **Release Date**: July 28, 2026

## Component Status
- **Backend Service (FastAPI / Uvicorn)**: `ONLINE 🟢` (Port 8000, `/api/v1`)
- **Mobile Client (Flutter)**: `PASSED 🟢` (`app-release.apk`)
- **Telegram Trading Intelligence**: `ONLINE 🟢` (`@RahuulRT_bot`)
- **Live Risk Engine**: `ACTIVE 🟢` (`LiveRiskEngine` + `DailyRiskTracker`)
- **Paytm Money Broker**: `READY 🟢` (`PaytmMoneyProvider` + `PaytmOrderEngine`)

## Audit & Verification Matrix
1. **Endpoint Resolution**: PASSED — 0 duplicate `/api/v1/api/v1` collisions.
2. **Configuration**: PASSED — `ApiConfig` validated with fallback IP/Port handling.
3. **Demo Data**: PASSED — 0 hardcoded ₹1000 fallbacks in Telegram or Scanner.
4. **Code Quality**: PASSED — 0 TODO/FIXME/HACK tags in production source.
5. **Release Build**: PASSED — `flutter build apk --release` compiled cleanly.
6. **Backend Test Suite**: PASSED — 59/59 Pytest unit tests passing (11.15s).

## Deployment & Installation
- **APK Path**: `mobile/build/app/outputs/flutter-apk/app-release.apk`
- **Backend Server**: `PYTHONPATH=. .venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000`
- **Telegram Bot**: `python telegram_controller.py`
