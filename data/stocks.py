"""
Stock universe data structure.
Contains the Top 50 most liquid NSE F&O stocks cleanly categorized.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Stock:
    """
    Domain model representing a single stock entity.
    """
    symbol: str
    company_name: str
    sector: str
    is_fno: bool
    is_nifty50: bool
    mcap: str = ""

# The core universe of Top 50 liquid F&O stocks
TOP_50_STOCKS: List[Stock] = [
    # BANK
    Stock("HDFCBANK", "HDFC Bank Ltd.", "BANK", True, True),
    Stock("ICICIBANK", "ICICI Bank Ltd.", "BANK", True, True),
    Stock("AXISBANK", "Axis Bank Ltd.", "BANK", True, True),
    Stock("KOTAKBANK", "Kotak Mahindra Bank Ltd.", "BANK", True, True),
    Stock("INDUSINDBK", "IndusInd Bank Ltd.", "BANK", True, True),
    
    # IT
    Stock("INFY", "Infosys Ltd.", "IT", True, True),
    Stock("TCS", "Tata Consultancy Services Ltd.", "IT", True, True),
    Stock("HCLTECH", "HCL Technologies Ltd.", "IT", True, True),
    Stock("WIPRO", "Wipro Ltd.", "IT", True, True),
    Stock("TECHM", "Tech Mahindra Ltd.", "IT", True, True),
    
    # AUTO
    Stock("MARUTI", "Maruti Suzuki India Ltd.", "AUTO", True, True),
    Stock("M&M", "Mahindra & Mahindra Ltd.", "AUTO", True, True),
    Stock("TMCV", "Tata Motors Ltd.", "AUTO", True, True),
    Stock("BAJAJ-AUTO", "Bajaj Auto Ltd.", "AUTO", True, True),
    Stock("EICHERMOT", "Eicher Motors Ltd.", "AUTO", True, True),
    
    # PHARMA
    Stock("SUNPHARMA", "Sun Pharmaceutical Industries Ltd.", "PHARMA", True, True),
    Stock("DRREDDY", "Dr. Reddy's Laboratories Ltd.", "PHARMA", True, True),
    Stock("CIPLA", "Cipla Ltd.", "PHARMA", True, True),
    Stock("DIVISLAB", "Divi's Laboratories Ltd.", "PHARMA", True, True),
    Stock("LUPIN", "Lupin Ltd.", "PHARMA", True, False),
    
    # METAL
    Stock("TATASTEEL", "Tata Steel Ltd.", "METAL", True, True),
    Stock("JSWSTEEL", "JSW Steel Ltd.", "METAL", True, True),
    Stock("HINDALCO", "Hindalco Industries Ltd.", "METAL", True, True),
    Stock("VEDL", "Vedanta Ltd.", "METAL", True, False),
    Stock("NMDC", "NMDC Ltd.", "METAL", True, False),
    
    # REALTY
    Stock("DLF", "DLF Ltd.", "REALTY", True, False),
    Stock("GODREJPROP", "Godrej Properties Ltd.", "REALTY", True, False),
    Stock("OBEROIRLTY", "Oberoi Realty Ltd.", "REALTY", True, False),
    Stock("LODHA", "Macrotech Developers Ltd.", "REALTY", True, False),
    Stock("PRESTIGE", "Prestige Estates Projects Ltd.", "REALTY", True, False),
    
    # FMCG
    Stock("ITC", "ITC Ltd.", "FMCG", True, True),
    Stock("HUL", "Hindustan Unilever Ltd.", "FMCG", True, True),
    Stock("NESTLEIND", "Nestle India Ltd.", "FMCG", True, True),
    Stock("TATACONSUM", "Tata Consumer Products Ltd.", "FMCG", True, True),
    Stock("BRITANNIA", "Britannia Industries Ltd.", "FMCG", True, True),
    
    # ENERGY
    Stock("RELIANCE", "Reliance Industries Ltd.", "ENERGY", True, True),
    Stock("TATAPOWER", "Tata Power Company Ltd.", "ENERGY", True, False),
    Stock("ADANIENT", "Adani Enterprises Ltd.", "ENERGY", True, True),
    Stock("ADANIPORTS", "Adani Ports & SEZ Ltd.", "ENERGY", True, True),
    Stock("BPCL", "Bharat Petroleum Corporation Ltd.", "ENERGY", True, True),
    
    # PSU
    Stock("SBIN", "State Bank of India", "PSU", True, True),
    Stock("ONGC", "Oil & Natural Gas Corporation Ltd.", "PSU", True, True),
    Stock("NTPC", "NTPC Ltd.", "PSU", True, True),
    Stock("POWERGRID", "Power Grid Corporation of India Ltd.", "PSU", True, True),
    Stock("COALINDIA", "Coal India Ltd.", "PSU", True, True),
    
    # FINANCE
    Stock("BAJFINANCE", "Bajaj Finance Ltd.", "FINANCE", True, True),
    Stock("BAJAJFINSV", "Bajaj Finserv Ltd.", "FINANCE", True, True),
    Stock("CHOLAFIN", "Cholamandalam Investment & Finance Co.", "FINANCE", True, False),
    Stock("SHRIRAMFIN", "Shriram Finance Ltd.", "FINANCE", True, True),
    Stock("HDFCLIFE", "HDFC Life Insurance Co Ltd.", "FINANCE", True, True),
]
