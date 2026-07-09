# INTRADAY RULE PARITY AUDIT

**CONCLUSION:**
**A) Intraday has its own optimized thresholds.**

The Intraday Scanner does **not** use the exact same filtering logic as the Swing Scanner. The architectures diverge significantly in the post-scan filtering stage. While both use the same base data from `ScannerEngine` and `MasterSignalPipeline`, the Swing Scanner applies hardcoded fallback thresholds and uses the `DecisionExplanationEngine`, whereas the Intraday Scanner routes trades through a much stricter institutional pipeline including the `EliteSelectionEngine`, `InstitutionalValidationEngine`, and `TradeExecutionCenter`.

Here is the exact comparison of the rules applied:

### 1. ADX Threshold
- **Swing Threshold:** Handled centrally by `MasterSignalPipeline`.
- **Intraday Threshold:** Handled centrally by `MasterSignalPipeline`.
- **Parity Status:** **IDENTICAL**. Neither scanner overrides the base ADX rules.

### 2. AI Confidence & Score Threshold
- **Swing Threshold:** `if score < 70.0 and conf < 70.0: continue`
  - *Logic:* The trade is rejected only if BOTH Score and Confidence are below 70. (e.g., Score 50, Confidence 75 = PASS).
- **Intraday Threshold:** `if score < 60 or conf < 60: return None` (via `EliteSelectionEngine`)
  - *Logic:* The trade is rejected if EITHER Score or Confidence is below 60. (e.g., Score 50, Confidence 75 = REJECT).
- **Parity Status:** **DIFFERENT**. Intraday is stricter on requiring balance (both metrics >= 60).

### 3. TQI (Trade Quality Index) Threshold
- **Swing Threshold:** N/A (Bypassed entirely).
- **Intraday Threshold:** Minimum TQI of **85** required. (via `EliteSelectionEngine`). If TQI < 85, the trade is rejected.
- **Parity Status:** **DIFFERENT**. Swing does not calculate or filter by TQI.

### 4. Market Regime Filter
- **Swing Threshold:** Only uses basic `MarketState` (Bullish/Bearish bonus). Bypasses the strict `InstitutionalValidationEngine`.
- **Intraday Threshold:** Explicitly routes every trade through `InstitutionalValidationEngine`, which utilizes full `MarketRegimeEngine` logic.
- **Parity Status:** **DIFFERENT**. Intraday applies institutional-grade regime validation; Swing applies a simple score bonus.

### 5. Capital Protection Filter
- **Swing Threshold:** N/A (Bypassed).
- **Intraday Threshold:** Explicitly routed through `TradeExecutionCenter.perform_risk_check` which can dynamically block trades based on system risk/regime.
- **Parity Status:** **DIFFERENT**. Swing does not use the Trade Execution Center.

### 6. Elite Selection Filter
- **Swing Threshold:** Bypassed. Swing uses `TradePriorityEngine` to sort, but does not use Elite Selection to gate trades.
- **Intraday Threshold:** Mandatory. Every trade must pass `EliteSelectionEngine` (generating Grades like "PREMIUM", "ELITE") and then pass `PrecisionEntryEngine`.
- **Parity Status:** **DIFFERENT**.

### 7. Risk/Reward Filter
- **Swing Threshold:** Minimum RR **1:1.5** (Hardcoded default in `swing_scanner_service.py`: `rr < 1.5`).
- **Intraday Threshold:** Minimum RR **1:2.0** (Hardcoded inside `EliteSelectionEngine`: `rr_val < 2.0`).
- **Parity Status:** **DIFFERENT**. Intraday demands a much higher asymmetric payoff to cover intraday noise.

---
**Summary of Architecture:**
The Intraday Scanner uses its own dedicated configuration via `EliteSelectionEngine` and `InstitutionalValidationEngine`, making it mathematically much stricter than the Swing Scanner.
