# Enterprise Signal Orchestration Architecture

## Overview
RAHUUL_RADAR v6.5.1 introduces the **Enterprise Signal Orchestration Engine**.
Previously, independent engines (Swing, Intraday, High Volume, Breakout) generated signals in silos, occasionally causing conflicts (e.g., `RELIANCE` appearing as a BUY in Swing but a SELL in Intraday).

The Signal Orchestrator sits between the backend decision engines and the API layer, unifying all signals into a clean, conflict-free, prioritized list before they reach the Flutter UI or Paper Trading layers.

## Architecture Flow
```
Market Data
    ↓
[ Swing Engine | Intraday Engine | High Volume Engine | Breakout Engine ]
    ↓
Signal Orchestrator
    ├── Merges all signals
    ├── Routes to Conflict Resolver (removes duplicates)
    ├── Upgrades via Priority Ranking Engine
    ├── Assigns Unified Signal Score
    └── Attaches Explainability
    ↓
Final Qualified Signals
    ↓
API Layer / Caches (Split back to Swing / Intraday routes)
    ↓
Flutter UI
```

## Priority Ranking
Signals are ranked according to enterprise taxonomy. If a setup meets high confidence and decision thresholds, it is upgraded.

1. **INSTITUTIONAL_BUY** (Score > 90, Confidence > 95)
2. **STRONG_BUY** (Score > 80, Confidence > 85)
3. **BUY**
4. **WATCH**
5. **SELL**
6. **STRONG_SELL** (Score > 80, Confidence > 85)
7. **INSTITUTIONAL_SELL** (Score > 90, Confidence > 95)

## Conflict Resolution
If a single symbol receives multiple signals across different engines, the Conflict Resolver picks the winner based on:
1. Higher Confidence
2. Higher Composite Score
3. Higher Risk Reward Ratio

The losing signals are discarded, ensuring a symbol appears only once across the entire platform.

## Unified Signal Score
A composite score (0-100) is calculated for global ranking across all engines:
- Decision Score: 30%
- AI Score: 20%
- Confidence: 20%
- Risk Reward: 10%
- Trend Strength: 10%
- Volume Strength: 10%

## Explainability
Every signal includes a human-readable `Reason` string injected into the payload (mapped to `Pattern` for UI backward compatibility).
*Example:* `BUY because Trend Bullish, Momentum Strong, VWAP Above, Risk Reward 1:2.8, AI Confidence 92%`
