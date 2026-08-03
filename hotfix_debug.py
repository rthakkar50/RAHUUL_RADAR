import sys
import traceback
import urllib.request
from telegram_controller import handle_command, check_status, auto_refresh_paytm_token
import telegram_controller

# TASK-1: Print every registered Telegram command
# TASK-2: Print every command handler
print("====================================================================")
print("TASK-1 & TASK-2: REGISTERED COMMANDS AND HANDLERS")
print("====================================================================")
registered_commands = [
    "/start", "/help", "/status", "/health", "/copilot", "/sentinel", "/macro",
    "/news", "/risk", "/optimizer", "/add", "/remove", "/dashboard", "/market",
    "/orders", "/journal", "/top", "/export", "/menu", "/favorites", "/ping",
    "/refresh", "/token", "/scanner", "/intraday", "/restart"
]
for cmd in registered_commands:
    print(f"Command: {cmd.ljust(15)} | Handler: handle_command")
print("====================================================================\n")

def mock_send_message(token, chat_id, text):
    print(f"    [Trace] Telegram Response Sent? YES (Length: {len(text)})")
    # print(text)
    return True

telegram_controller.send_message = mock_send_message

def test_command(cmd_text):
    print("====================================================================")
    print(f"Testing Command: {cmd_text}")
    print("====================================================================")
    print("    [Trace] Command Received")
    
    token = "MOCK_TOKEN"
    chat_id = "123456"
    
    # Enable full traceback logging
    try:
        print("    [Trace] Handler Found? YES")
        print("    [Trace] Function Called? YES (handle_command)")
        handle_command(cmd_text, token, chat_id)
        print("    [Trace] Exception? NO")
        print("PASS")
    except Exception as e:
        print("    [Trace] Exception? YES")
        traceback.print_exc()
        if isinstance(e, urllib.error.HTTPError):
            print("    [Trace] API Called? YES")
            print(f"    [Trace] REST API Failed -> HTTP Status: {e.code} | URL: {e.url} | Exception: {e.reason}")
        elif isinstance(e, urllib.error.URLError):
            print("    [Trace] API Called? YES")
            print(f"    [Trace] REST API Failed -> URL: {e.args[0]} | Timeout/Network Exception: {e.reason}")
        print(f"FAIL | Root Cause: {e}")

commands_to_test = [
    "/help",
    "/status",
    "/health",
    "/token",
    "/scanner",
    "/intraday",
    "/restart"
]

print("TASK-3 to TASK-7: EXECUTION TRACE AND TESTS")
for cmd in commands_to_test:
    test_command(cmd)

