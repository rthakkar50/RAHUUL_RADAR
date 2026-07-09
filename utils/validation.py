def validate_trade_levels(signal: str, entry: float, stop_loss: float, target: float) -> tuple[bool, str]:
    """
    Centralized helper to validate trade risk levels according to direction.
    """
    signal = (signal or "").upper()

    if entry <= 0 or stop_loss <= 0 or target <= 0:
        return False, "Invalid price level"

    if signal in ("BUY", "STRONG_BUY"):
        if stop_loss >= entry:
            return False, "Invalid BUY setup: stop loss must be below entry"
        if target <= entry:
            return False, "Invalid BUY setup: target must be above entry"

    elif signal in ("SELL", "STRONG_SELL"):
        if stop_loss <= entry:
            return False, "Invalid SELL setup: stop loss must be above entry"
        if target >= entry:
            return False, "Invalid SELL setup: target must be below entry"

    else:
        return True, "Non-directional signal"

    return True, "Valid trade levels"
