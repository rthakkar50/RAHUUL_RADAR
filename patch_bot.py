with open('telegram_controller.py', 'r') as f:
    content = f.read()

old_handler = """def handle_text_command(text, token, chat_id):
    if not is_authorized(chat_id):
        log_audit(chat_id, text, "DENIED", "Unauthorized CHAT_ID")
        send_message(token, chat_id, "⛔ Access Denied.")
        return
        
    log_audit(chat_id, text, "GRANTED")
    
    text_content, kb = get_home_menu()
    send_message(token, chat_id, text_content, kb)"""

new_handler = """def handle_text_command(text, token, chat_id):
    if not is_authorized(chat_id):
        log_audit(chat_id, text, "DENIED", "Unauthorized CHAT_ID")
        send_message(token, chat_id, "⛔ Access Denied.")
        return
        
    log_audit(chat_id, text, "GRANTED")
    
    from core.telegram_intelligence import TelegramIntelligence
    intel = TelegramIntelligence.get_instance()
    
    cmd_name = text.strip().split()[0] if text else ""
    
    if cmd_name == "/status":
        send_message(token, chat_id, intel.get_system_health())
    elif cmd_name == "/health":
        send_message(token, chat_id, intel.get_system_health())
    elif cmd_name == "/token":
        send_message(token, chat_id, intel.get_paytm_status_detailed())
    elif cmd_name == "/scanner":
        send_message(token, chat_id, intel.get_scanner_summary("swing"))
    elif cmd_name == "/intraday":
        send_message(token, chat_id, intel.get_scanner_summary("intraday"))
    elif cmd_name == "/portfolio":
        send_message(token, chat_id, intel.get_portfolio_summary())
    elif cmd_name == "/paper":
        send_message(token, chat_id, intel.get_paper_trading_summary())
    elif cmd_name == "/market":
        send_message(token, chat_id, intel.get_market_status())
    elif cmd_name == "/signal" and len(text.split()) > 1:
        send_message(token, chat_id, intel.get_copilot_analysis(text.split()[1]))
    elif cmd_name == "/restart":
        send_message(token, chat_id, "✅ *Restart sequence initiated.* API requested to reboot.")
    else:
        # Default to showing the interactive menu!
        text_content, kb = get_home_menu()
        send_message(token, chat_id, text_content, kb)"""

if old_handler in content:
    content = content.replace(old_handler, new_handler)
    with open('telegram_controller.py', 'w') as f:
        f.write(content)
    print("Patched successfully.")
else:
    print("Could not find handler.")
