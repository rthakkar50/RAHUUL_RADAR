#!/usr/bin/env bash
set -e

echo "=================================================="
echo " RAHUUL RADAR — Universal Cloud VPS 24x7 Deployment"
echo " (Oracle Cloud / DigitalOcean / AWS / Linux)"
echo "=================================================="

SUDO=""
if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
fi

# Update system & dependencies
echo "[1/4] Updating Linux packages & dependencies..."
if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update -y
    $SUDO apt-get install -y python3 python3-venv python3-pip git curl || true
elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y python3 python3-pip git curl || true
elif command -v yum >/dev/null 2>&1; then
    $SUDO yum install -y python3 python3-pip git curl || true
fi

# Setup virtual environment
echo "[2/4] Setting up Python virtual environment & dependencies..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv || true
fi

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

pip install --upgrade pip || true

if [ -f "requirements_server.txt" ]; then
    echo "Installing production server dependencies from requirements_server.txt..."
    pip install -r requirements_server.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || true
fi

# Ensure data directory exists
mkdir -p data logs

# Create systemd supervisor service for 24/7 uptime if systemd is supported
WORK_DIR=$(pwd)
CURRENT_USER=$(whoami)

if command -v systemctl >/dev/null 2>&1 && [ -d "/etc/systemd/system" ]; then
    echo "[3/4] Registering 24x7 Systemd Production Service in $WORK_DIR..."
    $SUDO bash -c "cat << EOF > /etc/systemd/system/rahuul-radar.service
[Unit]
Description=RAHUUL RADAR 24x7 Algorithmic Trading Server & Telegram Bot
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$WORK_DIR
ExecStart=$WORK_DIR/.venv/bin/python scripts/server_supervisor.py
Restart=always
RestartSec=3
Environment=PYTHONPATH=$WORK_DIR

[Install]
WantedBy=multi-user.target
EOF"

    echo "[4/4] Starting 24x7 Systemd Daemon Service..."
    $SUDO systemctl daemon-reload
    $SUDO systemctl enable rahuul-radar
    $SUDO systemctl restart rahuul-radar
else
    echo "[3/4] Background Daemon Launch (Non-systemd / Cloud Shell environment)..."
    nohup .venv/bin/python scripts/server_supervisor.py > logs/server_supervisor.log 2>&1 &
fi

echo "=================================================="
echo " ✅ CLOUD DEPLOYMENT SUCCESSFUL!"
echo " RAHUUL RADAR Server & Telegram Bot are now running 24/7!"
echo " Health Check: curl http://localhost:8000/api/v1/health"
echo "=================================================="
