import os
import sqlite3
import json
import logging
from typing import Dict, List, Any
from datetime import datetime

# Import Engines to verify compilation
from strategy.mie_engine import MarketIntelligenceEngine
from strategy.eve_engine import EntryValidationEngine
from strategy.fbde_engine import FalseBreakoutDetectionEngine
from strategy.eme_engine import ExitManagementEngine
from strategy.ltme_engine import LiveTradeMonitoringEngine
from strategy.cpe_engine import CapitalProtectionEngine
from strategy.uasd_engine import UnifiedScoringEngine
from strategy.trfa_engine import TradeForensicEngine
from strategy.ptve_engine import PaperTradingValidationEngine

logger = logging.getLogger(__name__)

class ProductionCertificationEngine:
    """
    MASTER-12: PRODUCTION CERTIFICATION ENGINE (PCE) V2.0
    The Final Gatekeeper. Audits the entire system before Live Trading.
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.scores = {
            "Scanner": 100,
            "AI": 100,
            "Risk": 100,
            "Capital_Protection": 100
        }
        
    def _add_error(self, category: str, msg: str, is_critical: bool = True):
        self.errors.append({"category": category, "msg": msg, "critical": is_critical})
        if is_critical:
            self.scores[category] -= 20
        else:
            self.scores[category] -= 10
            
    def _add_warning(self, msg: str):
        self.warnings.append(msg)
        
    def run_full_audit(self) -> str:
        """
        Runs the complete audit and returns the generated markdown report.
        """
        self.errors.clear()
        self.warnings.clear()
        
        self._audit_modules()
        self._audit_engines()
        self._audit_capital_protection()
        self._audit_paper_trading()
        
        return self._generate_report()
        
    def _audit_modules(self):
        # Verify core UI files exist
        required_ui = [
            "dashboard.py", "pages/swing_scanner_page.py", "intraday_scanner.py",
            "option_chain_page.py", "charts.py", "heatmap.py",
            "diagnostics.py", "live_trades_page.py", "trfa_page.py", "ptve_page.py"
        ]
        
        for f in required_ui:
            if not os.path.exists(f"ui/{f}"):
                self._add_error("Scanner", f"Missing UI Module: {f}", is_critical=True)
                
        # Verify Databases
        dbs = ["radar.db", "trade_journal.db", "paper_trading.db", "trade_forensics.db"]
        for db in dbs:
            if not os.path.exists(f"data/{db}") and not os.path.exists(db):
                self._add_error("Capital_Protection", f"Missing Database: {db}", is_critical=False)
                
    def _audit_engines(self):
        try:
            MarketIntelligenceEngine.get_instance()
            EntryValidationEngine()
            FalseBreakoutDetectionEngine()
            ExitManagementEngine()
            LiveTradeMonitoringEngine()
            CapitalProtectionEngine.get_instance()
            UnifiedScoringEngine()
            TradeForensicEngine()
            PaperTradingValidationEngine()
        except Exception as e:
            self._add_error("AI", f"Engine Instantiation Failure: {e}", is_critical=True)
            
    def _audit_capital_protection(self):
        # Verify config exists and has valid limits
        if not os.path.exists("config.json"):
            self._add_error("Capital_Protection", "config.json is missing.", is_critical=True)
            return
            
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                
            risk = config.get("risk", {})
            if risk.get("daily_loss_limit_pct", 0) <= 0:
                self._add_error("Risk", "Daily Loss Limit is <= 0 or missing.", is_critical=True)
            if risk.get("max_exposure_per_trade_pct", 0) <= 0:
                self._add_error("Risk", "Max Exposure per trade is <= 0 or missing.", is_critical=True)
                
            cpe = CapitalProtectionEngine.get_instance()
            res = cpe.validate_entry("RELIANCE.NS", 1.0, 5.0, "GOOD")
            if "cpe_status" not in res:
                self._add_error("Capital_Protection", "CPE engine validation returned invalid format.", is_critical=True)
                
        except Exception as e:
            self._add_error("Capital_Protection", f"Config parsing error: {e}", is_critical=True)

    def _audit_paper_trading(self):
        try:
            ptve = PaperTradingValidationEngine()
            report = ptve.generate_certification_report()
            if not report.get("certified", False):
                self._add_error("AI", f"Paper Trading Certification Failed: {report.get('status')}", is_critical=True)
        except Exception as e:
            self._add_error("AI", f"PTVE execution error: {e}", is_critical=True)
            
    def _generate_report(self) -> str:
        # Prevent negative scores
        for k in self.scores:
            self.scores[k] = max(0, self.scores[k])
            
        is_certified = True
        critical_errors = [e for e in self.errors if e["critical"]]
        major_errors = [e for e in self.errors if not e["critical"]]
        
        if len(critical_errors) > 0:
            is_certified = False
            
        overall_score = sum(self.scores.values()) / 4
        
        status_banner = "✅ CERTIFIED: READY FOR LIVE TRADING ✅" if is_certified else "❌ NOT CERTIFIED: LIVE TRADING BLOCKED ❌"
        
        report = f"""# Production Certification Engine (PCE) Audit Report
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Final Status
> [!{'IMPORTANT' if is_certified else 'CAUTION'}]
> {status_banner}

## Overall Grades
- **Scanner Score:** {self.scores["Scanner"]}/100
- **AI Engine Score:** {self.scores["AI"]}/100
- **Risk Management Score:** {self.scores["Risk"]}/100
- **Capital Protection Score:** {self.scores["Capital_Protection"]}/100
- **Overall Average:** {overall_score}/100

## Critical Errors (Blocks Live Trading)
"""
        if not critical_errors:
            report += "- None detected.\n"
        else:
            for e in critical_errors:
                report += f"- **[{e['category']}]** {e['msg']}\n"
                
        report += "\n## Major Errors\n"
        if not major_errors:
            report += "- None detected.\n"
        else:
            for e in major_errors:
                report += f"- **[{e['category']}]** {e['msg']}\n"
                
        report += "\n## Warnings & Suggestions\n"
        if not self.warnings:
            report += "- None.\n"
        else:
            for w in self.warnings:
                report += f"- {w}\n"
                
        report += "\n---\n*Generated by RAHUUL RADAR PRO - MASTER-12 (PCE)*"
        
        return report
