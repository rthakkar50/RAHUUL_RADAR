# RAHUUL RADAR PRO v1.0.0 - KNOWN LIMITATIONS

## 1. Data Latency & Provider Throttling
- **Free-Tier Yahoo Finance Data**: Public Yahoo Finance market endpoints possess an inherent 1-minute to 15-minute price delay depending on symbol tiering. Sub-minute scalping strategies should rely on real-time authenticated broker integrations (Paytm/Dhan).
- **API Rate Limiting**: Rapid successive scans across the entire 180+ F&O watchlist using public HTTP fallback methods may encounter short-term throttling (HTTP 429). An in-memory option chain cache (60-second TTL) is implemented to prevent repeated identical API requests. A 3-minute cooldown between forced cache purges is recommended.

## 2. Broker Execution State
- **Signal Analysis vs. Automated Order Execution**: RAHUUL RADAR PRO v1.0.0 operates strictly as an institutional-grade signal generation, technical scoring, and paper trading/journaling platform. One-click live automated brokerage trade execution will be officially activated in release v1.1.0.

## 3. Memory & Resource Usage
- **Long-Running Live Sessions**: Continuous 24x7 active option chain scanning and live background websocket streaming accumulate historical tick cache inside standard application RAM. While zero memory leaks have been certified over 30-cycle stress tests via aggressive DataFrame garbage collection, system environments with less than 8 GB of total system RAM are advised to perform a scheduled nightly daemon restart.

## 4. Symbol Lifecycle & Corporate Actions
- **Delisted / Merged Stocks**: Symbols undergoing active corporate restructuring, tickers renaming, or temporary suspension on NSE/BSE will return `NO_DATA` flags. The engine gracefully bypasses these symbols without interrupting scanner batch processing.
