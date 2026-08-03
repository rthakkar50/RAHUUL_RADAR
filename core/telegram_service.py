import os
import sys
import json
import time
import re
import sqlite3
import logging
import threading
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = BASE_DIR / "config.json"
DB_PATH = DATA_DIR / "radar.db"

class TelegramService:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)

        self._init_loggers()
        self._init_db()

        self._is_running = False
        self._heartbeat_thread = None
        self._retry_thread = None

        self.last_heartbeat_status = {"api": False, "db": False, "scanner": False, "paper": False, "ts": ""}
        self._last_subsystem_states = {"api": True, "db": True, "scanner": True, "paper": True}

        self.notification_settings = {
            "scanner_alerts": True,
            "paper_alerts": True,
            "portfolio_alerts": True,
            "risk_alerts": True,
            "news_alerts": True,
            "token_alerts": True,
        }

    def _init_loggers(self):
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')

        self.logger = logging.getLogger("telegram_main")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fh = logging.FileHandler(LOGS_DIR / "telegram.log", encoding="utf-8")
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        self.error_logger = logging.getLogger("telegram_error")
        self.error_logger.setLevel(logging.ERROR)
        if not self.error_logger.handlers:
            fh = logging.FileHandler(LOGS_DIR / "telegram_error.log", encoding="utf-8")
            fh.setFormatter(formatter)
            self.error_logger.addHandler(fh)

        self.cmd_logger = logging.getLogger("telegram_commands")
        self.cmd_logger.setLevel(logging.INFO)
        if not self.cmd_logger.handlers:
            fh = logging.FileHandler(LOGS_DIR / "telegram_commands.log", encoding="utf-8")
            fh.setFormatter(formatter)
            self.cmd_logger.addHandler(fh)

        self.notif_logger = logging.getLogger("telegram_notifications")
        self.notif_logger.setLevel(logging.INFO)
        if not self.notif_logger.handlers:
            fh = logging.FileHandler(LOGS_DIR / "telegram_notifications.log", encoding="utf-8")
            fh.setFormatter(formatter)
            self.notif_logger.addHandler(fh)

    def _init_db(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS telegram_retry_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    parse_mode TEXT DEFAULT 'Markdown',
                    retries INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS telegram_command_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    exec_time_ms REAL NOT NULL,
                    success INTEGER NOT NULL,
                    exception TEXT,
                    reply_length INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS telegram_watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            self.error_logger.error(f"Failed to initialize Telegram DB tables: {e}", exc_info=True)

    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text:
            return ""
        sanitized = re.sub(r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', '*************', text)
        sanitized = re.sub(
            r'(access_token|refresh_token|api_secret|apiSecretKey|telegram_bot_token|token|password)\s*[:=]\s*["\']?[A-Za-z0-9-_=]{8,}["\']?',
            r'\1: *************',
            sanitized,
            flags=re.IGNORECASE
        )
        return sanitized

    def get_config(self) -> dict:
        if not CONFIG_PATH.exists():
            return {}
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.error_logger.error(f"Error reading config: {e}")
            return {}

    def audit_command(self, user_id: str, command: str, exec_time_ms: float, success: bool, exception: str = "", reply_len: int = 0):
        log_msg = f"USER: {user_id} | CMD: {command} | TIME: {exec_time_ms:.2f}ms | SUCCESS: {success} | REPLY_LEN: {reply_len}"
        if exception:
            log_msg += f" | ERROR: {exception}"
        self.cmd_logger.info(log_msg)

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO telegram_command_audit (user_id, command, exec_time_ms, success, exception, reply_length) VALUES (?, ?, ?, ?, ?, ?)",
                (str(user_id), command, exec_time_ms, 1 if success else 0, exception, reply_len)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.error_logger.error(f"Failed to record command audit to DB: {e}")

    def enqueue_retry_message(self, chat_id: str, message: str, parse_mode: str = "Markdown"):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO telegram_retry_queue (chat_id, message, parse_mode) VALUES (?, ?, ?)",
                (str(chat_id), self.sanitize_text(message), parse_mode)
            )
            conn.commit()
            conn.close()
            self.logger.info(f"Enqueued message for retry to CHAT_ID: {chat_id}")
        except Exception as e:
            self.error_logger.error(f"Failed to enqueue retry message: {e}")

    def send_message(self, token: str, chat_id: str, text: str, parse_mode: str = "Markdown", reply_markup: dict = None) -> bool:
        if not token or not chat_id:
            self.error_logger.error("send_message failed: Missing bot token or chat_id")
            return False

        clean_text = self.sanitize_text(text)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": str(chat_id),
            "text": clean_text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        data = urllib.parse.urlencode(payload).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    self.notif_logger.info(f"Notification sent to CHAT_ID {chat_id} (Length: {len(clean_text)})")
                    return True
        except Exception as e:
            self.error_logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            self.enqueue_retry_message(chat_id, clean_text, parse_mode)
            return False

    def send_document(self, token: str, chat_id: str, file_path: str, caption: str = "") -> bool:
        if not os.path.exists(file_path):
            self.error_logger.error(f"send_document failed: File not found at {file_path}")
            return False

        url = f"https://api.telegram.org/bot{token}/sendDocument"
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        body = []
        body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
        if caption:
            body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{self.sanitize_text(caption)}\r\n".encode("utf-8"))
        body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"document\"; filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode("utf-8"))
        body.append(file_bytes)
        body.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))

        data = b"".join(body)
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}

        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    self.notif_logger.info(f"Document {filename} sent successfully to {chat_id}")
                    return True
        except Exception as e:
            self.error_logger.error(f"Failed to send document {file_path}: {e}")
            return False

    def process_retry_queue(self, token: str):
        if not token:
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, chat_id, message, parse_mode, retries FROM telegram_retry_queue ORDER BY id ASC LIMIT 10")
            rows = c.fetchall()

            for row in rows:
                msg_id, chat_id, msg, parse_mode, retries = row
                if retries >= 5:
                    c.execute("DELETE FROM telegram_retry_queue WHERE id = ?", (msg_id,))
                    self.error_logger.warning(f"Dropped retry message {msg_id} after 5 failed attempts")
                    continue

                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": chat_id, "text": msg, "parse_mode": parse_mode}
                data = urllib.parse.urlencode(payload).encode("utf-8")

                try:
                    req = urllib.request.Request(url, data=data)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.status == 200:
                            c.execute("DELETE FROM telegram_retry_queue WHERE id = ?", (msg_id,))
                            self.logger.info(f"Successfully processed retried message {msg_id}")
                except Exception as e:
                    c.execute("UPDATE telegram_retry_queue SET retries = retries + 1 WHERE id = ?", (msg_id,))
                    self.error_logger.error(f"Retry attempt failed for message {msg_id}: {e}")

            conn.commit()
            conn.close()
        except Exception as e:
            self.error_logger.error(f"Error processing retry queue: {e}")

    def run_heartbeat_check(self, token: str = None) -> dict:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = {"api": False, "db": False, "scanner": False, "paper": False, "ts": ts}

        try:
            req = urllib.request.Request("http://127.0.0.1:8000/api/v1/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    status["api"] = True
        except Exception:
            status["api"] = False

        try:
            if os.path.exists(DB_PATH):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT 1")
                conn.close()
                status["db"] = True
        except Exception:
            status["db"] = False

        status["scanner"] = status["api"]
        status["paper"] = status["api"]

        self.last_heartbeat_status = status

        # PART 15: Notify ONLY when status changes!
        if token:
            for sys_name, cur_state in status.items():
                if sys_name == "ts":
                    continue
                prev_state = self._last_subsystem_states.get(sys_name, True)
                if cur_state != prev_state:
                    self._last_subsystem_states[sys_name] = cur_state
                    alert_msg = f"⚠️ *SYSTEM STATE CHANGE DETECTED*\n-------------------------------------\nSubsystem `{sys_name.upper()}` changed state: `{'🟢 ONLINE' if cur_state else '🔴 OFFLINE'}`"
                    config = self.get_config()
                    chat_id = config.get("telegram_authorized_chat_id")
                    if chat_id:
                        self.send_message(token, chat_id, alert_msg)

        self.logger.info(f"Heartbeat Check [{ts}] -> API: {status['api']} | DB: {status['db']} | Scanner: {status['scanner']} | Paper: {status['paper']}")
        return status

    def start_background_tasks(self, token: str):
        if self._is_running:
            return
        self._is_running = True

        def _heartbeat_loop():
            while self._is_running:
                self.run_heartbeat_check(token)
                self.process_retry_queue(token)
                time.sleep(60)

        self._heartbeat_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        self.logger.info("Enterprise Telegram Service background threads started successfully.")

    def stop_background_tasks(self):
        self._is_running = False
        self.logger.info("Enterprise Telegram Service stopping background threads.")
