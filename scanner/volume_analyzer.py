"""
Volume Analyzer for RAHUUL_RADAR
Standalone module - can be used independently

Add this file to: scanner/volume_analyzer.py
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class VolumeMetrics:
    """Volume analysis metrics for a stock."""
    symbol: str
    current_volume: float
    avg_volume_20d: float
    volume_ratio: float
    is_surge: bool
    is_climax: bool  # Extremely high volume (potential reversal)
    trend_confirmation: str  # "CONFIRMED", "WEAK", "NEUTRAL", "CLIMAX", "LOW_LIQUIDITY"


class VolumeAnalyzer:
    """
    Analyzes volume patterns to confirm or reject trading signals.

    Key Concepts:
    - Volume Surge: Current volume > 1.5x average (confirms breakout)
    - Volume Climax: Current volume > 3x average (potential reversal)
    - Trend Confirmation: Rising volume in direction of trend
    """

    # Thresholds - TWEAK THESE AS NEEDED
    SURGE_MULTIPLIER = 1.5
    CLIMAX_MULTIPLIER = 3.0
    MIN_AVG_VOLUME = 100000  # Minimum average volume for liquidity

    def analyze(
        self,
        symbol: str,
        df: pd.DataFrame,
        lookback: int = 20
    ) -> VolumeMetrics:
        """
        Analyze volume for a given stock.

        Args:
            symbol: Stock symbol
            df: DataFrame with 'Volume' column
            lookback: Days to calculate average

        Returns:
            VolumeMetrics with analysis results
        """
        if df is None or df.empty or 'Volume' not in df.columns:
            return VolumeMetrics(
                symbol=symbol,
                current_volume=0,
                avg_volume_20d=0,
                volume_ratio=0,
                is_surge=False,
                is_climax=False,
                trend_confirmation="NO_DATA"
            )

        try:
            volumes = df['Volume'].dropna()
            if len(volumes) < lookback + 1:
                return VolumeMetrics(
                    symbol=symbol,
                    current_volume=volumes.iloc[-1] if len(volumes) > 0 else 0,
                    avg_volume_20d=0,
                    volume_ratio=0,
                    is_surge=False,
                    is_climax=False,
                    trend_confirmation="INSUFFICIENT_DATA"
                )

            current_volume = float(volumes.iloc[-1])
            avg_volume = float(volumes.iloc[-lookback:-1].mean())

            if avg_volume <= 0:
                volume_ratio = 0
            else:
                volume_ratio = current_volume / avg_volume

            # Determine volume state
            is_surge = volume_ratio >= self.SURGE_MULTIPLIER
            is_climax = volume_ratio >= self.CLIMAX_MULTIPLIER

            # Trend confirmation logic
            if is_climax:
                trend_confirmation = "CLIMAX"  # Potential reversal
            elif is_surge:
                trend_confirmation = "CONFIRMED"  # Strong confirmation
            elif volume_ratio >= 1.2:
                trend_confirmation = "MODERATE"  # Some confirmation
            elif volume_ratio >= 0.8:
                trend_confirmation = "NEUTRAL"  # Normal volume
            else:
                trend_confirmation = "WEAK"  # Low volume

            # Check minimum liquidity
            if avg_volume < self.MIN_AVG_VOLUME:
                trend_confirmation = "LOW_LIQUIDITY"
                is_surge = False

            return VolumeMetrics(
                symbol=symbol,
                current_volume=current_volume,
                avg_volume_20d=avg_volume,
                volume_ratio=round(volume_ratio, 2),
                is_surge=is_surge,
                is_climax=is_climax,
                trend_confirmation=trend_confirmation
            )

        except Exception as e:
            logger.error(f"Volume analysis error for {symbol}: {e}")
            return VolumeMetrics(
                symbol=symbol,
                current_volume=0,
                avg_volume_20d=0,
                volume_ratio=0,
                is_surge=False,
                is_climax=False,
                trend_confirmation="ERROR"
            )

    def filter_by_volume(
        self,
        scan_results: List[Dict[str, Any]],
        min_volume_ratio: float = 1.5,
        require_surge: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filter scan results by volume confirmation.

        Args:
            scan_results: List of scan result dictionaries
            min_volume_ratio: Minimum volume surge ratio
            require_surge: If True, only return stocks with volume surge

        Returns:
            Filtered list of scan results
        """
        filtered = []

        for result in scan_results:
            volume_metrics = result.get('volume_metrics')

            if not volume_metrics:
                if not require_surge:
                    filtered.append(result)
                continue

            # Skip low liquidity stocks
            if volume_metrics.trend_confirmation == "LOW_LIQUIDITY":
                logger.warning(f"Skipping {volume_metrics.symbol}: Low liquidity")
                continue

            # Skip climax volume (potential reversal)
            if volume_metrics.is_climax:
                logger.warning(
                    f"Skipping {volume_metrics.symbol}: Volume climax "
                    f"({volume_metrics.volume_ratio:.1f}x) - potential reversal"
                )
                continue

            # Check volume surge
            if require_surge and not volume_metrics.is_surge:
                logger.info(
                    f"Filtering out {volume_metrics.symbol}: "
                    f"Volume ratio {volume_metrics.volume_ratio:.1f}x < {min_volume_ratio}x"
                )
                continue

            # Add volume info to result
            result['volume_confirmed'] = volume_metrics.is_surge
            result['volume_ratio'] = volume_metrics.volume_ratio
            result['volume_status'] = volume_metrics.trend_confirmation

            filtered.append(result)

        logger.info(f"Volume filter: {len(scan_results)} -> {len(filtered)} stocks")
        return filtered
