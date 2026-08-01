# RAHUUL_RADAR Enterprise v2.0 — Deployment Guide

This guide details continuous 24x7 cloud deployment procedures on Render Cloud.

---

## 1. Render Cloud VPS Setup

- **Repository:** `https://github.com/rthakkar50/RAHUUL_RADAR.git`
- **Branch:** `main` (Production Gold Master)
- **Environment:** Python 3.11 / 3.14
- **Instance Type:** Starter / Standard Web Service

---

## 2. Environment Variables Checklist

- [x] `PAYTM_API_KEY`: Paytm Money API Key
- [x] `PAYTM_API_SECRET`: Paytm Money Secret
- [x] `TELEGRAM_BOT_TOKEN`: Telegram Bot Token
- [x] `TELEGRAM_CHAT_ID`: Admin Telegram Chat ID
- [x] `ENVIRONMENT`: `production`

---

## 3. Health Checks & Monitoring

- **Health Check Path:** `/api/v1/health`
- **Success HTTP Code:** `200 OK`
- **Auto-restart Policy:** Render automatically restarts instances upon unhandled crashes.
