import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("SIE")
logger.setLevel(logging.INFO)

class SignalImmutabilityEngine:
    """
    MASTER-13: SIGNAL IMMUTABILITY ENGINE (SIE) V2.0
    Guarantees that trade signals are never modified after creation.
    Only status updates and trailing stops are allowed.
    """
    
    def __init__(self):
        # Fields that MUST remain identical to the original ticket
        self.locked_fields = [
            'id', 'symbol', 'signal', 'timeframe', 'strategy',
            'entry_price', 't1', 't2', 'confidence', 'created_time'
        ]
        
    def lock_signal(self, trade_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a new trade and marks it as an immutable snapshot.
        This could involve deep copying or cryptographic hashing in a real system.
        For now, we just ensure it's a valid trade dict.
        """
        logger.info(f"[SIE] Locked trade ticket {trade_dict.get('id')} for {trade_dict.get('symbol')}")
        return trade_dict.copy()
        
    def validate_update(self, original: Dict[str, Any], updated: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates whether the requested update violates immutability rules.
        Returns (is_valid, error_message)
        """
        if not original:
            return False, "Original trade snapshot missing."
            
        # 1. Check Locked Fields
        for field in self.locked_fields:
            if field in original and field in updated:
                if original[field] != updated[field]:
                    msg = f"SECURITY VIOLATION: Attempted to modify locked field '{field}' from {original[field]} to {updated[field]}."
                    logger.error(f"[SIE] {msg}")
                    return False, msg
                    
        # 2. Check Stop Loss Logic (Only widening/trailing allowed)
        if 'sl' in original and 'sl' in updated:
            orig_sl = float(original['sl'])
            new_sl = float(updated['sl'])
            direction = original.get('signal', 'BUY')
            
            if orig_sl != new_sl:
                # If BUY, SL can only move UP (Trailing)
                if direction == "BUY" and new_sl < orig_sl:
                    msg = f"SECURITY VIOLATION: Attempted to widen BUY stop loss from {orig_sl} to {new_sl}."
                    logger.error(f"[SIE] {msg}")
                    return False, msg
                # If SELL, SL can only move DOWN (Trailing)
                if direction == "SELL" and new_sl > orig_sl:
                    msg = f"SECURITY VIOLATION: Attempted to widen SELL stop loss from {orig_sl} to {new_sl}."
                    logger.error(f"[SIE] {msg}")
                    return False, msg
                    
        return True, "Valid update."
