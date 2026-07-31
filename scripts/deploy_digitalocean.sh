#!/usr/bin/env bash
set -e

echo "=================================================="
echo " RAHUUL RADAR — DigitalOcean VPS 24x7 Deployment"
echo "=================================================="

# Update system & dependencies
echo "[1/4] Updating Linux packages & dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip git curl

# Setup virtual environment
echo "[2/4] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Ensure data directory exists
mkdir -p data logs

# Create systemd supervisor service for 24/7 uptime
WORK_DIR=$(pwd)
echo "[3/4] Registering 24x7 Systemd Production Service in $WORK_DIR..."

sudo bash -c "cat << EOF > /etc/systemd/system/rahuul-radar.service
[Unit]
Description=RAHUUL RADAR 24x7 Algorithmic Trading Server & Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=$WORK_DIR
ExecStart=$WORK_DIR/.venv/bin/python scripts/server_supervisor.py
Restart=always
RestartSec=3
Environment=PYTHONPATH=$WORK_DIR

[Install]
WantedBy=multi-user.target
EOF"

# Reload & start systemd service
echo "[4/4] Starting 24x7 Systemd Daemon Service..."
sudo systemctl daemon-reload
sudo systemctl enable rahuul-radar
sudo systemctl restart rahuul-radar

echo "=================================================="
echo " ✅ DIGITALOCEAN DEPLOYMENT SUCCESSFUL!"
echo " RAHUUL RADAR Server & Telegram Bot are now running 24/7!"
echo " Status Check: systemctl status rahuul-radar"
echo " Health Check: curl http://localhost:8000/api/v1/health"
echo "=================================================="
