# RAHUUL RADAR PRO - Agent Guidelines

## ARCHITECTURE FREEZE (CRITICAL)

**The Trading Logic is LOCKED and completely READ-ONLY.**

You must NEVER modify, rewrite, or alter any files inside the following directories:
- `core/`
- `engines/`
- `ranking/`
- `scanner/` (specifically the scanner engines)

**Why?**
The core trading logic (Trend Engine, Momentum Engine, Volume Engine, Structure Engine, Risk Engine, Confidence Engine, Institution Engine, Master AI, Entry, Stop Loss, Targets) has been strictly audited and frozen. Modifying these layers to fix UI bugs causes catastrophic regressions (e.g., missing SELL signals, artificially capped confidences).

**How to Handle UI / Data Display Tasks:**
If you need to fix a bug in the UI, layout, panels, menus, export functionalities, or charts:
1. Make all changes strictly in the **Application Layer** (e.g., `application/`) or the **UI Layer** (`ui/`).
2. Treat the output of the Trading Engines as absolute truth. Do not filter out signals forcefully or overwrite engine values (like Trend state or Confidence percentages) just to satisfy UI constraints.
3. Map the data cleanly without affecting the underlying algorithms.

For Trading Software, this strict separation of concerns (Core Engine vs. Display Application) is the most secure development pattern.
