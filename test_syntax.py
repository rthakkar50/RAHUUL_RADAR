import sys

files_to_test = [
    'auth.paytm_auth',
    'market.paytm_provider',
    'market.paytm_websocket',
    'ui.settings',
    'application.intraday_scanner_service',
    'application.scalping_scanner_service',
    'application.swing_scanner_service',
    'application.paper_market_updater',
    'core.scanner_engine'
]

errors = False
for m in files_to_test:
    try:
        __import__(m)
        print(f"SUCCESS: {m}")
    except Exception as e:
        print(f"ERROR importing {m}: {e}")
        errors = True

if errors:
    sys.exit(1)
