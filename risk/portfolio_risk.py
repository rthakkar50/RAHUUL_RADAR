from .models import RiskProfile

class PortfolioRiskEngine:
    def __init__(self):
        pass

    def evaluate_exposure(self, profile: RiskProfile, current_open_trades: int, sector: str, current_sector_exposure_pct: float) -> tuple[bool, str]:
        """
        Validates if adding a new trade violates portfolio-wide rules.
        """
        if current_open_trades >= profile.max_open_trades:
            return False, f"Max Open Trades Reached ({profile.max_open_trades})"
            
        if current_sector_exposure_pct >= profile.max_sector_exposure_pct:
            return False, f"Sector Exposure Limit Reached for {sector} ({profile.max_sector_exposure_pct}%)"
            
        # Placeholder for correlation checks, requiring historical correlation matrix
        
        return True, "Valid"
