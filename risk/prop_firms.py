from abc import ABC, abstractmethod
from .models import RiskProfile

class PropFirmRules(ABC):
    @abstractmethod
    def validate_rules(self, profile: RiskProfile, daily_drawdown: float, total_drawdown: float) -> tuple[bool, str]:
        pass

class FTMORules(PropFirmRules):
    def validate_rules(self, profile: RiskProfile, daily_drawdown: float, total_drawdown: float) -> tuple[bool, str]:
        if daily_drawdown >= 5.0:
            return False, "FTMO: Daily Drawdown Limit Reached (5%)"
        if total_drawdown >= 10.0:
            return False, "FTMO: Max Drawdown Limit Reached (10%)"
        return True, "Valid"

class FundedNextRules(PropFirmRules):
    def validate_rules(self, profile: RiskProfile, daily_drawdown: float, total_drawdown: float) -> tuple[bool, str]:
        if daily_drawdown >= 5.0:
            return False, "FundedNext: Daily Drawdown Limit Reached (5%)"
        if total_drawdown >= 10.0:
            return False, "FundedNext: Max Drawdown Limit Reached (10%)"
        return True, "Valid"

class The5ersRules(PropFirmRules):
    def validate_rules(self, profile: RiskProfile, daily_drawdown: float, total_drawdown: float) -> tuple[bool, str]:
        if daily_drawdown >= 4.0:
            return False, "5ers: Daily Pause Level Reached (4%)"
        if total_drawdown >= 6.0:
            return False, "5ers: Max Drawdown Limit Reached (6%)"
        return True, "Valid"

class FundingPipsRules(PropFirmRules):
    def validate_rules(self, profile: RiskProfile, daily_drawdown: float, total_drawdown: float) -> tuple[bool, str]:
        if daily_drawdown >= 5.0:
            return False, "FundingPips: Daily Drawdown Limit Reached (5%)"
        if total_drawdown >= 10.0:
            return False, "FundingPips: Max Drawdown Limit Reached (10%)"
        return True, "Valid"

class CustomRules(PropFirmRules):
    def validate_rules(self, profile: RiskProfile, daily_drawdown: float, total_drawdown: float) -> tuple[bool, str]:
        if daily_drawdown >= profile.max_daily_loss_pct:
            return False, f"Custom: Daily Drawdown Limit Reached ({profile.max_daily_loss_pct}%)"
        return True, "Valid"

def get_prop_firm_validator(name: str) -> PropFirmRules:
    mapping = {
        "ftmo": FTMORules,
        "fundednext": FundedNextRules,
        "5ers": The5ersRules,
        "fundingpips": FundingPipsRules,
        "custom": CustomRules
    }
    return mapping.get(name.lower(), CustomRules)()
