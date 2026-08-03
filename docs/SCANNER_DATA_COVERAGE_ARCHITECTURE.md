# SCANNER DATA COVERAGE & API METRICS RECONCILIATION ARCHITECTURE

## Overview: SPRINT-165 Metrics Transparency

In RAHUUL_RADAR Enterprise Platform v6.4.3, the API response exposes distinct, un-mixed metrics to eliminate confusion between filter rejections and off-market data skips.

```json
{
    "total_universe": 200,
    "total_scanned": 37,
    "qualified_count": 20,
    "filter_rejected_count": 17,
    "no_data_count": 163,
    "buy_count": 10,
    "watch_count": 10,
    "sell_count": 0,
    "rejected_count": 180
}
```

---

## 1. Metric Definition & Tooltip Breakdown

### A. `filter_rejected_count`
- **Definition:** Symbols successfully scanned with valid live market candles that were evaluated by the scanner engine but rejected by one or more of the 7 quantitative filter stages (Trend Filter, Momentum Filter, Structure Gate, Risk Gate, AI Engine, Decision Engine).
- **Formula:**  
  $$\text{filter\_rejected\_count} = \text{total\_scanned} - \text{qualified\_count}$$  
  $$\text{Example: } 37 - 20 = 17$$

### B. `no_data_count`
- **Definition:** Symbols in the configured universe skipped because valid live market tick/candle data was unavailable (e.g., during off-market hours or weekend market closure). These symbols were never scanned by the engine.
- **Formula:**  
  $$\text{no\_data\_count} = \text{total\_universe} - \text{total\_scanned}$$  
  $$\text{Example: } 200 - 37 = 163$$

### C. `rejected_count` (Backward Compatibility Field)
- **Definition:** Total universe symbols not in active trading signals (combining filter rejections and data skips for legacy mobile clients).
- **Formula:**  
  $$\text{rejected\_count} = \text{filter\_rejected\_count} + \text{no\_data\_count}$$  
  $$\text{Example: } 17 + 163 = 180$$

---

## 2. Fundamental Reconciled Identity

$$\text{total\_universe} = \text{qualified\_count} + \text{filter\_rejected\_count} + \text{no\_data\_count}$$

$$\text{Example: } 200 = 20 + 17 + 163$$

---

## 3. Metric Reconciliation Matrix

| Field Name | Formula | Example Value | Description |
| :--- | :--- | :---: | :--- |
| `total_universe` | Target NIFTY Universe | `200` | Full configured universe. |
| `total_scanned` | Downloaded Live Data Symbols | `37` | Symbols with active live market candles. |
| `qualified_count` | `buy_count + watch_count + sell_count` | `20` | Passed 7-stage filters (10 BUY + 10 WATCH). |
| `filter_rejected_count` | `total_scanned - qualified_count` | `17` | Scanned symbols rejected by quantitative filters. |
| `no_data_count` | `total_universe - total_scanned` | `163` | Symbols skipped due to off-market data unavailability. |
| `rejected_count` | `filter_rejected_count + no_data_count` | `180` | Legacy field for backward compatibility. |

---

## Conclusion

This reconciliation guarantees 100% mathematical integrity and clear visibility across both API payloads and Flutter dashboard displays.
