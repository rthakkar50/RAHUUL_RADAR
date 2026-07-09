# INTRADAY FILTER FUNNEL AUDIT

This funnel tracks how 178 symbols were filtered down through the strict Intraday Scanner pipeline.

### Loaded Symbols
**Total: 178**
↓
### Passed Trend Engine
*(Score > 50 or Base Signal BUY/SELL)*
**Passed: 5** | Rejected: 173 | Pass Rate: 2.8%
↓
### Passed AI Score
*(Score >= 60)*
**Passed: 4** | Rejected: 1 | Pass Rate: 80.0%
↓
### Passed Confidence
*(Confidence >= 60)*
**Passed: 0** | Rejected: 4 | Pass Rate: 0.0%
↓
### Passed Risk Reward
*(Risk/Reward >= 1:2.0)*
**Passed: 0** | Rejected: 0 | Pass Rate: 0.0%
↓
### Passed TQI
*(Trade Quality Index >= 85)*
**Passed: 0** | Rejected: 0 | Pass Rate: 0.0%
↓
### Passed Institutional Validation
*(Market Regime & False Signal Check)*
**Passed: 0** | Rejected: 0 | Pass Rate: 0.0%
↓
### Passed Capital Protection
*(Trade Execution Risk Check)*
**Passed: 0** | Rejected: 0 | Pass Rate: 0.0%
↓
### Passed Elite Selection
*(Final Tier Grades)*
**Passed: 0** | Rejected: 0 | Pass Rate: 0.0%
↓
### Final Result
**Final BUY: 0**
**Final SELL: 0**

---

**Summary:**
The strict intraday conditions immediately rejected the vast majority of symbols due to poor directional trend (173 rejected at the Trend Engine). The remaining 5 symbols were blocked because they failed to meet the minimum threshold of **60% Confidence** during Elite Selection. 

As a result, no trades were allowed through the pipeline, keeping capital perfectly protected in a low-probability environment.
