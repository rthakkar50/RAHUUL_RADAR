# SPRINT-178A: ENTERPRISE SIGNAL WATERFALL FORENSIC AUDIT

## TASK-1: Pipeline Trace Counts
Target Universe ............. 200
↓
Scanner Filter Passed ....... 194
↓
Master Pipeline Passed ...... 0
↓
Qualified Results ........... 20

## TASK-2: Rejection Details
- **LTIM.NS** | Stage: Scanner Engine | Engine: ScannerEngine | Reason: Dropped before Pipeline (No Data / Low Liquidity)
- **PEL.NS** | Stage: Scanner Engine | Engine: ScannerEngine | Reason: Dropped before Pipeline (No Data / Low Liquidity)
- **TATACHEMICALS.NS** | Stage: Scanner Engine | Engine: ScannerEngine | Reason: Dropped before Pipeline (No Data / Low Liquidity)
- **TATAELEXSI.NS** | Stage: Scanner Engine | Engine: ScannerEngine | Reason: Dropped before Pipeline (No Data / Low Liquidity)
- **TATAMOTORS.NS** | Stage: Scanner Engine | Engine: ScannerEngine | Reason: Dropped before Pipeline (No Data / Low Liquidity)
- **ZOMATO.NS** | Stage: Scanner Engine | Engine: ScannerEngine | Reason: Dropped before Pipeline (No Data / Low Liquidity)
- **MANAPPURAM.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: <core.false_signal_report.FalseSignalReport object
- **RECLTD.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: <core.false_signal_report.FalseSignalReport object
- **ASHOKLEY.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: <core.false_signal_report.FalseSignalReport object
- **EICHERMOT.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: <core.false_signal_report.FalseSignalReport object
- **LAURUSLABS.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **DIVISLAB.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **KALYANKJIL.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **FEDERALBNK.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **BAJFINANCE.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **MARICO.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **TITAN.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **TVSMOTOR.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **SUNPHARMA.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates
- **HEROMOTOCO.NS** | Stage: Master Signal Pipeline | Engine: MasterSignalPipeline | Reason: Failed Pipeline Gates

## TASK-3: Rejection Summary
Total Rejected: 200

## TASK-4: Stage Execution
- **ScannerEngine**: In: 200 | Out: 194 | Dropped: 6 | Time: 6.91s
- **MasterSignalPipeline**: In: 194 | Out: 0 | Dropped: 194 | Time: 0.10s

## TASK-6: Decision Mutation Audit
- MANAPPURAM.NS: WATCH -> REJECTED
- RECLTD.NS: WATCH -> REJECTED
- ASHOKLEY.NS: WATCH -> REJECTED
- EICHERMOT.NS: WATCH -> REJECTED
- LAURUSLABS.NS: BUY -> REJECTED
- DIVISLAB.NS: BUY -> REJECTED
- KALYANKJIL.NS: BUY -> REJECTED
- FEDERALBNK.NS: BUY -> REJECTED
- BAJFINANCE.NS: BUY -> REJECTED
- MARICO.NS: BUY -> REJECTED

## TASK-9: Root Cause Ranking
#1 Market Data / Liquidity (Scanner Filters)
#2 Precision Entry Score Ceiling
