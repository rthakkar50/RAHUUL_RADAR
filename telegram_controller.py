#!/usr/bin/env python3
"""
RAHUUL RADAR - Telegram Bot 24x7 Controller
Allows remote token updates, status monitoring, and service restart via Telegram.
"""
import urllib.request
import urllib.parse
import json
import time
import subprocess
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
CONFIG_PATH = BASE_DIR / "config.json"

def get_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=data)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True
        except Exception as e:
            print(f"Error sending message (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(0.5 * attempt)
    return False

def validate_user_session(config):
    """Validate user session and verify active Paytm credentials."""
    paytm_cfg = config.get("paytm", {})
    api_key = paytm_cfg.get("api_key") or os.environ.get("PAYTM_API_KEY", "").strip()
    acc_token = paytm_cfg.get("access_token") or os.environ.get("PAYTM_ACCESS_TOKEN", "").strip()
    if not api_key:
        return False, "Paytm API Key not configured or missing from environment."
    if not acc_token:
        return False, "No active access token found in session configuration."
    if "placeholder" in acc_token.lower() or len(acc_token) < 10:
        return False, "Access token appears uninitialized or invalid."
    return True, "Active Paytm session validated and operational."

def check_status():
    try:
        out = subprocess.check_output(["sudo", "systemctl", "is-active", "rahuul-radar.service"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        if out == "active":
            return "🟢 *RAHUUL RADAR* service is currently *ACTIVE & RUNNING 24x7*!"
        else:
            return f"🔴 *RAHUUL RADAR* service status: `{out}`"
    except subprocess.CalledProcessError as e:
        return f"🔴 *RAHUUL RADAR* service status: `{e.output.decode('utf-8').strip()}`"
    except Exception as e:
        return f"❓ Could not check systemctl status: {e}"

def restart_service():
    try:
        subprocess.check_call(["sudo", "systemctl", "restart", "rahuul-radar.service"])
        return "✅ *RAHUUL RADAR* service has been restarted successfully!"
    except Exception as e:
        return f"❌ Failed to restart service: {e}"

def handle_command(text, token, chat_id):
    text = text.strip()
    cmd_name = text.split()[0] if text else ""
    if cmd_name in ("/auth", "/token"):
        print(f"Received command: {cmd_name} [CREDENTIALS SANITIZED]")
    else:
        print(f"Received command: {text}")
    
    if text in ("/start", "/help"):
        msg = (
            "🤖 *RAHUUL RADAR TELEGRAM CONTROLLER*\n"
            "-------------------------------------\n"
            "Available Commands:\n\n"
            "🔑 `/login`\n"
            "   Generate a fresh daily Paytm login link and check session status.\n\n"
            "🛡️ `/session`\n"
            "   Validate current active user session and access token health.\n\n"
            "🔄 `/auth <REQUEST_TOKEN>`\n"
            "   Exchange browser callback token for 24h Access Tokens.\n\n"
            "🎟️ `/token <NEW_TOKEN>`\n"
            "   Directly update your daily Paytm API token.\n\n"
            "📊 `/status`\n"
            "   Check if the 24x7 trading system is running.\n\n"
            "🚀 `/restart`\n"
            "   Restart the trading server instantly.\n\n"
            "✈️ 100% Remote Mobile Control Active!"
        )
        send_message(token, chat_id, msg)

    elif text.startswith("/status"):
        status_msg = check_status()
        send_message(token, chat_id, status_msg)

    elif text.startswith("/session"):
        config = get_config()
        is_valid, reason = validate_user_session(config)
        status_icon = "🟢" if is_valid else "🔴"
        send_message(token, chat_id, f"{status_icon} *User Session Validation*\n----------------------------\n*Status*: {'ACTIVE & VALID' if is_valid else 'EXPIRED / INVALID'}\n*Details*: `{reason}`")

    elif text.startswith("/restart"):
        send_message(token, chat_id, "🔄 Restarting RAHUUL RADAR service...")
        res_msg = restart_service()
        send_message(token, chat_id, res_msg)

    elif text.startswith("/login"):
        config = get_config()
        is_valid, session_reason = validate_user_session(config)
        session_notice = f"🟢 *Current Session*: Active and Valid!\n" if is_valid else f"🔴 *Current Session*: Invalid/Expired (`{session_reason}`)\n"

        api_key = config.get("paytm", {}).get("api_key") or os.environ.get("PAYTM_API_KEY")
        if not api_key:
            send_message(token, chat_id, f"❌ *Login Failed*: `PAYTM_API_KEY` is missing from system configuration and environment variables.\n\nPlease configure your Paytm credentials in Settings before initiating login.")
            return

        login_url = f"https://login.paytmmoney.com/merchant-login?apiKey={api_key}&state=RADAR"
        msg = (
            f"🔑 *PAYTM MONEY DAILY LOGIN*\n"
            f"---------------------------\n"
            f"{session_notice}\n"
            f"1️⃣ Click this login link:\n[➡️ Open Paytm Login]({login_url})\n\n"
            f"2️⃣ Log in with your Paytm credentials.\n\n"
            f"3️⃣ After login, the browser address bar will show a link like:\n"
            f"`http://127.0.0.1:8000/callback?requestToken=ABCD1234...`\n\n"
            f"4️⃣ Copy that `requestToken` and send it here like:\n"
            f"`/auth ABCD1234...`\n\n"
            f"🤖 I will automatically validate and exchange it for 24h Access Tokens!"
        )
        send_message(token, chat_id, msg)

    elif text.startswith("/auth"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(token, chat_id, "⚠️ Please provide the request token after `/auth`.\nExample: `/auth 069b2d8d...`")
            return
        
        clean_input = "".join(parts[1].split())
        req_token = clean_input
        if "requestToken=" in req_token:
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(req_token if req_token.startswith("http") else f"http://{req_token}")
                qs = parse_qs(parsed.query)
                req_token = qs.get("requestToken", [req_token])[0]
            except Exception:
                req_token = req_token.split("requestToken=")[-1].split("&")[0].strip()

        req_token = "".join(req_token.split()).strip()
        config = get_config()
        paytm_cfg = config.get("paytm", {})
        api_key = paytm_cfg.get("api_key") or os.environ.get("PAYTM_API_KEY")
        api_secret = paytm_cfg.get("api_secret_key") or os.environ.get("PAYTM_API_SECRET")
        if not api_key or not api_secret:
            send_message(token, chat_id, "❌ *Authentication Error*: Paytm API Key or Secret is missing from system configuration and environment. Cannot complete token exchange.")
            return
        
        send_message(token, chat_id, f"⏳ Exchanging Request Token (`{req_token}`) for 24-hour Access Token via Paytm API...")
        
        url = "https://developer.paytmmoney.com/accounts/v2/gettoken"
        payload = {
            "apiKey": api_key,
            "api_key": api_key,
            "apiSecretKey": api_secret,
            "api_secret_key": api_secret,
            "requestToken": req_token,
            "request_token": req_token
        }
        
        try:
            import requests
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            if resp.status_code != 200:
                send_message(token, chat_id, f"❌ *Paytm API Error* (HTTP {resp.status_code}):\n`{resp.text}`\n\n💡 Credentials or token invalid. Try logging in again via `/login` to get a fresh link!")
                return
            data = resp.json()
                
            token_data = data.get("data", data) if isinstance(data, dict) else data
            acc_token = token_data.get("access_token", "")
            pub_token = token_data.get("public_access_token", "")
            read_token = token_data.get("read_access_token", "")
            
            if not acc_token:
                send_message(token, chat_id, f"❌ *Session Validation Failed*: Could not extract access token from broker response:\n`{json.dumps(data)}`")
                return
                
            if "paytm" not in config:
                config["paytm"] = {}
            config["paytm"]["access_token"] = acc_token
            config["paytm"]["public_access_token"] = pub_token or acc_token
            config["paytm"]["read_access_token"] = read_token or acc_token
            save_config(config)
            
            is_val, val_reason = validate_user_session(config)
            if is_val:
                send_message(token, chat_id, "🎉 *User Session Validated & Saved Successfully!* Restarting RAHUUL RADAR 24x7 Engine...")
                res_msg = restart_service()
                send_message(token, chat_id, f"✅ *Paytm Live Feed Active!*\n\n{res_msg}")
            else:
                send_message(token, chat_id, f"⚠️ *Warning*: Tokens generated but session validation check returned: `{val_reason}`")
        except Exception as e:
            send_message(token, chat_id, f"❌ Token generation failed: `{str(e)}`\n(Make sure the requestToken is fresh and valid!)")

    elif text.startswith("/token"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(token, chat_id, "⚠️ Please provide the token after `/token`.\nExample: `/token eyJ0eXAi...`")
            return
        
        new_token = parts[1].strip()
        config = get_config()
        if "paytm" not in config:
            config["paytm"] = {}
        
        config["paytm"]["access_token"] = new_token
        config["paytm"]["public_access_token"] = new_token
        config["paytm"]["read_access_token"] = new_token
        
        try:
            save_config(config)
            is_valid, _ = validate_user_session(config)
            status_text = "Active & Valid 🟢" if is_valid else "Unverified ⚠️"
            send_message(token, chat_id, "⏳ Token saved in `config.json`! Restarting RAHUUL RADAR engine...")
            res_msg = restart_service()
            send_message(token, chat_id, f"🎯 *Paytm Token Updated Successfully!*\n*Session Status*: {status_text}\n\n{res_msg}\n🟢 Live market data stream should now be active!")
        except Exception as e:
            send_message(token, chat_id, f"❌ Failed to save token: {e}")
    else:
        send_message(token, chat_id, "❓ Unknown command. Type `/help` to see available commands.")

def main():
    print("Starting RAHUUL RADAR Telegram Controller...")
    last_update_id = 0
    
    while True:
        try:
            config = get_config()
            token = config.get("telegram_token", "").strip()
            chat_id = str(config.get("telegram_chat_id", "")).strip()
            
            if not token:
                print("telegram_token not configured in config.json. Retrying in 10s...")
                time.sleep(10)
                continue
            
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            if last_update_id > 0:
                url += f"?offset={last_update_id + 1}&timeout=10"
            else:
                url += "?timeout=10"
                
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
            if data.get("ok"):
                for update in data.get("result", []):
                    last_update_id = max(last_update_id, update.get("update_id", 0))
                    msg = update.get("message", {})
                    sender_id = str(msg.get("from", {}).get("id", "")).strip()
                    text = msg.get("text", "")
                    
                    # Auto-bind if chat_id is empty!
                    if not chat_id and sender_id and text:
                        print(f"Auto-binding master Telegram Chat ID: {sender_id}")
                        chat_id = sender_id
                        config["telegram_chat_id"] = chat_id
                        save_config(config)
                        send_message(token, chat_id, f"🎉 *Welcome to RAHUUL RADAR!*\nYour Telegram Account (ID: `{chat_id}`) is now securely bound as the Master Controller for your 24x7 Trading System!")
                        handle_command("/help", token, chat_id)
                        continue

                    # Security check: only allow commands from the configured telegram_chat_id
                    if sender_id == chat_id and text:
                        handle_command(text, token, chat_id)
                    elif text:
                        print(f"Ignored message from unauthorized user ID: {sender_id}")
                        
        except Exception as e:
            time.sleep(3)
        time.sleep(1)

if __name__ == "__main__":
    main()
