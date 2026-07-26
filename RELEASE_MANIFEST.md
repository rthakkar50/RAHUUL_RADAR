# RAHUUL RADAR PRO - RELEASE MANIFEST (v1.0.0)

## VERSION
`1.0.0`

## BUILD_DATE
`2026-07-26`

## GIT_COMMIT
`1865219b7fa9b39ac279495710bc729866bec3da`

## DEPENDENCIES
- PySide6 == 6.11.1
- pandas == 3.0.3
- numpy == 2.2.6
- requests == 2.34.2
- websocket-client == 1.9.1
- websockets == 16.0
- dhanhq == 2.2.0
- cryptography == 46.0.4
- urllib3 == 2.6.3
- python-dateutil == 2.9.0.post0
- pytz == 2026.1.1
- setuptools == 79.1.0

## SUPPORTED OS
- **macOS**: Apple Silicon (M1/M2/M3/M4) & Intel (x86_64) - macOS 12+
- **Windows**: Windows 10 / Windows 11 (64-bit)
- **Linux**: Ubuntu 20.04+, Debian 11+, RHEL/Rocky Linux 8+ (x86_64 and ARM64 architectures)

## KNOWN LIMITATIONS
- **Public API Rate-Limiting**: Yahoo Finance fallback HTTP requests may throttle during rapid back-to-back batch scans; mitigated via an internal 60-second option chain cache TTL and multi-threading throttling.
- **Data Latency**: Unauthenticated free-tier market endpoints carry an inherent 1 to 15-minute price delay; live real-time scalping necessitates active broker (Paytm / Dhan) OAuth token authentication.
- **Automated Trading Execution**: v1.0.0 is dedicated to analytics, scanning, signal scoring, paper trading, and journaling. Automated live broker execution will activate in v1.1.0.
