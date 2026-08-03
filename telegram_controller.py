#!/usr/bin/env python3
"""
RAHUUL RADAR - Enterprise Telegram Command Center (v7.0.0)
Complete Remote Control Platform for Scanner, Paper Trading, Portfolio, & Admin Operations.
"""
import os
import sys
import json
import time
import re
import threading
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    import schedule
except ImportError:
    schedule = None

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

def add_timestamp(text: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\n*🕒 Last Updated*: `{ts}`"

def get_home_menu():
    text = "🚀 *RAHUUL RADAR ENTERPRISE COMMAND CENTER (v7.0.0)*\n-------------------------------------\nSelect a module below:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🚀 Dashboard", "callback_data": "menu_dashboard"}, {"text": "📊 Scanner", "callback_data": "menu_scanner"}],
            [{"text": "💼 Portfolio", "callback_data": "menu_portfolio"}, {"text": "📑 Positions", "callback_data": "menu_positions"}],
            [{"text": "🧾 Paper Control", "callback_data": "menu_paper"}, {"text": "🛡️ Risk Center", "callback_data": "action_port_risk"}],
            [{"text": "❤️ Health", "callback_data": "menu_health"}, {"text": "🔐 Token Center", "callback_data": "menu_token_center"}],
            [{"text": "🔔 Notifications", "callback_data": "menu_notifications"}, {"text": "👑 Admin", "callback_data": "menu_admin"}],
            [{"text": "🔄 Refresh UI", "callback_data": "menu_home"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_scanner_menu():
    text = "📡 *SCANNER COMMAND MENU*\n-------------------------------------\nSelect scanner variant:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "🟢 Swing Scanner", "callback_data": "action_scan_swing"}, {"text": "⚡ Intraday Scanner", "callback_data": "action_scan_intraday"}],
            [{"text": "📊 High Volume", "callback_data": "action_scan_volume"}, {"text": "🚀 Breakout", "callback_data": "action_scan_breakout"}],
            [{"text": "⭐ Today's Best", "callback_data": "action_scan_best"}, {"text": "👀 Watchlist", "callback_data": "action_scan_watchlist"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_scanner"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_portfolio_menu():
    text = "💼 *PORTFOLIO & RISK COMMAND MENU*\n-------------------------------------\nSelect a view:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "💼 Portfolio Summary", "callback_data": "action_port_summary"}],
            [{"text": "📑 Open Positions", "callback_data": "action_port_positions"}],
            [{"text": "🛡️ Risk Center", "callback_data": "action_port_risk"}, {"text": "🍰 Sector Allocation", "callback_data": "action_port_sector"}],
            [{"text": "⬅️ Back", "callback_data": "menu_home"}, {"text": "🔄 Refresh", "callback_data": "menu_portfolio"}]
        ]
    }
    return add_timestamp(text), keyboard

def get_paper_menu():
    text = "📝 *PAPER TRADING REMOTE CONTROL*\n-------------------------------------\nSelect an action:"
    keyboard = {
        "inline_keyboard": [
            [{"text": "📄 Account Summary", "callback_data": "action_paper_account"}, {"text": "📑 Open Positions", "callback_data": "action_paper_orders"}],
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
        elif data == "menu_dashboard":
            text = intel.get_enterprise_dashboard()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_dashboard"))
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
        elif data == "menu_notifications":
            text = intel.get_notification_settings_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_notifications"))
        elif data == "menu_admin":
            text = intel.get_admin_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_admin"))
        elif data == "action_token_refresh":
            text = intel.trigger_token_refresh()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
        elif data == "action_token_toggle_auto":
            text = intel.toggle_auto_refresh()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
        elif data == "action_token_history":
            text = intel.get_token_refresh_history()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_token_center_menu())
        elif data in ("action_scan_swing", "action_scan_volume", "action_scan_breakout", "action_scan_best"):
            text = intel.get_scanner_summary("swing")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_scanner"))
        elif data == "action_scan_intraday":
            text = intel.get_scanner_summary("intraday")
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_scanner"))
        elif data == "action_scan_watchlist":
            text = intel.get_watchlist_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("menu_scanner"))
        elif data == "action_port_summary":
            text = intel.get_portfolio_summary()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_summary"))
        elif data == "action_port_positions":
            text = intel.get_open_positions_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_positions"))
        elif data == "action_port_risk":
            text = intel.get_risk_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_risk"))
        elif data == "action_port_sector":
            text = intel.get_sector_report()
            edit_message(token, chat_id, message_id, add_timestamp(text), get_back_menu("action_port_sector"))
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
        if cmd in ("/menu", "/help"):
            txt, kb = get_home_menu()
            send_message(token, chat_id, txt, reply_markup=kb)
            service.audit_command(str(chat_id), cmd, (time.time() - start_t) * 1000, True, "", len(txt))
            return
        elif cmd == "/dashboard":
            reply = intel.get_enterprise_dashboard()
        elif cmd in ("/status", "/health"):
            reply = intel.get_system_health()
        elif cmd == "/diag":
            reply = intel.get_diagnostics_report()
        elif cmd == "/ping":
            reply = intel.get_ping_report()
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
        elif cmd in ("/scanner", "/swing", "/fno", "/highvolume", "/breakout", "/topbuy", "/topsell", "/top", "/recent"):
            reply = intel.get_scanner_summary("swing")
        elif cmd == "/intraday":
            reply = intel.get_scanner_summary("intraday")
        elif cmd == "/market":
            reply = intel.get_market_status()
        elif cmd == "/news":
            reply = intel.get_market_news()
        elif cmd == "/copilot":
            reply = intel.get_copilot_analysis(arg if arg else "RELIANCE")
        elif cmd in ("/strategy", "/strategies", "/liststrategy"):
            reply = intel.list_strategies()
        elif cmd == "/runstrategy":
            reply = intel.run_custom_strategy(arg)
        elif cmd == "/createstrategy":
            reply = intel.create_custom_strategy(arg)
        elif cmd == "/deletestrategy":
            reply = intel.delete_custom_strategy(arg)
        elif cmd == "/explain":
            reply = intel.explain_stock_decision(arg if arg else "RELIANCE")
        elif cmd == "/paper":
            reply = intel.get_paper_trading_summary()
        elif cmd in ("/open", "/positions"):
            reply = intel.get_open_positions_report()
        elif cmd == "/closed":
            reply = intel.get_closed_positions_report()
        elif cmd == "/trade" and arg:
            reply = intel.execute_paper_trade_cmd(arg, "BUY")
        elif cmd == "/close" and arg:
            reply = intel.close_paper_trade_cmd(arg)
        elif cmd in ("/history", "/performance", "/statistics"):
            reply = intel.get_performance_report()
        elif cmd == "/journal":
            reply = intel.get_journal_report()
        elif cmd == "/features":
            reply = intel.get_features_report()
        elif cmd == "/portfolio":
            reply = intel.get_portfolio_summary()
        elif cmd == "/cash":
            reply = intel.get_cash_report()
        elif cmd == "/equity":
            reply = intel.get_equity_report()
        elif cmd == "/exposure":
            reply = intel.get_exposure_report()
        elif cmd == "/risk":
            reply = intel.get_risk_report()
        elif cmd == "/sector":
            reply = intel.get_sector_report()
        elif cmd == "/add" and arg:
            reply = intel.add_to_watchlist(arg)
        elif cmd == "/remove" and arg:
            reply = intel.remove_from_watchlist(arg)
        elif cmd in ("/watchlist", "/favorites", "/alerts"):
            reply = intel.get_watchlist_report()
        elif cmd == "/morning_report":
            reply = intel.generate_morning_report()
        elif cmd == "/midday_report":
            reply = intel.generate_midday_report()
        elif cmd == "/eod_report":
            reply = intel.generate_eod_report()
        elif cmd == "/broker":
            reply = intel.get_broker_summary()
        elif cmd == "/funds":
            reply = intel.get_broker_funds()
        elif cmd == "/holdings":
            reply = intel.get_broker_holdings()
        elif cmd == "/positions":
            reply = intel.get_broker_positions()
        elif cmd == "/orders":
            reply = intel.get_broker_orders()
        elif cmd == "/preview":
            reply = intel.get_broker_order_preview(arg if arg else "RELIANCE")
        elif cmd == "/analytics":
            reply = intel.get_analytics_report()
        elif cmd == "/strategy":
            reply = intel.get_strategy_report()
        elif cmd == "/heatmap":
            reply = intel.get_heatmap_report()
        elif cmd == "/replay":
            reply = intel.get_replay_report()
        elif cmd == "/report":
            reply = intel.get_full_report()
        elif cmd == "/export":
            fmt = arg.lower() if arg else "csv"
            export_path = intel.generate_export_file(fmt, "portfolio")
            if export_path:
                service.send_document(token, chat_id, export_path, caption=f"📊 RAHUUL RADAR Portfolio Export ({fmt.upper()})")
                reply = f"✅ Export generated successfully: `{os.path.basename(export_path)}`"
            else:
                reply = "❌ Failed to generate export file."
        elif cmd == "/admin":
            reply = intel.get_admin_report()
        elif cmd == "/notifications":
            reply = intel.get_notification_settings_report()
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

def run_scheduler(token):
    if schedule is None:
        return

    config = service.get_config()
    chat_id = config.get("telegram_authorized_chat_id")
    if not chat_id:
        return

    def _send_morning():
        service.send_message(token, chat_id, intel.generate_morning_report())

    def _send_midday():
        service.send_message(token, chat_id, intel.generate_midday_report())

    def _send_eod():
        service.send_message(token, chat_id, intel.generate_eod_report())

    schedule.every().day.at("08:30").do(_send_morning)
    schedule.every().day.at("12:30").do(_send_midday)
    schedule.every().day.at("15:45").do(_send_eod)

    while True:
        schedule.run_pending()
        time.sleep(1)

def telegram_polling(token):
    last_update_id = 0
    backoff = 1
    service.start_background_tasks(token)

    t_sched = threading.Thread(target=run_scheduler, args=(token,), daemon=True)
    t_sched.start()

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
    print("Starting RAHUUL RADAR Enterprise Telegram Command Center (v7.0.0 - Certified)...")
    config = service.get_config()
    token = config.get("telegram_bot_token") or config.get("telegram_token") or os.environ.get("TELEGRAM_BOT_TOKEN") or "8805672111:AAEBsy0L4Za7hb-2BthOd9WIvc37QdKXPPQ"

    telegram_polling(token)

if __name__ == "__main__":
    main()
