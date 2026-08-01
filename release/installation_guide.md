# RAHUUL_RADAR Enterprise v2.0 — Installation Guide

This document covers installation and setup across macOS, Windows, Linux, Render Cloud, and Docker container environments.

---

## System Requirements

- **Python:** 3.10+ (Recommended Python 3.11 / 3.12 / 3.14)
- **RAM:** Minimum 2 GB (4 GB recommended)
- **Disk:** 500 MB free space
- **OS:** macOS 12+, Ubuntu 20.04+, Windows 10/11

---

## 1. macOS / Linux Installation

```bash
# Clone the repository
git clone https://github.com/rthakkar50/RAHUUL_RADAR.git
cd RAHUUL_RADAR

# Create virtual environment
python3 -m venv .venv
source .venv/bin/python

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run full test suite to verify installation
PYTHONPATH=. pytest
```

---

## 2. Windows Installation (PowerShell)

```powershell
# Clone repository
git clone https://github.com/rthakkar50/RAHUUL_RADAR.git
cd RAHUUL_RADAR

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Verify test suite
$env:PYTHONPATH="."
pytest
```

---

## 3. Render Cloud VPS Deployment

1. Connect GitHub repository `rthakkar50/RAHUUL_RADAR` to Render.
2. Select **Web Service**.
3. **Environment:** Python 3
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `uvicorn rest_api:app --host 0.0.0.0 --port 10000`
6. Set Environment Variables:
   - `PAYTM_API_KEY`: `<your_key>`
   - `PAYTM_API_SECRET`: `<your_secret>`
   - `TELEGRAM_BOT_TOKEN`: `<your_token>`
   - `TELEGRAM_CHAT_ID`: `<your_chat_id>`

---

## 4. Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run container:
```bash
docker build -t rahuul-radar:v2.0 .
docker run -d -p 8000:8000 --name rahuul_radar rahuul-radar:v2.0
```
