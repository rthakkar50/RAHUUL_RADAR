import logging
from typing import List, Dict
from broker.broker_manager import BrokerManager
from broker.models.order import Position
from portfolio.models import PortfolioStats, SectorAllocation

logger = logging.getLogger("PortfolioManager")

class PortfolioManager:
    def __init__(self, broker_manager: BrokerManager):
        self.broker_manager = broker_manager
        
        # Basic mock sector mapping for Top 50 F&O
        self.sector_map = {
            "HDFCBANK": "BANKING", "ICICIBANK": "BANKING", "SBIN": "BANKING",
            "TCS": "IT", "INFY": "IT", "WIPRO": "IT",
            "RELIANCE": "ENERGY", "ONGC": "ENERGY",
            "TATAMOTORS": "AUTO", "M&M": "AUTO",
            "ITC": "FMCG", "HUL": "FMCG"
        }
        
    def get_portfolio_stats(self) -> PortfolioStats:
        broker = self.broker_manager.get_broker()
        if not broker:
            return PortfolioStats(0.0, 0.0, 0.0, 0.0, 0.0)
            
        funds = broker.get_funds()
        positions = broker.get_positions()
        
        invested_capital = sum(p.qty * p.avg_price for p in positions)
        total_mtm = sum(p.total_pnl for p in positions)
        total_capital = funds.available_cash + funds.collateral + invested_capital + total_mtm
        
        # Mock overall risk: assuming fixed 1% per position max loss
        overall_risk = len(positions) * 1.0 
        
        return PortfolioStats(
            total_capital=total_capital,
            invested_capital=invested_capital,
            available_cash=funds.available_cash,
            total_mtm=total_mtm,
            overall_risk_pct=overall_risk
        )
        
    def get_sector_allocation(self) -> SectorAllocation:
        broker = self.broker_manager.get_broker()
        if not broker:
            return SectorAllocation({})
            
        positions = broker.get_positions()
        invested_capital = sum(p.qty * p.avg_price for p in positions)
        
        if invested_capital == 0:
            return SectorAllocation({})
            
        sector_totals: Dict[str, float] = {}
        for p in positions:
            # Drop the .NS suffix for mapping
            clean_symbol = p.symbol.split(".")[0]
            sector = self.sector_map.get(clean_symbol, "OTHER")
            val = p.qty * p.avg_price
            sector_totals[sector] = sector_totals.get(sector, 0.0) + val
            
        allocations = {k: round((v / invested_capital) * 100, 2) for k, v in sector_totals.items()}
        return SectorAllocation(allocations)
