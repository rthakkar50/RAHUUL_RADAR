"""
RAHUUL RADAR — F&O Engine: Expiry Engine (Task 2)
=================================================
Automated Options & Futures Expiry Date Engine.
Calculates Current Weekly, Next Weekly, and Monthly Expiries for NSE/BSE/MCX/Crypto.
Handles expiry rollover logic.
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional


class ExpiryEngine:
    """
    Expiry date calculation and rollover manager.
    """

    # Default weekly expiry days by underlying symbol (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri)
    EXPIRY_DAYS = {
        "NIFTY": 3,       # Thursday
        "BANKNIFTY": 3,   # Thursday
        "FINNIFTY": 1,    # Tuesday
        "MIDCPNIFTY": 0,  # Monday
        "NIFTYNXT50": 4,  # Friday
    }

    def get_current_weekly_expiry(self, underlying: str, ref_date: Optional[date] = None) -> str:
        """Returns ISO string (YYYY-MM-DD) of the current weekly expiry date."""
        today = ref_date or date.today()
        underlying_upper = underlying.upper()
        target_weekday = self.EXPIRY_DAYS.get(underlying_upper, 3)

        days_ahead = (target_weekday - today.weekday()) % 7
        target_date = today + timedelta(days=days_ahead)
        return target_date.strftime("%Y-%m-%d")

    def get_next_weekly_expiry(self, underlying: str, ref_date: Optional[date] = None) -> str:
        """Returns ISO string (YYYY-MM-DD) of the next weekly expiry date."""
        current = datetime.strptime(self.get_current_weekly_expiry(underlying, ref_date), "%Y-%m-%d").date()
        next_weekly = current + timedelta(days=7)
        return next_weekly.strftime("%Y-%m-%d")

    def get_monthly_expiry(self, underlying: str, ref_date: Optional[date] = None) -> str:
        """Returns ISO string (YYYY-MM-DD) of the last Thursday of the current month."""
        today = ref_date or date.today()
        # Last day of current month
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)
        
        last_day = next_month - timedelta(days=1)
        
        # Roll backward to Thursday (weekday = 3)
        offset = (last_day.weekday() - 3) % 7
        last_thursday = last_day - timedelta(days=offset)
        
        # If last thursday has passed, fetch next month's last thursday
        if last_thursday < today:
            if today.month == 12:
                nm = date(today.year + 1, 2, 1)
            elif today.month == 11:
                nm = date(today.year + 1, 1, 1)
            else:
                nm = date(today.year, today.month + 2, 1)
            ld = nm - timedelta(days=1)
            off = (ld.weekday() - 3) % 7
            last_thursday = ld - timedelta(days=off)

        return last_thursday.strftime("%Y-%m-%d")

    def is_expiry_day(self, underlying: str, ref_date: Optional[date] = None) -> bool:
        """Checks if today is the expiry day for the given underlying."""
        today = ref_date or date.today()
        current_exp = self.get_current_weekly_expiry(underlying, today)
        return today.strftime("%Y-%m-%d") == current_exp

    def get_all_expiries(self, underlying: str, ref_date: Optional[date] = None) -> Dict[str, str]:
        """Returns a map of current_weekly, next_weekly, and monthly expiries."""
        return {
            "current_weekly": self.get_current_weekly_expiry(underlying, ref_date),
            "next_weekly": self.get_next_weekly_expiry(underlying, ref_date),
            "monthly": self.get_monthly_expiry(underlying, ref_date)
        }
