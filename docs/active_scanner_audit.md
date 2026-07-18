# F&O Active Scanner Architecture Audit (Sprint 81.1)

Based on a complete architectural audit of the **F&O Active Scanner**, here is the exact runtime flow and technical analysis of the current implementation.

==================================================
## TRACE THE COMPLETE FLOW
==================================================

**Data Provider**
- **File Name**: `application/intraday_scanner_service.py`
- **Class**: `IntradayScannerService`
- **Method**: `execute_intraday_scan()`
- **Responsibility**: Initializes either `DhanProvider` or `YahooFinanceProvider`. Fetches the `get_all_symbols()` list.

**Scanner**
- **File Name**: `scanner/scanner_engine.py`
- **Class**: `ScannerEngine`
- **Method**: `scan_market()`
- **Responsibility**: Loops through the symbol universe and triggers the core engines. *(Note: Receives `mode="INTRADAY"`.)*

**Indicator Engines**
- **File Name**: `scanner/scanner_engine.py`
- **Class**: `TrendEngine`, `MomentumEngine`, `StructureEngine`, etc.
- **Method**: `evaluate()`
- **Responsibility**: Calculates raw indicator values. 

**Decision Engine**
- **File Name**: `core/decision_engine.py`
- **Class**: `DecisionEngine`
- **Method**: `evaluate()`
- **Responsibility**: Takes engine outputs and generates a raw BUY/SELL/WATCH decision.

**Signal Pipeline (Risk / Entry / SL)**
- **File Name**: `core/master_signal_pipeline.py`
- **Class**: `MasterSignalPipeline`
- **Method**: `run()`
- **Responsibility**: Generates recommended Entry, Stop Loss, Target 1, Target 2, and validates Risk/Reward mathematically.

**Validation & Execution**
- **File Name**: `core/trade_execution_center.py`
- **Class**: `TradeExecutionCenter`
- **Method**: `validate_request()`, `perform_risk_check()`
- **Responsibility**: Simulates a live trade request and ensures position sizing and institutional boundaries are valid.

**Priority Engine (Post-Processing)**
- **File Name**: `application/intraday_scanner_service.py`
- **Class**: `IntradayScannerService`
- **Method**: `execute_intraday_scan()` (Lines 295-325)
- **Responsibility**: Runs the `EliteSelectionEngine` and `PrecisionEntryEngine` on the results. Then performs an inline `sort()` and manual truncation (`elite_picks = buys[:10] + watches[:10] + sells[:10]`) before sending to UI.

**UI**
- **File Name**: `ui/pages/intraday_scanner_page.py`
- **Class**: `IntradayScannerPage`
- **Method**: `_populate_table()`
- **Responsibility**: Renders the final returned arrays on the front-end grid.

==================================================
## VERIFY REUSED COMPONENTS
==================================================

1. **Is ScannerEngine reused?** **Yes.** It is instantiated and called natively.
2. **Is MasterSignalPipeline reused?** **Yes.** It is instantiated and run exactly like the Swing service.
3. **Is DecisionEngine reused?** **Yes.** (As well as the `MasterAIDecisionEngine`).
4. **Is TradePriorityEngine reused?** **NO.** The Active Scanner completely bypasses the `TradePriorityEngine`. Instead, it uses `EliteSelectionEngine` and `PrecisionEntryEngine`, followed by a hard-coded Python array slice (`buys[:10] + watches[:10] + sells[:10]`).
5. **Is RiskReward Engine reused?** **Yes.** It is evaluated inside the `MasterSignalPipeline`.
6. **Is Confidence Calibration reused?** **Yes.** 
7. **Is Position Sizing reused?** **Yes.** It leverages the `TradeExecutionCenter`.

==================================================
## F&O SPECIFIC LOGIC (CRITICAL FINDINGS)
==================================================

> [!WARNING] 
> The audit revealed a severe disconnect between the intended F&O design and the actual implementation in `application/intraday_scanner_service.py`.

**1. Dead Intraday Engine:**
The `IntradayScannerService` natively instantiates `self.intraday_engine = IntradayEngine()` at Line 95. However, this engine is **never actually called** anywhere in the execution loop. 

**2. Hardcoded Non-F&O Universe:**
At Line 144, when the scanner builds the universe array to pass to the scanner, it actively strips F&O context:
`stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=False, is_nifty50=False))`
*(Notice that `is_fno` is hardcoded to `False` for the entire Intraday F&O scanner).*

**3. Ignored Intraday Mode:**
The `execute_intraday_scan` passes `mode="INTRADAY"` into `scanner_engine.py` and `decision_engine.py`. However, neither of those files contains logic for the `"INTRADAY"` string. They only contain specific overrides for `"OPTIONS"`. Because `"INTRADAY"` is not `"OPTIONS"`, the engine falls back to standard `SWING` thresholds.

**Conclusion on Specific Logic:**
Currently, there is **zero** functional F&O, Options, or Intraday specific logic being executed in the Active Scanner. It is evaluating 5m candles using the exact same metrics, thresholds, and engine parameters as a multi-day Swing trade.

==================================================
## OUTPUT DIAGRAM
==================================================
```mermaid
graph TD
    A[Data <br><i>Hardcoded F&O=False</i>] --> B[ScannerEngine <br><i>Defaults to SWING rules</i>]
    B --> C[Core Indicators]
    C --> D[DecisionEngine <br><i>Defaults to SWING thresholds</i>]
    D --> E[MasterSignalPipeline]
    E --> F[InstitutionalValidation / TradeExecutionCenter]
    F --> G[EliteSelectionEngine + PrecisionEntryEngine <br><i>Bypasses TPE</i>]
    G --> H[Inline Truncation <br><i>buys[:10] + ...</i>]
    H --> I[UI <br><i>IntradayScannerPage</i>]
```

==================================================
## FINAL REPORT
==================================================

1. **Current Architecture Score:** **3 / 10**
2. **Strengths:** Heavily reuses the `MasterSignalPipeline` and `ScannerEngine`, ensuring the mathematical baselines for indicator reading and Risk/Reward remain highly consistent with the Swing scanner.
3. **Weaknesses:** Complete bypass of the `TradePriorityEngine`. Hard-coded F&O disqualification (`is_fno=False`). `mode="INTRADAY"` falls through to Swing defaults.
4. **Technical Debt:** `self.intraday_engine = IntradayEngine()` is instantiated but abandoned. The final sorting logic is hardcoded inside the scanner service rather than encapsulated in an engine.
5. **Missing Modules:** Missing VWAP filters, Option Greeks (Delta/OI checks), and Intraday opening range/time-of-day filters in the primary loop.
6. **Highest Priority Improvement:** 
   Wire the `IntradayEngine` back into the main execution loop, correct the `is_fno=True` parameter mapping, and unify the sorting backend by routing it through the recently upgraded `TradePriorityEngine`.
