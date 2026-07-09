import pandas as pd
from typing import List
from .models import FilterCondition, FilterOperator

class FilterEngine:
    @staticmethod
    def evaluate(df: pd.DataFrame, conditions: List[FilterCondition]) -> bool:
        if df.empty or not conditions:
            return True
            
        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest
        
        for condition in conditions:
            field = condition.field
            
            # Simple metadata fields (e.g. Sector, MarketCap) might be injected directly as columns 
            # or bypassed if missing. We assume they exist in the enriched DataFrame for now.
            if field not in df.columns:
                # If a field is not available, we conservatively pass it or warn
                continue
                
            val_latest = latest[field]
            val_prev = previous[field]
            target = condition.value
            
            # Allow comparing field against another field (e.g. Close > VWAP)
            if isinstance(target, str) and target in df.columns:
                target_val = latest[target]
                target_prev = previous[target]
            else:
                target_val = target
                target_prev = target
                
            op = condition.operator
            
            try:
                if op == FilterOperator.GREATER_THAN and not (val_latest > target_val): return False
                if op == FilterOperator.LESS_THAN and not (val_latest < target_val): return False
                if op == FilterOperator.EQUAL and not (val_latest == target_val): return False
                if op == FilterOperator.GREATER_EQUAL and not (val_latest >= target_val): return False
                if op == FilterOperator.LESS_EQUAL and not (val_latest <= target_val): return False
                if op == FilterOperator.CONTAINS and str(target_val) not in str(val_latest): return False
                
                if op == FilterOperator.CROSS_ABOVE:
                    if not (val_prev <= target_prev and val_latest > target_val): return False
                    
                if op == FilterOperator.CROSS_BELOW:
                    if not (val_prev >= target_prev and val_latest < target_val): return False
                    
            except TypeError:
                # Handle comparison errors gracefully
                return False
                
        return True
