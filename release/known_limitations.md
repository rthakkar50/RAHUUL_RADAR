# RAHUUL_RADAR Enterprise v2.0 — Known Limitations

1. **GUI Display on Headless Servers:** PySide6 desktop GUI features require a local X11/Qt display server. On headless cloud servers (Render Cloud), the application runs via REST APIs and Telegram CLI seamlessly.
2. **Paper Trading Simulation:** Paper trading fills simulate market orders immediately and check limit orders against tick updates. Order book depth slippage is modeled statically.
