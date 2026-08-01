"""
RAHUUL RADAR — Enterprise Governance: License Manager (Task 6)
==============================================================
License Tiers (FREE, PRO, ENTERPRISE, INSTITUTIONAL) controlling module access.
"""

from typing import Dict, List, Set
from enterprise.enterprise_models import LicenseRecord


class LicenseManager:
    """
    Module Feature License Access Control.
    """

    TIER_FEATURES: Dict[str, Set[str]] = {
        "FREE": {"dashboard", "swing_scanner", "paper_trading_basic"},
        "PRO": {"dashboard", "swing_scanner", "fno_engine", "paper_trading_advanced", "quant_lab_basic"},
        "ENTERPRISE": {"dashboard", "swing_scanner", "fno_engine", "paper_trading_full", "quant_lab_full", "ai_learning", "ops"},
        "INSTITUTIONAL": {"dashboard", "swing_scanner", "fno_engine", "paper_trading_full", "quant_lab_full", "ai_learning", "ops", "multi_tenant", "hft_gateway"}
    }

    def is_module_allowed(self, tier: str, module_name: str) -> bool:
        """Checks if a module/feature is unlocked under the license tier."""
        features = self.TIER_FEATURES.get(tier.upper(), self.TIER_FEATURES["FREE"])
        return module_name in features or "ops" in features  # Ops/Full tiers unlock core features
