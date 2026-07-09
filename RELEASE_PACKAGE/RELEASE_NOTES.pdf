# RELEASE NOTES - v1.0.0

**Release Date:** 2026-07-09
**Product:** RAHUUL RADAR PRO

Welcome to the 1.0 launch of RAHUUL RADAR PRO! This release marks the transition from beta engineering into a fully production-ready, institutional-grade scanning tool.

## New Features
- **Intraday, Swing, and Active Scanners**: Three unique scanning modules tailored to specific holding periods.
- **Institutional Analytics Dashboard**: Live Market Regime detection, ADX trend filtering, and Sector Rotation mapping.
- **Master Signal Pipeline**: AI-driven adaptive weighting engine that adjusts indicator thresholds based on live volatility.
- **Comprehensive Grading**: Stocks are definitively ranked from A+ to D based on multiple conflating technical signals.
- **Data Export**: Full CSV, JSON, and Excel export support.

## Major Improvements
- **UI Modernization**: A complete dark-mode, 60-FPS reactive interface built on PySide6.
- **Thread Safety**: Long-running scans now execute asynchronously without freezing the UI.
- **Robust Caching**: Historical data is cached locally to prevent aggressive API timeouts and drastically speed up multi-timeframe analysis.

## Performance
- Scanner latency reduced by 85% via Bulk-Download parallel processing.
- Ram usage stabilized (proven 0.0% leakage over intensive 30-cycle stress tests).
- Optimized Memory Footprint: Garbage collection forces aggressive offloading of obsolete pandas DataFrames.

## Bug Fixes
- Fixed an issue where the Context Menu would crash the application due to unlinked Qt bindings.
- Fixed an issue where Excel Export silently failed due to missing dependencies.
- Resolved race conditions affecting the progress bar during early scanner abortion.
- Handled Yahoo Finance 404/Delisted symbols securely without halting the execution batch.

## Known Issues
- Network timeouts from Yahoo Finance can occasionally throttle rapid successive scans. A 3-minute cooldown is recommended.
- Free-tier Yahoo Data possesses an inherent 1-minute delay which may affect sub-minute Scalping strategies.
