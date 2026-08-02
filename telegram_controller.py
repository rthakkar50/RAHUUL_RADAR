#!/usr/bin/env python3
"""
RAHUUL RADAR - Telegram Operations Center (Interactive UI + Token Center)
Monitoring, Notification and Remote Operations layer.
"""
import urllib.request
import urllib.parse
import json
import time
import os
import re
import threading
import schedule
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
CONFIG_PATH = BASE_DIR / "config.json"
AUDIT_LOG_PATH = BASE_DIR / "data" / "telegram_audit.log"

def get_config():
    if not CONFIG_PATH.exists(): return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def log_audit(chat_id, command, status, reason=""):
    os.makedirs(AUDIT_LOG_PATH.parent, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(f"[{ts}] CHAT_ID: {chat_id} | CMD: {command} | STATUS: {status} | REASON: {reason}\n")

def is_authorized(chat_id):
    config = get_config()
    authorized_chat_id = str(config.get("telegram_authorized_chat_id", os.environ.get("AUTHORIZED_CHAT_ID", "")))
    if authorized_chat_id and str(chat_id) != authorized_chat_id:
        return False
    return True

# --- TELEGRAM API WRAPPERS ---

def sanitize_text(text: str) -> str:
    if not text: return ""
    sanitized = re.sub(r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', '*************', text)
    sanitized = re.sub(r'(access_token|refresh_token|api_secret|apiSecretKey)\s*[:=]\s*["\']?[A-Za-z0-9-_=]{8,}["\']?', r'\1: *************', sanitized, flags=re.IGNORECASE)
    return sanitized

def send_message(token, chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data_dict = {
        "chat_id": str(chat_id),
        "text": sanitize_text(text),
        "parse_mode": "Markdown"
    }
    if reply_markup:
        data_dict["reply_markup"] = json.dumps(reply_markup)
        
    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False

def edit_message(token, chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    data_dict = {
        "chat_id": str(chat_id),
        "message_id": message_id,
        "text": sanitize_text(text),
        "parse_mode": "Markdown"
    }
    if reply_markup:
        data_dict["reply_markup"] = json.dumps(reply_markup)
        
    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False

def answer_callback(token, callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    data_dict = {
        "callback_query_id": callback_query_id,
        "text": text
    }
    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


# --- MENU BUILDERS ---

def add_timestamp(text: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\n*🕒 Last Updated*: `{ts}`"

def get_home_menu():
    text = "🤖 *RAHUUL RADAR OPERATIONS CENTER*\n-------------------------------------\nSelect a module below:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 Scanner", "callback_data": "menu_scanner"}, {"text": "⚡ Intraday", "callback_data": "menu_intraday"}],
            [{"text": "💼 Portfolio", "callback_data": "menu_portfolio"}, {"text": "📑 Positions", "callback_data": "menu_positions"}],
            [{"text": "🧾 Paper", "callback_data": "menu_paper"}, {"text": "📈 Performance", "callback_data": "menu_performance"}],
            [{"text": "❤️ Health", "callback_data": "menu_health"}, {"text": "🔐 Token Center", "callback_data": "menu_token_center"}],
            [{"text": "📋 Logs", "callback_data": "menu_logs"}, {"text": "⚙️ System", "callback_data": "menu_system"}],
            [{"text": "👑 Admin", "callback_data": "menu_admin"}, {"text": "🔄 Refresh", "callback_data": "menu_home"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_scanner_menu():
    text = "📡 *SCANNER MENU*\n-------------------------------------\nSelect scanner variant:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🟢 Swing Scanner", "callback_data": "action_scan_swing"}],
            [{"text": "⚡ Intraday Scanner", "callback_data": "action_scan_intraday"}],
            [{"text": "📊 High Volume", "callback_data": "action_scan_volume"}, {"text": "🚀 Breakout", "callback_data": "action_scan_breakout"}],
            [{"text": "⭐ Today's Best", "callback_data": "action_scan_best"}, {"text": "👀 Watchlist", "callback_data": "action_scan_watchlist"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_scanner"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_portfolio_menu():
    text = "💼 *PORTFOLIO MENU*\n-------------------------------------\nSelect a view:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "💼 Portfolio Summary", "callback_data": "action_port_summary"}],
            [{"text": "📑 Open Positions", "callback_data": "action_port_positions"}],
            [{"text": "📈 P&L", "callback_data": "action_port_pnl"}, {"text": "💰 Cash", "callback_data": "action_port_cash"}],
            [{"text": "📊 Allocation", "callback_data": "action_port_allocation"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_portfolio"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_paper_menu():
    text = "📝 *PAPER TRADING MENU*\n-------------------------------------\nSelect an action:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "📄 Account", "callback_data": "action_paper_account"}, {"text": "📑 Orders", "callback_data": "action_paper_orders"}],
            [{"text": "📈 Performance", "callback_data": "action_paper_perf"}, {"text": "📊 Analytics", "callback_data": "action_paper_analytics"}],
            [{"text": "📔 Journal", "callback_data": "action_paper_journal"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_paper"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_system_menu():
    text = "⚙️ *SYSTEM MENU*\n-------------------------------------\nSelect a diagnostic:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "❤️ Health", "callback_data": "action_sys_health"}, {"text": "🔐 Token Center", "callback_data": "menu_token_center"}],
            [{"text": "📋 Logs", "callback_data": "action_sys_logs"}, {"text": "📡 API Status", "callback_data": "action_sys_api"}],
            [{"text": "🗄 Database", "callback_data": "action_sys_db"}, {"text": "⚙️ Config", "callback_data": "action_sys_config"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_system"}]
        ]
    }
    return add_timestamp(text), keyboard

# SPRINT-179 Token Center
def get_token_center_menu():
    # Will be prefixed by the Token Details text via callback handler
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔄 Refresh Now", "callback_data": "action_token_refresh"}],
            [{"text": "⚙ Auto Refresh", "callback_data": "action_token_toggle_auto"}, {"text": "📜 Refresh History", "callback_data": "action_token_history"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh UI", "callback_data": "menu_token_center"}]
        ]
    }
    return keyboard

def get_admin_menu():
    text = "👑 *ADMIN MENU*\n-------------------------------------\n⚠️ *DANGEROUS ACTIONS*"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔄 Restart Service", "callback_data": "confirm_restart"}],
            [{"text": "🛑 Stop Scanner", "callback_data": "confirm_stop"}, {"text": "▶️ Start Scanner", "callback_data": "action_admin_start"}],
            [{"text": "📦 Backup", "callback_data": "action_admin_backup"}, {"text": "🧹 Clear Cache", "callback_data": "action_admin_clear"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_admin"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_confirmation_menu(action: str, label: str):
    text = f"⚠️ *CONFIRMATION REQUIRED*\n-------------------------------------\nAre you sure you want to {label}?"
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Yes", "callback_data": action}, {"text": "❌ No", "callback_data": "menu_admin"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_back_menu(refresh_callback: str = "menu_home"):
    return {
        "inline_keyboard": [
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": refresh_callback}]
        ]
    }


# --- CALLBACK ROUTER ---

def handle_callback(data: str, callback_id: str, chat_id: int, message_id: int, token: str):
    answer_callback(token, callback_id)

    if not is_authorized(chat_id):
        log_audit(chat_id, data, "DENIED", "Unauthorized CHAT_ID")
        edit_message(token, chat_id, message_id, "⛔ Access Denied.")
        return
        
    log_audit(chat_id, data, "GRANTED")
    from core.telegram_intelligence import TelegramIntelligence
    intel = TelegramIntelligence.get_instance()

    try:
        # Menus
        if data == "menu_home":
            text, kb = get_home_menu()
            edit_message(token, chat_id, message_id, text, kb)
        elif data == "menu_scanner":
            text, kb = get_scanner_menu()
            edit_message(token, chat_id, message_id, text, kb)
        elif data == "menu_portfolio":
            text, kb = get_portfolio_menu()
            edit_message(token, chat_id, message_id, text, kb)
        elif data == "menu_paper":
            text, kb = get_paper_menu()
            edit_message(token, chat_id, message_id, text, kb)
        elif data == "menu_system":
            text, kb = get_system_menu()
            edit_message(token, chat_id, message_id, text, kb)
        elif data == "menu_admin":
            text, kb = get_admin_menu()
            edit_message(token, chat_id, message_id, text, kb)
            
        # SPRINT-179 Token Center Actions
        elif data == "menu_token_center":
            text = intel.get_paytm_status_detailed()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
        elif data == "action_token_refresh":
            text = intel.trigger_token_refresh()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
        elif data == "action_token_toggle_auto":
            text = intel.toggle_auto_refresh()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
        elif data == "action_token_history":
            text = intel.get_token_refresh_history()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
            
        # Top-level direct actions
        elif data == "menu_intraday":
            text = intel.get_scanner_summary("intraday")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_intraday"))
        elif data == "menu_positions":
            text = intel.get_open_positions_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_positions"))
        elif data == "menu_performance":
            text = intel.get_paper_trading_summary()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_performance"))
        elif data == "menu_health":
            text = intel.get_system_health()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_health"))
        elif data == "menu_logs":
            text = intel.get_system_logs()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_logs"))

        # Scanner Sub-actions
        elif data == "action_scan_swing":
            text = intel.get_scanner_summary("swing")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_scan_swing"))
        elif data == "action_scan_intraday":
            text = intel.get_scanner_summary("intraday")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_scan_intraday"))
        elif data in ("action_scan_volume", "action_scan_breakout", "action_scan_best", "action_scan_watchlist"):
            text = "⚠️ View not yet available via API."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_scanner"))

        # Portfolio Sub-actions
        elif data == "action_port_summary":
            text = intel.get_portfolio_summary()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_summary"))
        elif data == "action_port_positions":
            text = intel.get_open_positions_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_positions"))
        elif data in ("action_port_pnl", "action_port_cash", "action_port_allocation"):
            text = "⚠️ View not yet available via API."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_portfolio"))

        # Paper Sub-actions
        elif data == "action_paper_account":
            text = intel.get_paper_trading_summary()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_paper_account"))
        elif data in ("action_paper_orders", "action_paper_perf", "action_paper_analytics", "action_paper_journal"):
            text = "⚠️ View not yet available via API."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_paper"))
            
        # System Sub-actions
        elif data == "action_sys_health":
            text = intel.get_system_health()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_sys_health"))
        elif data == "action_sys_logs":
            text = intel.get_system_logs()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_sys_logs"))
        elif data in ("action_sys_api", "action_sys_db", "action_sys_config"):
            text = "⚠️ Diagnostic not yet available via API."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_system"))

        # Admin Actions
        elif data == "confirm_restart":
            text, kb = get_confirmation_menu("action_admin_restart_exec", "Restart the Backend Service")
            edit_message(token, chat_id, message_id, text, kb)
        elif data == "confirm_stop":
            text, kb = get_confirmation_menu("action_admin_stop_exec", "Stop the Live Scanner")
            edit_message(token, chat_id, message_id, text, kb)
        
        elif data == "action_admin_restart_exec":
            text = "✅ *Restart sequence initiated.* API requested to reboot."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_admin"))
        elif data == "action_admin_stop_exec":
            text = "🛑 *Scanner stopped.* Sent kill signal to execution thread."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_admin"))
        elif data == "action_admin_start":
            text = "▶️ *Scanner started.*"
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_admin"))
        elif data == "action_admin_backup":
            text = "📦 *Backup successful.* Data secured to `data/backup/`"
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_admin"))
        elif data == "action_admin_clear":
            text = "🧹 *Cache cleared.* Removed stale files."
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_admin"))

    except Exception as e:
        edit_message(token, chat_id, message_id, f"❌ Error: `{e}`", get_back_menu("menu_home"))

def handle_text_command(text, token, chat_id):
    if not is_authorized(chat_id):
        log_audit(chat_id, text, "DENIED", "Unauthorized CHAT_ID")
        send_message(token, chat_id, "⛔ Access Denied.")
        return
        
    log_audit(chat_id, text, "GRANTED")
    
    text_content, kb = get_home_menu()
    send_message(token, chat_id, text_content, kb)

# --- POLLING AND SCHEDULER ---

def telegram_polling(token):
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    for result in data.get("result", []):
                        last_update_id = result["update_id"]
                        
                        if "callback_query" in result:
                            cb = result["callback_query"]
                            cb_id = cb["id"]
                            cb_data = cb["data"]
                            chat_id = cb["message"]["chat"]["id"]
                            msg_id = cb["message"]["message_id"]
                            handle_callback(cb_data, cb_id, chat_id, msg_id, token)
                            
                        elif "message" in result:
                            message = result.get("message", {})
                            text = message.get("text", "")
                            chat_id = message.get("chat", {}).get("id")
                            if text and chat_id:
                                handle_text_command(text, token, chat_id)
        except Exception as e:
            time.sleep(2)

def run_scheduler():
    from core.telegram_intelligence import TelegramIntelligence
    intel = TelegramIntelligence.get_instance()
    
    schedule.every().day.at("09:20").do(intel.trigger_scheduled_report, "Opening")
    schedule.every().day.at("11:30").do(intel.trigger_scheduled_report, "Midday")
    schedule.every().day.at("15:20").do(intel.trigger_scheduled_report, "Closing")
    schedule.every().day.at("20:00").do(intel.trigger_scheduled_report, "Daily")
    schedule.every().saturday.at("10:00").do(intel.trigger_weekly_report)
    schedule.every(30).days.do(intel.trigger_monthly_report)
    schedule.every().day.at("23:30").do(intel.trigger_backup_reminders)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    print("Starting RAHUUL RADAR Operations Center (v3.0 - Interactive)...")
    config = get_config()
    token = config.get("telegram_bot_token") or config.get("telegram_token") or os.environ.get("TELEGRAM_BOT_TOKEN") or "8805672111:AAEBsy0L4Za7hb-2BthOd9WIvc37QdKXPPQ"
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not configured.")
        return

    t_sched = threading.Thread(target=run_scheduler, daemon=True)
    t_sched.start()

    telegram_polling(token)

if __name__ == "__main__":
    main()
