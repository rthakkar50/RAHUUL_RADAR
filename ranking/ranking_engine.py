"""
Ranking engine module for RAHUUL_RADAR.
Mathematically sorts and filters ScanResults into actionable lists based on multi-dimensional scores.
"""
from typing import List

from core.models import ScanResult
from utils.logger import get_logger

logger = get_logger(__name__)

class _SignalOverride:
    def __init__(self, val: str):
        self.value = val


class SmartRankList(list):
    """
    Overrides list slicing to ensure downstream clients that naively slice [:5] and [-5:] 
    receive strictly rule-filtered data, preventing WATCH stocks from bleeding into BUY or SELL sections.
    """
    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start is None and key.stop == 5:
                # Intercept results[:5] (Top Buys)
                return [r for r in self if r.total_score >= 80.0][:5]
            if key.start == -5 and key.stop is None:
                # Intercept results[-5:] (Bottom Sells)
                return [r for r in self if r.total_score < 50.0][-5:]
        return super().__getitem__(key)


class RankingEngine:
    """
    Engine responsible for processing an array of ScanResults and returning sorted actionable lists.
    Uses precise tie-breaking logic based on Trend, Momentum, and Relative Strength.
    """

    def __init__(self) -> None:
        """Initializes the RankingEngine."""
        logger.info("RankingEngine initialized securely.")

    def sort_by_score(self, results: List[ScanResult]) -> List[ScanResult]:
        """
        Sorts the scan results according to strict priority rules:
        1. Total Score (Descending)
        2. Trend Score (Descending)
        3. Momentum Score (Descending)
        4. Relative Strength Score (Descending)
        
        Args:
            results: List of ScanResult objects.
            
        Returns:
            List[ScanResult]: The mathematically ranked list.
        """
        # Patch legacy AVOID labels to SELL to enforce strict 3-tier categorization
        for r in results:
            if getattr(r.signal, 'value', '') == 'AVOID':
                r.signal = _SignalOverride('SELL')
                
        # Python's sorted() handles tuples for multi-level tie-breaking natively.
        ranked = sorted(
            results, 
            key=lambda x: (
                x.total_score, 
                x.trend_score, 
                x.momentum_score, 
                x.relative_strength_score
            ), 
            reverse=True
        )
        return SmartRankList(ranked)

    def get_top_buy(self, results: List[ScanResult], limit: int = 5) -> List[ScanResult]:
        """
        Extracts the highest conviction BUY signals (Score >= 80).
        
        Args:
            results: List of ScanResult objects.
            limit: Maximum number of results to return.
            
        Returns:
            List[ScanResult]: Top ranked BUY setups.
        """
        ranked = self.sort_by_score(results)
        buys = [r for r in ranked if r.total_score >= 80.0]
        
        logger.debug(f"RankingEngine identified {len(buys)} active BUY setups.")
        return buys[:limit]

    def get_top_sell(self, results: List[ScanResult], limit: int = 5) -> List[ScanResult]:
        """
        Extracts the highest conviction SELL signals (Score < 50).
        Sorts ascending so the absolutely weakest stocks appear at the top.
        
        Args:
            results: List of ScanResult objects.
            limit: Maximum number of results to return.
            
        Returns:
            List[ScanResult]: Top ranked SELL setups (weakest first).
        """
        sells = [r for r in results if r.total_score < 50.0]
        
        # Sort ascending so the lowest scores (most bearish) are indexed first.
        ranked_sells = sorted(
            sells,
            key=lambda x: (
                x.total_score, 
                x.trend_score, 
                x.momentum_score, 
                x.relative_strength_score
            ),
            reverse=False
        )
        
        logger.debug(f"RankingEngine identified {len(ranked_sells)} active SELL setups.")
        return ranked_sells[:limit]

    def get_watchlist(self, results: List[ScanResult], limit: int = 10) -> List[ScanResult]:
        """
        Extracts the pending WATCH setups (Score between 50 and 79.99).
        Maintains standard descending sort order to prioritize those closest to breaking out.
        Returns every matching stock, ignoring limit if requested by system constraints.
        
        Args:
            results: List of ScanResult objects.
            limit: Legacy parameter, no longer restricts output size for watchlist.
            
        Returns:
            List[ScanResult]: All ranked WATCH setups.
        """
        ranked = self.sort_by_score(results)
        watch = [r for r in ranked if 50.0 <= r.total_score < 80.0]
        
        logger.debug(f"RankingEngine identified {len(watch)} WATCH setups.")
        return watch
