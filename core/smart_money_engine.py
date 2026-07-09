import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class SmartMoneyEngine:
    """
    MASTER-19: SMART MONEY ENGINE VERSION 1.0
    Detects high-probability institutional footprints based solely on available data.
    Never fakes signals. Never invents data.
    """
    
    def __init__(self):
        pass
        
    def analyze(self, df: pd.DataFrame, market_regime_data: dict, sector_strength: str = "Neutral") -> dict:
        """
        Analyzes a single stock dataframe to detect Smart Money activity.
        df requires: Open, High, Low, Close, Volume, VWAP (if available)
        """
        if df is None or len(df) < 20:
            return self._get_insufficient_result()
            
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Prepare Base Data
            price = latest['Close']
            prev_price = prev['Close']
            volume = latest['Volume']
            prev_volume = prev['Volume']
            
            price_change = ((price - prev_price) / prev_price) * 100
            is_up = price_change > 0
            is_down = price_change < 0
            
            # Need basic indicators if not present
            if 'VWAP' not in df.columns:
                df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
                df['VWAP'] = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
                
            vwap = df['VWAP'].iloc[-1]
            prev_vwap = df['VWAP'].iloc[-2]
            
            # ATR
            df['tr1'] = df['High'] - df['Low']
            df['tr2'] = abs(df['High'] - df['Close'].shift(1))
            df['tr3'] = abs(df['Low'] - df['Close'].shift(1))
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = df['tr'].rolling(14).mean().iloc[-1]
            
            score = 50  # Neutral base score
            
            # =================================================================
            # CHECK-1: RELATIVE VOLUME
            # =================================================================
            vol_5 = df['Volume'].rolling(5).mean().iloc[-1]
            vol_10 = df['Volume'].rolling(10).mean().iloc[-1]
            vol_20 = df['Volume'].rolling(20).mean().iloc[-1]
            
            avg_vol = vol_20
            rvol = volume / avg_vol if avg_vol > 0 else 1.0
            
            if rvol > 3.0:
                rel_vol_status = "Very High"
            elif rvol > 1.5:
                rel_vol_status = "High"
            elif rvol > 0.8:
                rel_vol_status = "Normal"
            else:
                rel_vol_status = "Low"
                
            # =================================================================
            # CHECK-2: DELIVERY QUALITY
            # =================================================================
            # "Never invent institutional activity."
            delivery_status = "NOT AVAILABLE"
            
            # =================================================================
            # CHECK-3: PRICE-VOLUME RELATIONSHIP
            # =================================================================
            vol_up = volume > prev_volume
            
            if is_up and vol_up:
                pv_rel = "Healthy"
                score += 10
            elif is_down and vol_up:
                pv_rel = "Weak"
                score -= 10
            elif is_up and not vol_up:
                pv_rel = "Suspicious"
            elif is_down and not vol_up:
                pv_rel = "Healthy" # Less selling pressure
                score += 5
            else:
                pv_rel = "Neutral"
                
            # =================================================================
            # CHECK-4: ACCUMULATION
            # =================================================================
            price_stable = abs(price_change) < 1.0
            accum_status = "No conclusion."
            
            if price_stable and rel_vol_status in ["High", "Very High"] and close_near_high(latest):
                accum_status = "Possible Accumulation"
                score += 15
                
            # =================================================================
            # CHECK-5: DISTRIBUTION
            # =================================================================
            dist_status = "No conclusion."
            if close_near_low(latest) and rel_vol_status in ["High", "Very High"] and is_down:
                dist_status = "Possible Distribution"
                score -= 20
                
            # =================================================================
            # CHECK-6: ABSORPTION
            # =================================================================
            abs_status = "No conclusion."
            # Detect repeated support / large volume / minimal price movement
            if price_stable and rvol > 2.0 and latest['Low'] >= df['Low'].iloc[-3:].min():
                abs_status = "Possible Absorption"
                score += 10
                
            # =================================================================
            # CHECK-7: UNUSUAL ACTIVITY
            # =================================================================
            unusual = "Not Confirmed"
            if rvol > 3.0 or atr > (df['tr'].rolling(14).mean().iloc[-2] * 2):
                unusual = "Confirmed"
                if is_up: score += 10
                if is_down: score -= 10
                
            # =================================================================
            # CHECK-8: VWAP PARTICIPATION
            # =================================================================
            vwap_status = "Neutral"
            if price > vwap and vwap > prev_vwap:
                vwap_status = "Supported"
                score += 10
            elif price < vwap and vwap < prev_vwap:
                vwap_status = "Rejected"
                score -= 10
                
            # =================================================================
            # CHECK-9: SECTOR CONFIRMATION
            # =================================================================
            sect_status = "Confirmed" if sector_strength == "Strong" else ("Weak" if sector_strength == "Weak" else "Neutral")
            if sect_status == "Strong": score += 5
            
            # =================================================================
            # CHECK-10: MARKET CONFIRMATION
            # =================================================================
            market_reg = market_regime_data.get("Market Regime", "UNKNOWN")
            if market_reg in ["STRONG BULL TREND", "BULL TREND"]:
                if score > 50: score += 5 # Market confirms accumulation
            elif market_reg in ["STRONG BEAR TREND", "BEAR TREND"]:
                if score > 50: score -= 15 # Market rejects accumulation

            # =================================================================
            # FINAL SCORING & CLASSIFICATION
            # =================================================================
            score = max(0, min(100, score))
            
            if score >= 90:
                classification = "Strong Institutional Footprint"
                evidence = "Strong Evidence"
            elif score >= 80:
                classification = "Possible Institutional Activity"
                evidence = "Moderate Evidence"
            elif score <= 20:
                classification = "Strong Distribution Footprint"
                evidence = "Strong Evidence"
            elif score <= 40:
                classification = "Possible Distribution"
                evidence = "Moderate Evidence"
            elif 40 < score < 70:
                classification = "Insufficient Evidence"
                evidence = "Weak Evidence"
            else:
                classification = "Neutral"
                evidence = "Weak Evidence"
                
            return {
                "Smart Money Score": score,
                "Relative Volume": rel_vol_status,
                "Delivery Status": delivery_status,
                "Accumulation Status": accum_status,
                "Distribution Status": dist_status,
                "VWAP Status": vwap_status,
                "Sector Confirmation": sect_status,
                "Evidence Level": evidence,
                "Classification": classification
            }
            
        except Exception as e:
            logger.error(f"Error in SME: {e}")
            return self._get_insufficient_result()
            
    def _get_insufficient_result(self):
        return {
            "Smart Money Score": 50,
            "Relative Volume": "NOT AVAILABLE",
            "Delivery Status": "NOT AVAILABLE",
            "Accumulation Status": "No conclusion.",
            "Distribution Status": "No conclusion.",
            "VWAP Status": "NOT AVAILABLE",
            "Sector Confirmation": "NOT AVAILABLE",
            "Evidence Level": "Insufficient Evidence",
            "Classification": "INSUFFICIENT EVIDENCE"
        }

def close_near_high(row):
    body = abs(row['Close'] - row['Open'])
    range_ = row['High'] - row['Low']
    if range_ == 0: return False
    return (row['High'] - row['Close']) / range_ < 0.25

def close_near_low(row):
    range_ = row['High'] - row['Low']
    if range_ == 0: return False
    return (row['Close'] - row['Low']) / range_ < 0.25
