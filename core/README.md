# Adaptive Strategy Engine

The **Adaptive Strategy Engine** is an institutional-grade intelligence layer that dynamically classifies the current market regime and selects the most appropriate trading strategy based on live indicators.

---

## Key Components

### 1. MarketSnapshot
`MarketSnapshot` is a strongly-typed data container (`dataclass`) holding the key technical metrics of the current market state. It acts as the raw input for the engine.

**Fields:**
* `trend_direction` (str): Overall direction of the market trend (`BULL` or `BEAR`).
* `adx` (float): Average Directional Index measuring trend strength.
* `atr` (float): Average True Range measuring market volatility.
* `rsi` (float): Relative Strength Index measuring momentum.
* `price_above_vwap` (bool): Indicates if current price is trading above the Volume Weighted Average Price.
* `volume_ratio` (float): Current volume relative to historical averages.
* `market_breadth` (float): Percentage of advancing stocks vs. declining stocks.
* `sector_strength` (float): Strength score of the underlying sector.
* `relative_strength` (float): Performance comparison score against benchmark indices.
* `option_chain_bias` (str): Bias calculated from Options Open Interest data.

---

### 2. MarketEnvironment
An `Enum` representing the classified market regime after parsing the `MarketSnapshot`.

**Values:**
* `UNKNOWN`: Default fallback / missing data.
* `BULL`: Standard bullish trending market.
* `STRONG_BULL`: Highly trending bullish market.
* `BEAR`: Standard bearish trending market.
* `STRONG_BEAR`: Highly trending bearish market.
* `SIDEWAYS`: Range-bound or neutral market.
* `VOLATILE`: High-range choppy market.
* `LOW_VOLATILITY`: Tight range, dormant market.

---

### 3. StrategyType
An `Enum` representing the selected execution profile recommended for the current environment.

**Values:**
* `SWING`: Multi-day holding setups.
* `INTRADAY`: Same-day entry and exit.
* `SCALPING`: Rapid, micro-target setups.
* `OPTION_SCALPING`: Specific option-buying/selling quick setups.
* `NO_TRADE`: Direct recommendation to sit on cash due to unfavorable risk/reward parameters.

---

## Processing Flow (`evaluate_snapshot`)

The entry point of evaluation is `evaluate_snapshot(snapshot)`. It runs through the following pipeline:

```
  [MarketSnapshot]
         │
         ▼
 1. detect_market_environment() ──► Resolves MarketEnvironment
         │
         ▼
 2. select_strategy()           ──► Resolves StrategyType
         │
         ▼
 3. get_strategy_name()         ──► Maps to User-Friendly Strategy Name
         │
         ▼
  [Return (Tuple)]  ──► (MarketEnvironment, StrategyType, "Strategy Name")
```

### Strategy Mapping Matrix

| Market Environment | Target Strategy | Description / Style |
| :--- | :--- | :--- |
| `STRONG_BULL` | `Intraday Trading` | Day trading high-momentum breakouts. |
| `BULL` | `Swing Trading` | Swing setups buying pullbacks to key EMA levels. |
| `STRONG_BEAR` | `Intraday Trading` | High-momentum day trading shorts. |
| `BEAR` | `Swing Trading` | Swing setups selling rallies in bearish regimes. |
| `VOLATILE` | `Scalping` | Quick scalps with tight SL and short targets. |
| `LOW_VOLATILITY` | `No Trade` | Strict risk management restriction (preserves capital). |
| `SIDEWAYS` | `No Trade` | Restriction to prevent losses in range chop. |
| `UNKNOWN` | `No Trade` | Safe default configuration. |
