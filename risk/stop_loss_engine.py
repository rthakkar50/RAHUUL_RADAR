class StopLossEngine:
    @staticmethod
    def calculate_atr_sl(entry_price: float, atr: float, multiplier: float = 1.5) -> float:
        """
        Calculates Stop Loss based on Average True Range.
        """
        return entry_price - (atr * multiplier)

    @staticmethod
    def calculate_structure_sl(entry_price: float, swing_low: float, buffer_pct: float = 0.2) -> float:
        """
        Calculates Stop Loss based on the most recent structural swing low with a safety buffer.
        """
        buffer_amount = entry_price * (buffer_pct / 100.0)
        return swing_low - buffer_amount
