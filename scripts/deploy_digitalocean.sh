#!/usr/bin/env bash
set -e

echo "=================================================="
echo " RAHUUL RADAR — Universal Cloud VPS 24x7 Deployment"
echo " (Oracle Cloud / DigitalOcean / AWS / Linux)"
echo "=================================================="

SUDO=""
if sudo -n true 2>/dev/null || sudo true 2>/dev/null; then
    SUDO="sudo"
fi

# Update system & dependencies
echo "[1/4] Checking Linux environment & dependencies..."
if [ -n "$SUDO" ]; then
    if command -v apt-get >/dev/null 2>&1; then
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3 python3-venv python3-pip git curl || true
    elif command -v dnf >/dev/null 2>&1; then
        $SUDO dnf install -y python3 python3-pip git curl || true
    elif command -v yum >/dev/null 2>&1; then
        $SUDO yum install -y python3 python3-pip git curl || true
    fi
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

# Register 24/7 background process
WORK_DIR=$(pwd)
CURRENT_USER=$(whoami)

HAS_SYSTEMD=false
if [ -n "$SUDO" ] && command -v systemctl >/dev/null 2>&1 && [ -d "/etc/systemd/system" ]; then
    HAS_SYSTEMD=true
fi

if [ "$HAS_SYSTEMD" = true ]; then
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
    echo "[3/4] Launching 24x7 Background Supervisor Engine (Oracle Cloud Shell Mode)..."
    pkill -f "server_supervisor.py" 2>/dev/null || true
    pkill -f "telegram_controller.py" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    sleep 1
    PYTHONPATH=. .venv/bin/python scripts/server_supervisor.py > logs/server_supervisor.log 2>&1 &
    sleep 3
fi

# Setup Automatic 15-Minute Auto-Update Cron Job
if [ -f "scripts/auto_update_cron.sh" ]; then
    chmod +x scripts/auto_update_cron.sh
    (crontab -l 2>/dev/null | grep -v "auto_update_cron.sh" ; echo "*/15 * * * * $WORK_DIR/scripts/auto_update_cron.sh") | crontab - || true
    echo "[+] Automated 15-minute GitHub Auto-Sync enabled in Crontab!"
fi

echo "=================================================="
echo " ✅ CLOUD DEPLOYMENT SUCCESSFUL!"
echo " RAHUUL RADAR Server & Telegram Bot are now running 24/7!"
echo " Status Check: ps aux | grep python"
echo " Health Check: curl http://localhost:8000/api/v1/health"
echo "=================================================="
