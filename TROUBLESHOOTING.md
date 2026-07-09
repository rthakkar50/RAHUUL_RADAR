# TROUBLESHOOTING

## 1. No Internet / Connection Failed
**Symptom**: The application opens but the scanner hangs immediately or displays "Network Error".
**Solution**: Verify your broadband connection. RAHUUL RADAR PRO requires an active, uninterrupted internet connection to function. If you are behind a corporate proxy, you must configure your proxy settings at the OS level.

## 2. Yahoo Timeout / Freezing
**Symptom**: Scanner progress bar is stuck. Log files show `TimeoutException`.
**Solution**: Yahoo Finance enforces rate limits.
1. Wait 5-10 minutes before initiating a new scan.
2. In `Settings`, switch to a different Data Provider (e.g., Dhan) if you possess API credentials.

## 3. Missing Data / NO_DATA Tags
**Symptom**: Stocks like `TATAMOTORS.NS` are listed as `NO_DATA` or missing from the results.
**Solution**:
- This typically happens if the symbol has been delisted, renamed, or temporarily blocked by the exchange.
- The engine automatically skips and ranks them with zero scores to prevent application crashes.

## 4. Scanner Running Slow
**Symptom**: Scans take longer than 30 seconds.
**Solution**:
- Ensure no other heavily CPU-bound tasks are running on your machine.
- Under **Settings > Performance**, lower the concurrent thread count.
- Delete the `/cache` folder and restart the application to force a clean data download.

## 5. No BUY Signals
**Symptom**: The scanner finishes successfully, but 0 BUY signals are generated.
**Solution**: This is a feature, not a bug. If the overall Market Regime is severely Bearish or highly volatile, the Risk Manager explicitly blocks BUY setups to protect capital. 

## 6. Export Problems
**Symptom**: Clicking "Export to Excel" does nothing or shows an error.
**Solution**: Ensure that Microsoft Excel is closed if you are attempting to overwrite an existing `exports/scan.xlsx` file. Windows locks open files, preventing the software from writing to them.

## 7. Reset Settings
**Symptom**: UI is corrupted or settings are misconfigured.
**Solution**: Close the application. Navigate to the installation folder, locate the `/config` directory, and delete `settings.json`. Relaunch the application to restore factory defaults.
