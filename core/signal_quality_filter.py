class SignalQualityFilter:
    """
    SPRINT-72.5: AI SIGNAL QUALITY FILTER
    Implements 10 strict rejection filters.
    All filters must pass for a signal to be accepted.
    """
    
    def evaluate(self, symbol, signal, ctx):
        """
        Evaluates a signal against 10 strict quality filters.
        Returns (is_valid: bool, rejection_reasons: list)
        """
        reasons = []
        is_buy = (signal == "BUY")
        is_sell = (signal == "SELL")
        
        if not is_buy and not is_sell:
            return False, ["Invalid Signal Type"]

        # Filter 1: Trend (Price vs 200 EMA)
        price = ctx.get('close_price', 0)
        ema_200 = ctx.get('ema_200', 0)
        if ema_200 > 0:
            if is_buy and price < ema_200:
                reasons.append("Price below 200 EMA (Trend Filter)")
            elif is_sell and price > ema_200:
                reasons.append("Price above 200 EMA (Trend Filter)")

        # Filter 2: Momentum (RSI)
        rsi = ctx.get('rsi', 50)
        if is_buy and not (55 <= rsi <= 70):
            reasons.append(f"RSI {rsi:.1f} outside 55-70 range (Momentum Filter)")
        elif is_sell and not (30 <= rsi <= 45):
            reasons.append(f"RSI {rsi:.1f} outside 30-45 range (Momentum Filter)")

        # Filter 3: ADX
        adx = ctx.get('adx', 0)
        if adx < 25:
            reasons.append(f"ADX {adx:.1f} < 25 (Weak Trend)")

        # Filter 4: Volume
        vol = ctx.get('volume', 0)
        avg_vol = ctx.get('avg_volume', 0)
        if avg_vol > 0 and vol < (1.5 * avg_vol):
            reasons.append(f"Volume < 1.5x Average (Volume Filter)")

        # Filter 5: Risk/Reward
        entry = ctx.get('entry', 0)
        sl = ctx.get('sl', 0)
        t1 = ctx.get('target_1', 0)
        if isinstance(entry, (int, float)) and isinstance(sl, (int, float)) and entry > 0 and sl > 0:
            risk = abs(entry - sl)
            reward = abs(t1 - entry) if isinstance(t1, (int, float)) else 0
            if risk > 0:
                rr = reward / risk
                if rr < 2.0:
                    reasons.append(f"Risk/Reward {rr:.1f} < 2.0")
            else:
                reasons.append("Invalid Risk Parameters")
        else:
            reasons.append("Missing Entry/SL (RR Filter)")

        # Filter 6: ATR Extremes
        atr = ctx.get('atr', 0)
        if price > 0 and atr > 0:
            atr_pct = (atr / price) * 100
            if atr_pct < 0.5:
                reasons.append("Extremely Low Volatility (ATR Filter)")
            elif atr_pct > 7.0:
                reasons.append("Extremely High Volatility (ATR Filter)")
                
        # Filter 7: Market Breadth
        breadth = ctx.get('market_breadth', 'Neutral')
        if is_buy and breadth != 'Bullish':
            reasons.append("Market Breadth not Bullish")
        elif is_sell and breadth != 'Bearish':
            reasons.append("Market Breadth not Bearish")

        # Filter 8: Option Chain Confirmation
        option_sentiment = ctx.get('option_sentiment', 'Neutral')
        if is_buy and option_sentiment != 'Bullish':
            reasons.append("Option Chain not Bullish")
        elif is_sell and option_sentiment != 'Bearish':
            reasons.append("Option Chain not Bearish")

        # Filter 9: Sector Strength (SPRINT-73)
        sector_score = ctx.get('sector_score', 50)
        if is_buy and sector_score < 70:
            reasons.append(f"Sector Score {sector_score} < 70 (Weak Sector)")
        elif is_sell and sector_score > 35:
            reasons.append(f"Sector Score {sector_score} > 35 (Strong Sector)")

        # Filter 10: Signal Agreement (4 out of 5 engines)
        # Engines: Trend, Momentum, Volume, Structure, Master AI
        agreement_count = ctx.get('engine_agreement_count', 0)
        if agreement_count < 4:
            reasons.append(f"Signal Agreement {agreement_count}/5 < 4")

        is_valid = (len(reasons) == 0)
        return is_valid, reasons
