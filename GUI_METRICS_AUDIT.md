# GUI METRICS PARITY AUDIT
**Objective:** Identify discrepancies between the GUI displayed metrics and the Backtest Engine / Trade Evaluator outputs.

---

## 1. Why BUY Win Rate is always 0%
* **Exact File:** `backtest/engine_wrapper.py`
* **Exact Function:** `StdoutRedirector.write()`
* **Exact Calculation/Regex:** 
  ```python
  if "BUY Win Rate:" in message:
      match = re.search(r'BUY Win Rate:\s*([\d\.]+)%', message)
  ```
* **Root Cause:** The `TradeEvaluator` (in `backtest/trade_evaluator.py`, `_generate_summary()` line 254) prints the string with **two spaces** for alignment: 
  ```python
  print(f"BUY  Win Rate: {wr_b:.2f}% ...")
  ```
  Because the GUI redirector searches for `"BUY Win Rate:"` (one space), the condition `if "BUY Win Rate:" in message` always returns `False`. The regex is never evaluated, leaving the variable at its initialized state of `0.0`.

---

## 2. Average Return calculation always 0%
* **Exact File:** `backtest/engine_wrapper.py`
* **Exact Function:** `StdoutRedirector.write()`
* **Exact Calculation/Regex:**
  ```python
  elif "Average Return:" in message and "BUY" not in message and "SELL" not in message:
  ```
* **Root Cause:** The `TradeEvaluator` (line 249) prints:
  ```python
  print(f"Average Return / Trade: {avg_all:.2f}%")
  ```
  The literal string `"Average Return:"` (with a colon) does not exist in `"Average Return / Trade: "`. Therefore, the `in message` check fails, and the regex is never triggered.

---

## 3. Execution Time calculation always 0s
* **Exact File:** `backtest/engine_wrapper.py`
* **Exact Function:** `StdoutRedirector.write()`
* **Exact Calculation/Regex:**
  ```python
  elif "Execution Time:" in message:
      match = re.search(r'Execution Time:\s*([\d\.]+)', message)
  ```
* **Root Cause:** The `TradeEvaluator` does not compute or print `"Execution Time:"` at all in its output. The GUI expects a metric that the backend never provides.

---

## 4. Metrics That ARE Working Properly
* **SELL Win Rate:** 
  GUI checks for `"SELL Win Rate:"` -> Evaluator prints `"SELL Win Rate:"`. (Match!)
* **Overall Win Rate:** 
  GUI checks for `"Overall Win Rate:"` -> Evaluator prints `"Overall Win Rate:  X%"`. (Match!)
* **Profit Factor:** 
  GUI checks for `"Profit Factor:"` -> Evaluator prints `"Overall Profit Factor: X"`. (Match!)

---

## 5. Answers to General Audit Questions
**Q: Is the GUI reading the correct TradeEvaluator results?**
Yes, `BacktestWrapperThread` properly invokes `TradeEvaluator.evaluate()` and successfully redirects `sys.stdout`.

**Q: Is the GUI reading stale or cached variables?**
No, it correctly resets defaults to 0 on every run inside `StdoutRedirector.__init__()`. The metrics remain 0 because the string parsing fails, not because of caching.

**Q: Verify every displayed metric against the exported CSV.**
The underlying CSV (`exports/simulated_trades_*.csv`) contains all correct `Win / Loss` strings and `Return %` calculations. The backend math is fully accurate. The bugs exist **strictly in the string-matching regex bridge** between `TradeEvaluator` and the PyQt6 GUI.

---
### Audit Conclusion
The Backtest GUI metrics parity issues are purely superficial UI-layer parsing bugs. The underlying backtest trading logic and exported CSVs are 100% accurate. 
**Required Fix:** Update the `in message` checks and regex patterns in `engine_wrapper.py` to match the exact string formats outputted by `trade_evaluator.py`.
