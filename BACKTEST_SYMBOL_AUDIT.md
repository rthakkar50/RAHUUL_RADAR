# BACKTEST SYMBOL LOADER AUDIT
**Objective:** Audit the Symbol Loader inside the Backtest Engine to verify the behavior of the "Top 50 NSE" selection.

---

### 1. Which symbols are loaded when "Top 50 NSE" is selected?
Only **10 specific large-cap stocks** are actually loaded. The system does not load 50 stocks.

### 2. Complete list of loaded symbols
1. `HDFCBANK.NS`
2. `ICICIBANK.NS`
3. `SBIN.NS`
4. `RELIANCE.NS`
5. `INFY.NS`
6. `TCS.NS`
7. `ITC.NS`
8. `LNT.NS`
9. `AXISBANK.NS`
10. `KOTAKBANK.NS`

### 3. How many symbols are loaded?
Exactly **10 symbols**.

### 4. Which file provides the Top 50 list?
The list is not provided by an external data file or a dynamic symbol fetcher. 
It is **hardcoded directly in the frontend UI file**:
**File:** `/Users/pr/RAHUUL_RADAR/ui/backtest.py`
**Line 167:**
```python
symbols = ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "RELIANCE.NS", "INFY.NS", "TCS.NS", "ITC.NS", "LNT.NS", "AXISBANK.NS", "KOTAKBANK.NS"] if self.chk_top50.isChecked() else ["RELIANCE.NS", "TCS.NS"]
```

### 5. Is the GUI hiding the loaded symbols?
**Yes.** 
The GUI displays a simple checkbox labeled `"Top 50 NSE"`, strongly implying that 50 symbols will be tested. However, clicking the `Run Backtest` button silently injects the hardcoded array of 10 symbols. There is no visual indicator or tooltip in the UI revealing that only 10 symbols are actually being processed.

### 6. Verify that the backtest actually runs on these symbols
**Verified.**
When the user clicks `Run Backtest`, the hardcoded array of 10 symbols is passed directly into the `BacktestWrapperThread` (Line 173 of `ui/backtest.py`):
```python
self.engine = BacktestWrapperThread(symbols, start, end, hold_days)
```
The thread then passes this array directly to the core `BacktestEngine.run_backtest(self.symbols, ...)` method. No additional symbol expansion, mapping, or dynamic universe fetching occurs. The backtest exclusively runs on these 10 symbols.
