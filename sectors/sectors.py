"""
Sector definitions and helper functions for RAHUUL_RADAR.
"""
from enum import Enum
from typing import List
from data.stocks import TOP_50_STOCKS, Stock

class Sector(str, Enum):
    """
    Core sectors mapped out for the Indian Stock Market Scanner.
    """
    BANK = "BANK"
    IT = "IT"
    AUTO = "AUTO"
    PHARMA = "PHARMA"
    METAL = "METAL"
    REALTY = "REALTY"
    FMCG = "FMCG"
    ENERGY = "ENERGY"
    PSU = "PSU"
    FINANCE = "FINANCE"

def get_all_sectors() -> List[str]:
    """
    Returns a list of all defined sector names as strings.
    """
    return [sector.value for sector in Sector]

def get_sector_stocks(sector_name: str) -> List[Stock]:
    """
    Returns a list of Stock objects belonging to the specified sector.
    
    Args:
        sector_name: The name of the sector to filter by (e.g., "BANK")
        
    Returns:
        List of Stock objects.
    """
    normalized_sector = sector_name.upper().strip()
    return [stock for stock in TOP_50_STOCKS if stock.sector.upper() == normalized_sector]
