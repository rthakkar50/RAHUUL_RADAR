#!/usr/bin/env python3
"""
RAHUUL RADAR - Enterprise Telegram Operations Center (v6.9.0)
24x7 Interactive Bot with Heartbeat, Persistent Retry Queue, Command Audit, & Export Engine.
"""
import os
import sys
import json
import time
import re
import threading
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from core.telegram_service import TelegramService
from core.telegram_intelligence import TelegramIntelligence

service = TelegramService.get_instance()
intel = TelegramIntelligence.get_instance()

def get_config():
    return service.get_config()

def is_authorized(chat_id):
    config = get_config()
    authorized_chat_id = str(config.get("telegram_authorized_chat_id", os.environ.get("AUTHORIZED_CHAT_ID", "")))
    if authorized_chat_id and str(chat_id) != authorized_chat_id:
        return False
    return True

def send_message(token, chat_id, text, reply_markup=None):
    return service.send_message(token, chat_id, text, reply_markup=reply_markup)

def edit_message(token, chat_id, message_id, text, reply_markup=None):
    clean_text = service.sanitize_text(text)
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    data_dict = {
        "chat_id": str(chat_id),
        "message_id": message_id,
        "text": clean_text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        data_dict["reply_markup"] = json.dumps(reply_markup)

    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        service.error_logger.error(f"edit_message failed: {e}")
        return False

def answer_callback(token, callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    data_dict = {"callback_query_id": callback_query_id, "text": text}
    data = urllib.parse.urlencode(data_dict).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

import urllib.request
import urllib.parse

def add_timestamp(text: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\n*🕒 Last Updated*: `{ts}`"

def get_home_menu():
    text = "🤖 *RAHUUL RADAR OPERATIONS CENTER (v6.9.0)*\n-------------------------------------\nSelect a module below:"
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
            [{"text": "🛡️ Risk Center", "callback_data": "action_port_risk"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_portfolio"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_paper_menu():
    text = "📝 *PAPER TRADING MENU*\n-------------------------------------\nSelect an action:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "📄 Account Summary", "callback_data": "action_paper_account"}, {"text": "📑 Open Trades", "callback_data": "action_paper_orders"}],
            [{"text": "📈 Performance", "callback_data": "action_paper_perf"}, {"text": "📔 Journal", "callback_data": "action_paper_journal"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_paper"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_token_center_menu():
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔄 Refresh Now", "callback_data": "action_token_refresh"}],
            [{"text": "⚙ Auto Refresh", "callback_data": "action_token_toggle_auto"}, {"text": "📜 Refresh History", "callback_data": "action_token_history"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh UI", "callback_data": "menu_token_center"}]
        ]
    }
    return keyboard

def get_back_menu(refresh_callback: str = "menu_home"):
    return {
        "inline_keyboard": [
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": refresh_callback}]
        ]
    }

def handle_callback(data: str, callback_id: str, chat_id: int, message_id: int, token: str):
    start_t = time.time()
    answer_callback(token, callback_id)

    if not is_authorized(chat_id):
        service.audit_command(str(chat_id), data, (time.time() - start_t) * 1000, False, "Unauthorized")
        edit_message(token, chat_id, message_id, "⛔ Access Denied.")
        return

    try:
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
        elif data == "action_scan_swing":
            text = intel.get_scanner_summary("swing")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_scan_swing"))
        elif data == "action_scan_intraday":
            text = intel.get_scanner_summary("intraday")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_scan_intraday"))
        elif data == "action_port_summary":
            text = intel.get_portfolio_summary()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_summary"))
        elif data == "action_port_positions":
            text = intel.get_open_positions_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_positions"))
        elif data == "action_port_risk":
            text = intel.get_risk_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_risk"))
        elif data == "action_paper_account":
            text = intel.get_paper_trading_summary()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_paper_account"))
        elif data == "action_paper_orders":
            text = intel.get_open_positions_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_paper_orders"))
        elif data == "action_paper_perf":
            text = intel.get_performance_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_paper_perf"))
        elif data == "action_paper_journal":
            text = intel.get_journal_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_paper_journal"))
        elif data == "menu_health":
            text = intel.get_system_health()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_health"))
        else:
            text, kb = get_home_menu()
            edit_message(token, chat_id, message_id, text, kb)

        service.audit_command(str(chat_id), data, (time.time() - start_t) * 1000, True, "", 0)
    except Exception as e:
        service.audit_command(str(chat_id), data, (time.time() - start_t) * 1000, False, str(e), 0)
        edit_message(token, chat_id, message_id, f"❌ Error: `{e}`", get_back_menu("menu_home"))

def handle_text_command(text, token, chat_id):
    start_t = time.time()
    if not is_authorized(chat_id):
        service.audit_command(str(chat_id), text, (time.time() - start_t) * 1000, False, "Unauthorized")
        send_message(token, chat_id, "⛔ Access Denied.")
        return

    parts = text.strip().split()
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""

    try:
        reply = ""
        if cmd == "/menu":
            txt, kb = get_home_menu()
            send_message(token, chat_id, txt, reply_markup=kb)
            service.audit_command(str(chat_id), cmd, (time.time() - start_t) * 1000, True, "", len(txt))
            return
        elif cmd in ("/dashboard", "/status", "/health"):
            reply = intel.get_system_health()
        elif cmd == "/diag":
            reply = intel.get_diagnostics_report()
        elif cmd == "/ping":
            reply = intel.get_ping_report()
        elif cmd == "/help":
            reply = intel.get_help_manual()
        elif cmd == "/settings":
            reply = intel.get_settings_summary()
        elif cmd == "/token":
            reply = intel.get_paytm_status_detailed()
        elif cmd == "/token_refresh":
            reply = intel.trigger_token_refresh()
        elif cmd == "/token_history":
            reply = intel.get_token_refresh_history()
        elif cmd == "/token_auto":
            reply = intel.toggle_auto_refresh()
        elif cmd in ("/scanner", "/swing"):
            reply = intel.get_scanner_summary("swing")
        elif cmd == "/intraday":
            reply = intel.get_scanner_summary("intraday")
        elif cmd == "/fno":
            reply = intel.get_scanner_summary("swing")
        elif cmd == "/top":
            reply = intel.get_scanner_summary("swing")
        elif cmd == "/market":
            reply = intel.get_market_status()
        elif cmd == "/news":
            reply = intel.get_market_news()
        elif cmd == "/copilot":
            reply = intel.get_copilot_analysis(arg if arg else "RELIANCE")
        elif cmd == "/portfolio":
            reply = intel.get_portfolio_summary()
        elif cmd == "/paper":
            reply = intel.get_paper_trading_summary()
        elif cmd == "/open":
            reply = intel.get_open_positions_report()
        elif cmd == "/closed":
            reply = intel.get_closed_positions_report()
        elif cmd == "/performance":
            reply = intel.get_performance_report()
        elif cmd == "/journal":
            reply = intel.get_journal_report()
        elif cmd == "/risk":
            reply = intel.get_risk_report()
        elif cmd in ("/watchlist", "/favorites"):
            reply = intel.get_watchlist_report()
        elif cmd == "/export":
            fmt = arg.lower() if arg else "csv"
            export_path = intel.generate_export_file(fmt, "portfolio")
            if export_path:
                service.send_document(token, chat_id, export_path, caption=f"📊 RAHUUL RADAR Portfolio Export ({fmt.upper()})")
                reply = f"✅ Export generated successfully: `{os.path.basename(export_path)}`"
            else:
                reply = "❌ Failed to generate export file."
        elif cmd == "/morning_report":
            reply = intel.generate_morning_report()
        else:
            txt, kb = get_home_menu()
            send_message(token, chat_id, txt, reply_markup=kb)
            service.audit_command(str(chat_id), cmd, (time.time() - start_t) * 1000, True, "", len(txt))
            return

        send_message(token, chat_id, reply)
        service.audit_command(str(chat_id), cmd, (time.time() - start_t) * 1000, True, "", len(reply))
    except Exception as e:
        service.audit_command(str(chat_id), cmd, (time.time() - start_t) * 1000, False, str(e), 0)
        send_message(token, chat_id, f"❌ Command execution error: `{e}`")

def telegram_polling(token):
    last_update_id = 0
    backoff = 1
    service.start_background_tasks(token)

    while True:
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    backoff = 1
                    for result in data.get("result", []):
                        last_update_id = result["update_id"]

                        if "callback_query" in result:
                            cb = result["callback_query"]
                            handle_callback(cb["data"], cb["id"], cb["message"]["chat"]["id"], cb["message"]["message_id"], token)
                        elif "message" in result:
                            message = result.get("message", {})
                            text = message.get("text", "")
                            chat_id = message.get("chat", {}).get("id")
                            if text and chat_id:
                                handle_text_command(text, token, chat_id)
        except Exception as e:
            service.error_logger.error(f"Telegram polling disconnect/error: {e}. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)

def main():
    print("Starting RAHUUL RADAR Enterprise Telegram Platform (v6.9.0 - 24x7 Certified)...")
    config = service.get_config()
    token = config.get("telegram_bot_token") or config.get("telegram_token") or os.environ.get("TELEGRAM_BOT_TOKEN") or "8805672111:AAEBsy0L4Za7hb-2BthOd9WIvc37QdKXPPQ"

    telegram_polling(token)

if __name__ == "__main__":
    main()
