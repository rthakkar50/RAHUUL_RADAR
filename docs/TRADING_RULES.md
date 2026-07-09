# RAHUUL AI Trading Rules

## Philosophy
**The system never predicts.**
The system only reacts to confirmed market conditions. We do not attempt to catch bottoms or short tops. We identify where institutional capital is flowing, wait for mathematical alignment across multiple technical engines, and execute with calculated precision.

---

## Rule 1 : Market Direction
The foundational filter for all trades. The system must align with the broader market.
- **Conditions for Bullish Market**: NIFTY is trading above its primary moving averages (EMA20 > EMA50) with expanding volume. Sector breadth is positive.
- **Conditions for Bearish Market**: NIFTY is trading below its primary moving averages (EMA20 < EMA50) with sustained downside momentum. Sector breadth is negative.
- **Conditions for Neutral Market**: NIFTY is ranging between key support and resistance zones. Moving averages are flat. Position sizing is halved or trading is paused.

## Rule 2 : Sector Strength
Capital flows through sectors before hitting individual stocks. Trades are only executed in the direction of the sector's trend.
- **How to identify strong sectors**: The sector index is heavily outperforming the benchmark index. It exhibits a clear series of Higher Highs (HH) and Higher Lows (HL) with high relative volume.
- **How to identify weak sectors**: The sector index is underperforming the benchmark index. It exhibits Lower Highs (LH) and Lower Lows (LL) with heavy distribution volume.

## Rule 3 : Trend Rules
Trend dictates the directional bias of the individual stock.
- **EMA20**: Acts as the primary dynamic support/resistance. The slope of the EMA20 must physically point in the trade direction.
- **EMA50**: Acts as the baseline trend filter. For long setups, EMA20 must remain strictly > EMA50.
- **VWAP**: Intraday anchor point. Longs are only initiated when the price is > VWAP; shorts only when the price is < VWAP.
- **Higher Timeframe Alignment**: The trend on the execution timeframe must be validated and confirmed by the trend on the next immediate higher timeframe.

## Rule 4 : Momentum Rules
Momentum dictates the speed and validity of the move.
- **RSI**: Must show expansion without immediate bearish divergence. For longs, RSI must hold above 50. For shorts, RSI must hold below 50.
- **ADX**: Trend strength must be confirmed. ADX should ideally be rising and > 20 to indicate a trending environment.
- **Momentum Confirmation**: Breakout price action must be accompanied by expanding momentum oscillators. Lagging momentum invalidates the setup.

## Rule 5 : Structure Rules
Structure dictates the market context and trap zones.
- **Higher High (HH)**: A peak higher than the previous peak.
- **Higher Low (HL)**: A trough higher than the previous trough. Required for all long entries.
- **Lower High (LH)**: A peak lower than the previous peak.
- **Lower Low (LL)**: A trough lower than the previous trough. Required for all short entries.
- **Break of Structure (BOS)**: A confirmed candle close past a previous swing point in the direction of the trend. Validates continuation.
- **Fake Breakout**: A sweep of a key level followed by an immediate rejection back into the range. Disqualifies continuation trades.
- **Liquidity Sweep**: Price dipping below a swing low (or above a swing high) strictly to trigger stops before reversing. A strong reversal signal.

## Rule 6 : Volume Rules
Volume is the footprint of institutional participation.
- **Relative Volume (RVOL)**: Must be > 1.2 on entry candles to confirm active participation.
- **Volume Expansion**: Up-candles must possess higher volume than down-candles in a bullish trend (and vice versa for bearish trends).
- **Volume Confirmation**: Breakouts must occur on expanding volume. A breakout on average or low volume is flagged as a high-risk trap.

## Rule 7 : Relative Strength Rules
- **Compare stock strength against NIFTY**: The stock must display a positive Relative Strength (RS) line against the NIFTY index. A stock making new highs while NIFTY consolidates is mathematically flagged as an 'A' grade setup.

## Rule 8 : Risk Rules
Capital preservation is the ultimate directive.
- **Minimum Risk Reward**: Every trade must mathematically offer a minimum of 1:2 Risk-Reward (RR) ratio to the first logical structure target.
- **Maximum Daily Risk**: The system halts trading if a predefined percentage of the total portfolio is lost in a single session.
- **Position Sizing**: Calculated dynamically based on the distance from the entry to the technical stop loss. Fixed fractional risk per trade.

## Rule 9 : Entry Rules
- **Conditions before BUY**: Bullish Market + Strong Sector + Bullish Trend (EMA/VWAP) + Bullish Structure + Favorable Risk/Reward + Expanding Volume.
- **Conditions before SELL**: Bearish Market + Weak Sector + Bearish Trend + Bearish Structure + Favorable Risk/Reward + Expanding Volume.
- **Conditions before BUY CE**: Same conditions as BUY, but specifically mandates high ADX and expanding volatility to combat options Theta decay.
- **Conditions before BUY PE**: Same conditions as SELL, but mandates expanding volatility and swift downside momentum structure.

## Rule 10 : Exit Rules
- **Target**: Pre-defined structure levels, liquidity pools, or Fibonacci extensions.
- **Stop Loss**: Placed strictly beyond the most recent validated swing high/low or major EMA cluster.
- **Trailing Stop**: Activated once the trade reaches 1:1 RR. Trails dynamically using the EMA20 or previous candle extremes.
- **Momentum Exit**: Immediate exit triggered if ADX drops sharply or RSI prints a hard divergence against the open position.
- **Structure Exit**: Immediate exit triggered if the market prints a confirmed Change of Character (CHoCH) against the position.

## Rule 11 : No Trade Rules
The system explicitly forbids trading under the following conditions:
- **Low Volume**: Relative volume is stagnant; low liquidity increases slippage.
- **Sideways Market**: ADX < 20, moving averages are flat, horizontal, and intertwined.
- **High Volatility**: Erratic price swings that distort valid structure and mandate impossibly wide stop losses.
- **News Events**: 15 minutes before and after major macroeconomic data releases or earnings.
- **Gap Opening**: If a stock gaps heavily past its intended target or fundamentally alters structure at the open, the setup is abandoned.

## Rule 12 : Scanner Rules
- **Ranking Rules**: Stocks are mathematically ranked based on the aggregated score from all technical engines (Total Score = 100).
- **Confidence Rules**: Only setups scoring 80+ (`BUY`) or 90+ (`STRONG_BUY`) are executed or forwarded to the user.
- **Priority Rules**: A `STRONG_BUY` signal in a top-performing sector takes absolute algorithmic priority over a `STRONG_BUY` in a lagging sector.

## Rule 13 : Dashboard Rules
- **Explain every score**: The dashboard must transparently break down the exact point allocation (e.g., Trend: 25/25, Momentum: 15/20) for immediate user verification.
- **Explain every recommendation**: Signals must be paired with clear, readable logic (e.g., "STRONG_BUY: Aligning Trend, High RVOL, BOS Confirmed").

## Rule 14 : AI Coach Rules
- **Explain WHY a trade exists**: The AI Coach must articulate the mechanical, technical, and structural reasoning behind every generated signal.
- **Never give unexplained signals**: Trust requires transparency. The AI must actively refuse to output a trade idea that cannot be mathematically validated by the core engines.

---

### Future Expansion
This rulebook is designed as a living architecture. Future expansions will integrate dynamic options Greek evaluation, automated macroeconomic sentiment scraping, and advanced volume profile algorithms into the core engine logic without violating the fundamental philosophy: **We react. We do not predict.**
