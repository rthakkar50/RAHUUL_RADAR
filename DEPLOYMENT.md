# RAHUUL RADAR — Production Deployment Guide (v1.1)

---

## 1. Prerequisites

* **Operating System:** macOS / Ubuntu 22.04 LTS / Windows 11
* **Python Version:** 3.10+ (Tested on Python 3.14)
* **Flutter SDK:** 3.19+ (For mobile app build)
* **Database:** SQLite3 (Built-in)

---

## 2. Server Installation (FastAPI Backend)

### Step 1: Clone & Environment Setup
```bash
git clone https://github.com/RAHUUL/RAHUUL_RADAR.git
cd RAHUUL_RADAR

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration
Copy `config.json.example` to `config.json`:
```bash
cp config.json.example config.json
```

Edit `config.json` with Paytm Money API credentials:
```json
{
  "paytm_api_key": "YOUR_PAYTM_API_KEY",
  "paytm_api_secret": "YOUR_PAYTM_API_SECRET",
  "paytm_public_access_token": "YOUR_PUBLIC_JWT_TOKEN",
  "capital": 1000000.0,
  "risk_pct": 1.0,
  "daily_loss_limit": 5000.0,
  "daily_profit_target": 15000.0,
  "max_consecutive_losses": 3,
  "max_open_trades": 5,
  "max_orders_per_day": 20,
  "kill_switch_active": false,
  "auto_trading_enabled": true
}
```

### Step 3: Launch FastAPI Service
```bash
# Run backend on port 8000
.venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 3. Flutter Mobile Application Deployment

### Step 1: Configure Production Endpoint
Edit `mobile/lib/core/network/api_config.dart` or set via Mobile Settings UI:
```dart
static String localIp = 'api.rahuulradar.com';
static String port = '8000';
static String env = 'Production';
```

### Step 2: Build Android / iOS Release Package
```bash
cd mobile

# Android APK / App Bundle
flutter build apk --release

# iOS Bundle
flutter build ipa --release
```

---

## 4. Desktop PyQt5 Application Launch

```bash
source .venv/bin/activate
python main.py
```

---

## 5. Systemd Production Service Setup (Linux)

Create `/etc/systemd/system/rahuul-radar.service`:
```ini
[Unit]
Description=RAHUUL RADAR Algorithmic Trading Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/RAHUUL_RADAR
ExecStart=/home/ubuntu/RAHUUL_RADAR/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable & start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rahuul-radar
sudo systemctl start rahuul-radar
```
