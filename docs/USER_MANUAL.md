# RAHUUL_RADAR Pro - User Manual

Welcome to RAHUUL_RADAR Pro, the professional Indian stock market scanner and trading analytics desktop application. This manual will guide you through setting up and using the application effectively.

---

## Table of Contents
1. [Installation](#installation)
2. [First-Time Setup](#first-time-setup)
3. [Dhan API Setup](#dhan-api-setup)
4. [Telegram Alert Setup](#telegram-alert-setup)
5. [Scanner Modes](#scanner-modes)
6. [Watchlist](#watchlist)
7. [Backtesting](#backtesting)
8. [Paper Trading](#paper-trading)
9. [Export & Report Usage](#export--report-usage)
10. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- Windows 10/11, macOS, or Linux.
- If running from source, ensure **Python 3.12+** is installed on your system.

### Running from Compiled Executable
If you have downloaded a release version (e.g., `RAHUUL_RADAR.app` for Mac or the Windows installer):
1. Simply double-click the application icon to launch.
2. The application will automatically create its databases (`data/`) and configuration file on the first run.

### Running from Source
1. Open your terminal or command prompt.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python main.py
   ```

---

## First-Time Setup

When you first launch the application, you will be greeted with a clean, professional dashboard. 
The application will automatically detect if it is running for the first time and will initialize local databases (for caching, paper trading, and journaling). 

To customize your experience, navigate to the **Settings** tab on the left sidebar where you can configure:
- Starting Capital for Paper Trading
- API Integrations
- UI Preferences (e.g., Scan intervals)

---

## Dhan API Setup

To enable live market data and real-time execution capabilities, you must configure your Dhan API credentials.

1. Navigate to the **Settings** tab.
2. Locate the **API Configuration** section.
3. Enter your **Dhan Client ID**.
4. Enter your **Dhan Access Token** (generated from the Dhan web portal under API management).
5. Click **Save Settings**.
6. The connection indicator on the Dashboard will turn Green (🟢 API: Connected) once successfully authenticated.

---

## Telegram Alert Setup

You can configure the application to send you instant alerts when the auto-scanner finds a high-confidence setup.

1. Create a bot using BotFather on Telegram and note the **Bot Token**.
2. Find your **Chat ID** (using bots like @userinfobot or checking your channel ID).
3. In the application **Settings** tab, scroll to the **Telegram Integration** section.
4. Input your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
5. Check the box to **Enable Alerts** and hit **Save Settings**.

---

## Scanner Modes

RAHUUL_RADAR offers multiple scanning engines designed for different trading styles:

- **Swing Scanner**: Scans higher timeframes (Daily/Weekly) focusing on momentum, trend alignment, and structural breakouts. Ideal for holding positions for days or weeks.
- **Intraday Scanner**: Scans lower timeframes (5m/15m) focusing on VWAP alignment, volume spikes, and immediate momentum. Ideal for day trading.
- **Auto-Scanner**: A background worker that can be toggled via the Dashboard ("Auto Scan: ON"). It will automatically re-scan the F&O universe at your configured interval and issue notifications.

---

## Watchlist

The **Dashboard** features a Top Buys table where you can track the best setups.
- **Add to Watchlist**: Click the "Add to Watchlist" button next to any symbol to track it actively. 
- You can manage your saved symbols which are persisted locally, allowing you to build a curated list of high-potential stocks for the day.

---

## Backtesting

The **Backtest** tab allows you to evaluate how specific setups would have performed historically.

1. Select a **Symbol** and a **Date Range**.
2. Click **Run Backtest**.
3. The engine simulates the scanner's entry/exit rules against historical price action.
4. Review the resulting equity curve, win rate, and total drawdown in the analytics view.

---

## Paper Trading

Before risking real capital, practice with the built-in Paper Trading engine!

1. Navigate to the **Dashboard** or **Scanner** results.
2. Next to a trade setup, use the **Trade Execution Panel**.
3. Select **"Paper Trade"** instead of "Live Execution".
4. The application will track the entry price, target, and stop loss, recording the simulated P&L in the **Journal** tab without connecting to your broker.

---

## Export & Report Usage

The application heavily features data exporting for external analysis.

- **CSV / Excel / JSON**: In the scanner toolbar, you will find export icons. Click these to dump the current scanner table directly to your `exports/` folder.
- **Diagnostics**: If you need to generate a full system health audit (PCE Audit), click **Diagnostics** on the dashboard. A markdown report will be generated and saved in the `reports/` folder.

---

## Troubleshooting

- **"Market Status: CLOSED" when it's open**: Check your system clock. The application restricts scanning to Indian Standard Time (IST) market hours (09:15 - 15:30).
- **Scanner is hanging or returning no results**: Ensure your Dhan API credentials are valid. If you are rate-limited, wait a few minutes or adjust your auto-scan interval in Settings.
- **Where are the logs?**: If the app crashes, open the **Diagnostics** tool and click **Open Log**, or manually navigate to the `logs/app.log` file in the application directory.

---
*For legal and risk information, please read the [TRADING_DISCLAIMER.md](TRADING_DISCLAIMER.md) before using this software.*
