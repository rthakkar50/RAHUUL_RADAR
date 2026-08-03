import time
import subprocess
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

tg_process = None

def ensure_background_services():
    global tg_process
    try:
        # Check Telegram Controller Bot without relying on pgrep
        if tg_process is None or tg_process.poll() is not None:
            logging.info("Starting Telegram 24x7 Controller Bot...")
            env = os.environ.copy()
            env["PYTHONPATH"] = "."
            tg_process = subprocess.Popen([sys.executable, "telegram_controller.py"], env=env)
    except Exception as e:
        logging.error(f"Supervisor background services error: {e}")

def run_supervisor():
    port = os.environ.get("PORT", "8000")
    cmd = [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", str(port)]
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    
    while True:
        try:
            ensure_background_services()
            logging.info(f"Starting Mobile API Uvicorn Server on 0.0.0.0:{port}...")
            proc = subprocess.Popen(cmd, env=env)
            proc.wait()
            logging.warning("API Server process exited unexpectedly! Auto-restarting in 2 seconds...")
            time.sleep(2)
        except KeyboardInterrupt:
            logging.info("Supervisor stopped manually.")
            break
        except Exception as e:
            logging.error(f"Supervisor error: {e}. Retrying in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    run_supervisor()
