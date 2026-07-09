# RAHUUL RADAR PRO v1.0

## Project Overview
RAHUUL RADAR PRO is a high-performance, institutional-grade stock screening and analysis platform tailored for the Indian Equity Market (F&O). It bridges the gap between retail trading tools and professional quantitative analysis by leveraging adaptive ranking, multi-timeframe engines, and robust real-time market regime detection.

## Features
- **Intraday Scanner**: Fast, multi-threaded scanner identifying breakouts and breakdowns.
- **Swing Scanner**: Deep structural analysis for multi-day position holding.
- **Active Scanner**: Live real-time market updates tracking extreme momentum and liquidity shifts.
- **Institutional Analytics Dashboard**: Complete top-down market perspective, ADX trend filtering, and sector rotation metrics.
- **Advanced Ranking System**: proprietary Confidence and Grade-based scoring (A+, A, B, C, D).
- **Data Export**: Complete CSV, JSON, and Excel data dumps for downstream analysis.

## System Requirements
- **OS**: Windows 10/11 (64-bit)
- **CPU**: 4 Cores / 8 Threads minimum (Intel i5/AMD Ryzen 5 equivalent or better)
- **RAM**: 8 GB RAM (16 GB Recommended for intensive intraday scanning)
- **Network**: Stable broadband internet connection (low latency preferred)
- **Disk Space**: 500 MB free space (SSD strongly recommended)

## Installation
See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for full installation instructions.

## Quick Start
1. Launch **RahuulRadarPro.exe**.
2. Navigate to the **Swing Scanner** tab.
3. Click **Scan F&O Universe**.
4. Review the top **BUY** signals in the results table.
5. Export results via the **Export to Excel** button.

## Screenshots Placeholder
![Dashboard](assets/dashboard_placeholder.png)
![Scanner](assets/scanner_placeholder.png)

## Folder Structure
```text
RAHUUL RADAR PRO/
├── RahuulRadarPro.exe
├── config/
├── logs/
├── exports/
├── cache/
├── reports/
├── resources/
├── icons/
├── images/
└── fonts/
```

## Architecture
The system employs a multi-layered, decoupled architecture:
1. **Core Engines**: Momentum, Trend, Structure, Sector Rotation, and Risk Management.
2. **Scanner Service**: Thread-pool execution for concurrent multi-symbol analysis.
3. **Data Providers**: Fault-tolerant API handlers (Yahoo Finance / Dhan).
4. **UI Layer**: Asynchronous PySide6 interfaces ensuring 60 FPS responsiveness.

## Known Limitations
- Data delays depending on the Yahoo Finance / Free-tier API constraints.
- Real-time options data strictly depends on the broker API (Dhan) uptime.
- High memory usage if cache is strictly maintained over 24+ hour uninterrupted sessions.

## Roadmap
- **v1.1**: Direct Broker API Execution (One-click trading).
- **v1.2**: Advanced Options Chain Greeks visualization.
- **v2.0**: Machine Learning Pattern Recognition models.

## Support
For technical support, licensing, and general inquiries, please contact:
**Rahul Thakkar** (Commercial Distribution Team)

## License
See [LICENSE](LICENSE) for terms of use. All rights reserved.
