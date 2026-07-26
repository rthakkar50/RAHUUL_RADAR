# RAHUUL RADAR PRO - INSTALLATION GUIDE (v1.0.0)

## 1. System Requirements
- **Operating System**: macOS, Windows 10/11, or Linux (x64 / ARM64).
- **Python**: Version 3.10 to 3.14.
- **Memory**: Minimum 4GB RAM (8GB+ recommended for live 24x7 scanning).
- **Disk Space**: 500MB free disk space for cache and database logging.

## 2. Source Code Installation & Virtual Environment Setup
1. **Clone or Extract Repository**:
   ```bash
   cd /path/to/RAHUUL_RADAR
   ```
2. **Create Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## 3. Configuration & Initialization
1. Ensure `config.json` and `ui_settings.json` are present in the application root.
2. Verify API Keys and market provider settings inside `config.json`.
3. Local database tables (`radar.db`, `paper_trading.db`, `trade_forensics.db`) and directories (`/logs`, `/exports`, `/config`) will be automatically checked and generated upon first launch.

## 4. Launching Application
- **GUI Application**:
  ```bash
  python3 main.py
  ```
- **Background Engine / Service**:
  Ensure systemd service (`rahuul-radar.service`) or local orchestrator script is active for 24x7 Telegram alerting and automated market monitoring.

## 5. Troubleshooting & Security Note
- Ensure write permissions to `/logs` and `/exports` are granted.
- Production log files are completely sanitized and strip out sensitive access tokens or credentials automatically.
