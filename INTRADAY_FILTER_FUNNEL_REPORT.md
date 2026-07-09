# INTRADAY FILTER FUNNEL REPORT (SPRINT-35)

**MISSION:** Deep pipeline inspection across 20 stages of the Intraday Scanner to identify exact points of rejection.

====================================================
### FUNNEL ANALYSIS
====================================================

**1. Symbol Loader**
Input: 178 | Passed: 178 | Rejected: 0 | Rejection: 0.0%
↓
**2. Data Availability**
Input: 178 | Passed: 174 | Rejected: 4 | Rejection: 2.2%
*Reason: No OHLCV data returned (e.g. GMRINFRA, LTIM, PEL, TATAMOTORS)*
↓
**3. Trend Engine**
Input: 174 | Passed: 111 | Rejected: 63 | Rejection: 36.2%
*Reason: Trend Score < 15 (Directionally Sideways or No Consensus)*
↓
**4. Volume Engine**
Input: 111 | Passed: 104 | Rejected: 7 | Rejection: 6.3%
*Reason: Insufficient Intraday Volume (< 50,000)*
↓
**5. Momentum Engine**
Input: 104 | Passed: 78 | Rejected: 26 | Rejection: 25.0%
*Reason: Momentum Score < 15 (No RSI/MACD alignment)*
↓
**6. ADX Filter**
Input: 78 | Passed: 51 | Rejected: 27 | Rejection: 34.6%
*Reason: ADX < 20 (Weak Trend, Low Conviction)*
↓
**7. Anchored VWAP**
Input: 51 | Passed: 51 | Rejected: 0 | Rejection: 0.0%
*Reason: All passed structural AVWAP positioning.*
↓
**8. Smart Money Engine**
Input: 51 | Passed: 46 | Rejected: 5 | Rejection: 9.8%
*Reason: Failed institutional volume surge criteria.*
↓
**9. Relative Strength**
Input: 46 | Passed: 46 | Rejected: 0 | Rejection: 0.0%
*Reason: Core RS engine did not hard-reject.*
↓
**10. Sector Strength**
Input: 46 | Passed: 46 | Rejected: 0 | Rejection: 0.0%
*Reason: Sector alignment was sufficient.*
↓
**11. AI Score**
Input: 46 | Passed: 46 | Rejected: 0 | Rejection: 0.0%
*Reason: Base score naturally remained >= 60 after surviving upstream technicals.*
↓
**12. Confidence**
Input: 46 | Passed: 1 | Rejected: 45 | Rejection: 97.8%
*Reason: Confidence < 60%. (Driven by MTF Multi-Timeframe Conflict where 1H/4H/Daily do not perfectly align, causing heavy MTF Confidence penalties)*
↓
**13. Trade Quality Index (TQI)**
Input: 1 | Passed: 0 | Rejected: 1 | Rejection: 100.0%
*Reason: TQI < 85. The single remaining trade did not have the explosive combination of Score, Confidence, Volume, and RR needed to cross the Elite TQI threshold.*
↓
**14. Risk Reward**
Input: 0 | Passed: 0 | Rejected: 0 | Rejection: 0.0%
↓
**15. Institutional Validation**
Input: 0 | Passed: 0 | Rejected: 0 | Rejection: 0.0%
↓
**16. Capital Protection**
Input: 0 | Passed: 0 | Rejected: 0 | Rejection: 0.0%
↓
**17. Elite Selection**
Input: 0 | Passed: 0 | Rejected: 0 | Rejection: 0.0%
↓
**18. Execution Readiness**
Input: 0 | Passed: 0 | Rejected: 0 | Rejection: 0.0%
↓
**19. Final BUY**
0
↓
**20. Final SELL**
0

====================================================
### FINAL ANALYSIS
====================================================

**Top 5 Rejection Filters**
1. **Trend Engine:** 63 rejections
2. **Confidence (MTF Conflict):** 45 rejections
3. **ADX Filter:** 27 rejections
4. **Momentum Engine:** 26 rejections
5. **Volume Engine:** 7 rejections

====================================================
### FINAL VERDICT
====================================================
**A) System behaving correctly**

The strict filtering is mathematically working exactly as designed for Intraday V1.0 rules. The pipeline systematically clears out sideways/low-momentum stocks early (Trend/ADX), and then the **Confidence engine** acts as a heavy institutional gatekeeper by rejecting 97.8% of surviving setups due to Multi-Timeframe (MTF) conflicts. The system protects capital by refusing to trade unless everything perfectly aligns.
