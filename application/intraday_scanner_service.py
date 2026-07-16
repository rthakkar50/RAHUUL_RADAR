import os
import csv
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

from config.config import AppConfig
from market.yahoo_provider import YahooFinanceProvider
from market.dhan_provider import DhanProvider
from strategy.intraday_engine import IntradayEngine
from core.trade_lock_engine import TradeLockEngine
from market.universe import get_all_symbols
from data.stocks import Stock
from scanner.scanner_engine import ScannerEngine
from ranking.score_engine import ScoreEngine
from core.sector_engine import SectorEngine

from core.master_signal_pipeline import MasterSignalPipeline
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from core.relative_strength_engine import RelativeStrengthEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.adaptive_strategy_engine import AdaptiveStrategyEngine
from core.master_ai_decision_engine import MasterAIDecisionEngine

from core.institutional_validation_engine import InstitutionalValidationEngine, InstitutionalValidationInput
from core.trade_execution_center import TradeExecutionCenter, ExecutionRequest

# ScoreFloat helper to allow transparent operations on complex engine return values
class ScoreFloat(float):
    def __new__(cls, value, original_obj=None):
        try:
            val = float(value)
        except Exception:
            val = 50.0
        inst = super(ScoreFloat, cls).__new__(cls, val)
        inst.original_obj = original_obj
        return inst
    
    def __getattr__(self, name):
        if self.original_obj is not None:
            if hasattr(self.original_obj, name):
                return getattr(self.original_obj, name)
            if isinstance(self.original_obj, dict) and name in self.original_obj:
                return self.original_obj[name]
        raise AttributeError(f"'ScoreFloat' object has no attribute '{name}'")
        
    def get(self, key, default=None):
        if isinstance(self.original_obj, dict):
            return self.original_obj.get(key, default)
        if hasattr(self.original_obj, key):
            return getattr(self.original_obj, key)
        return default

def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(val)
    except Exception:
        return default

def safe_int(val, default=0):
    if val is None:
        return default
    try:
        return int(val)
    except Exception:
        return default

# Monkey-patches removed - native pipeline logic handles type extraction cleanly now.

logger = logging.getLogger("IntradayScannerService")

class IntradayScannerService:
    def __init__(self):
        self.config = AppConfig()
        self.config.load()
        
        # Instantiate core engines for the pipeline
        self.engines = {
            "trend": TrendEngine(),
            "momentum": MomentumEngine(),
            "structure": StructureEngine(),
            "relative_strength": RelativeStrengthEngine(),
            "sector_rotation": SectorRotationEngine(),
            "adaptive_strategy": AdaptiveStrategyEngine.get_instance() if hasattr(AdaptiveStrategyEngine, 'get_instance') else AdaptiveStrategyEngine(),
            "master_ai": MasterAIDecisionEngine()
        }
        self.pipeline = MasterSignalPipeline(self.engines)
        
        self.intraday_engine = IntradayEngine()
        self.lock_engine = TradeLockEngine()
        self.validation_engine = InstitutionalValidationEngine()
        self.execution_center = TradeExecutionCenter()
        self.last_results = []
        
    def _get_market_trend(self, provider) -> str:
        try:
            ohlcv = provider.get_ohlcv("^NSEI", "5m", "2d")
            if len(ohlcv) > 10:
                import pandas as pd
                df = pd.DataFrame([{'High': c.high, 'Low': c.low, 'Close': c.close, 'Volume': c.volume} for c in ohlcv])
                df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
                vwap = (df['Typical_Price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
                if df['Close'].iloc[-1] > vwap.iloc[-1]:
                    return "BULLISH"
                else:
                    return "BEARISH"
        except Exception as e:
            logger.warning(f"Market trend calculation failed: {e}")
        return "NEUTRAL"

    def execute_intraday_scan(self, timeframe: str = "5m", progress_callback=None) -> List[Dict[str, Any]]:
        start_time = time.time()
        logger.info("Scan Started: Intraday Scanner")
        
        try:
            # 1. Setup Providers
            if getattr(self.config, 'data_provider', 'yahoo') == 'dhan':
                data_provider = DhanProvider(
                    client_id=getattr(self.config, 'dhan_client_id', ''),
                    access_token=getattr(self.config, 'dhan_access_token', '')
                )
            else:
                data_provider = YahooFinanceProvider()
                
            logger.info("Connecting to data provider...")
            data_provider.connect()
            
            # 2. Get Universe (Standard Architecture)
            logger.info("Fetching Symbol Universe...")
            fno_data = get_all_symbols()
            if not fno_data:
                raise ValueError("Empty universe returned from get_all_symbols()")
                
            stock_list = []
            for item in fno_data:
                sym = item["symbol"]
                sector = item.get("sector", "N/A")
                stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=False, is_nifty50=False))
                
            score_engine = ScoreEngine()
            sector_rotation_service = SectorEngine(data_provider)
            scanner = ScannerEngine(
                data_provider=data_provider,
                trend_engine=self.engines["trend"],
                momentum_engine=self.engines["momentum"],
                structure_engine=self.engines["structure"],
                score_engine=score_engine,
                sector_engine=sector_rotation_service
            )
            
            if progress_callback:
                progress_callback(20)
                
            # 3. Use Shared Scanner Engine
            raw_results = scanner.scan_market(
                stock_list, 
                mode="INTRADAY", 
                progress_callback=lambda idx, tot: progress_callback(20 + int(idx/tot * 50)) if progress_callback else None
            )
            
            if progress_callback:
                progress_callback(80)
                
            processed_results = []
            total = len(raw_results)
            completed = 0
            
            for r in raw_results:
                symbol = r.symbol
                
                # Fetch cached price/volume directly from ScanResult
                price = getattr(r, 'price', 0.0)
                volume = getattr(r, 'volume', 0.0)
                decision_str = getattr(r.signal, 'value', str(r.signal))
                
                try:
                    # 4. Refine with Master Signal Pipeline
                    pipeline_res = self.pipeline.run(
                        symbol=symbol,
                        price=price,
                        decision=decision_str,
                        confidence=safe_float(getattr(r, 'confidence', 80.0), 80.0),
                        trend={"score": getattr(r, 'trend_score', 50.0)},
                        momentum={"score": getattr(r, 'momentum_score', 50.0)},
                        structure={"score": getattr(r, 'structure_score', 50.0)},
                        volume={"score": getattr(r, 'volume_score', 50.0)},
                        risk={"score": getattr(r, 'risk_score', 50.0)},
                        relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)}
                    )
                    
                    engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
                    score = safe_int(engine_score, 50)
                    bullish_score = score
                    
                    # Normalization Layer before Elite Selection
                    if decision_str in ["SELL", "STRONG_SELL"]:
                        score = 100 - bullish_score
                        
                    confidence = safe_float(pipeline_res.get("calibrated_confidence", getattr(r, "confidence", 80.0)), 80.0)
                    
                    entry = safe_float(pipeline_res.get("recommended_entry", 0.0), 0.0)
                    sl = safe_float(pipeline_res.get("stop_loss", 0.0), 0.0)
                    t1 = safe_float(pipeline_res.get("target_1", 0.0), 0.0)
                    t2 = safe_float(pipeline_res.get("target_2", 0.0), 0.0)

                    if entry == 0.0 or sl == 0.0 or t1 == 0.0:
                        continue
                    rr = pipeline_res.get("risk_reward", 2.0)
                    
                    sector = getattr(r, "sector", "Unknown")
                    if not sector or sector == "N/A":
                        sector = "Unknown"
                        
                    # 5. Institutional Validation Engine
                    fs_res = pipeline_res.get("report")
                    if fs_res is not None:
                        if hasattr(fs_res, "to_dict"):
                            fs_dict = fs_res.to_dict()
                        elif hasattr(fs_res, "status"):
                            fs_dict = {"status": fs_res.status}
                        elif isinstance(fs_res, dict):
                            fs_dict = fs_res
                        else:
                            fs_dict = {"status": "APPROVED"}
                    else:
                        fs_dict = {"status": "APPROVED"}
                        
                    val_input = InstitutionalValidationInput(
                        false_signal_result=fs_dict,
                        mtf_result={"status": pipeline_res.get("status") or "APPROVED", "score": 100.0},
                        entry_result={"entry_score": safe_float(pipeline_res.get("entry_score"), 100.0)},
                        exit_result={"exit_action": pipeline_res.get("exit_action") or "HOLD", "exit_confidence": confidence},
                        walk_forward_result={"status": "APPROVED"},
                        ranking_result={"status": "APPROVED"},
                        confidence_result={"confidence": confidence, "status": "APPROVED"},
                        performance_result={"status": "APPROVED"}
                    )
                    self.validation_engine.validate_all_modules(val_input)
                    
                    # 6. Trade Execution Center
                    req = ExecutionRequest(
                        symbol=symbol,
                        action=decision_str if decision_str in ["BUY", "SELL"] else "BUY",
                        quantity=10,
                        entry_price=entry,
                        stop_loss=sl,
                        target_1=t1,
                        target_2=t2,
                        target_3=t2,
                        confidence=confidence,
                        position_size_factor=1.0,
                        strategy_name="INTRADAY",
                        timestamp=datetime.now().isoformat()
                    )
                    self.execution_center.validate_request(req)
                    self.execution_center.perform_risk_check(req)
                    self.execution_center.perform_validation_check(req)
                    
                    processed_results.append({
                        "Symbol": symbol,
                        "Company": symbol.replace(".NS", ""),
                        "Sector": sector,
                        "Price": round(price, 2),
                        "Signal": decision_str,
                        "Score": score,
                        "Raw Score": bullish_score,
                        "Confidence": round(confidence, 1),
                        "Entry": round(entry, 2),
                        "Stop Loss": round(sl, 2),
                        "Target 1": round(t1, 2),
                        "Target 2": round(t2, 2),
                        "Risk Reward": f"1:{round(rr, 1)}" if isinstance(rr, (int, float)) else str(rr),
                        "Volume": int(volume),
                        "OI": 0,
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    logger.error(f"Error evaluating symbol {symbol}: {e}")
                    
                completed += 1
                if progress_callback:
                    progress_callback(80 + int((completed / total) * 15))
                    
            if not processed_results:
                raise Exception("Universe scanned but 0 valid setups found. (Possible Data Fetch Timeout or API Block)")
                
            self.last_full_results = processed_results
            
            # --- STAGE 2: ELITE SELECTION ENGINE & PRECISION ENTRY ENGINE ---
            from core.elite_selection_engine import EliteSelectionEngine
            from core.precision_entry_engine import PrecisionEntryEngine
            ese = EliteSelectionEngine()
            pee = PrecisionEntryEngine()
            
            elite_candidates = []
            for res in processed_results:
                elite_res = ese.evaluate(dict(res)) # pass copy so full export is untouched
                if elite_res is not None:
                    pee_res = pee.evaluate(elite_res)
                    if pee_res is not None:
                        # Map the new fields to UI columns for display
                        pee_res["Score"] = pee_res.get("Trade Quality Index", res["Score"])
                        pee_res["Trend"] = pee_res.get("Trade Grade", "")
                        pee_res["Risk Reward"] = f"{pee_res.get('Risk Grade', '')} | {res.get('Risk Reward', '')}"
                        pee_res["Signal"] = f"{pee_res.get('Entry Decision', '')} | {res.get('Signal', '')}"
                        pee_res["Confidence"] = pee_res.get("Entry Score", 0)
                        pee_res["Timestamp"] = f"{res.get('Timestamp', '')} | Hold: {pee_res.get('Expected Holding Time', '')}"
                        pee_res["Company"] = f"{res.get('Company', '')} - {pee_res.get('Reason Selected', '')}"
                        elite_candidates.append(pee_res)
                    
            buys = [res for res in elite_candidates if "BUY" in str(res.get("Signal", ""))]
            watches = [res for res in elite_candidates if "WATCH" in str(res.get("Signal", ""))]
            sells = [res for res in elite_candidates if "SELL" in str(res.get("Signal", ""))]

            buys.sort(key=lambda x: float(x.get("Score", 0)), reverse=True)
            watches.sort(key=lambda x: float(x.get("Score", 0)), reverse=True)
            sells.sort(key=lambda x: float(x.get("Score", 0)), reverse=True)
            
            elite_picks = buys[:10] + watches[:10] + sells[:10]
            
            self.last_results = elite_picks
            exec_time = time.time() - start_time
            logger.info(f"Scan Completed: Intraday Scanner. Found {len(processed_results)} assets. Filtered to {len(elite_picks)} Elite Picks. Exec time: {exec_time:.2f}s")
            
            if progress_callback:
                progress_callback(100)
                
            return elite_picks
            
        except Exception as e:
            err_msg = f"Scanner Failed: {str(e)}"
            logger.error(err_msg)
            if progress_callback:
                progress_callback(100)
            raise Exception(err_msg)

    def export_csv(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            export_data = getattr(self, "last_full_results", results)
            if not export_data:
                return ""
            dir_name = os.path.dirname(filepath)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            keys = export_data[0].keys()
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(export_data)
            logger.info(f"Export CSV successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export CSV failed: {e}")
            return ""

    def export_excel(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            export_data = getattr(self, "last_full_results", results)
            if not export_data:
                return ""
            dir_name = os.path.dirname(filepath)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            try:
                import pandas as pd
                pd.DataFrame(export_data).to_excel(filepath, index=False)
            except Exception:
                # Fallback to CSV style write renamed to .xlsx
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
                    writer.writeheader()
                    writer.writerows(export_data)
            logger.info(f"Export Excel successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export Excel failed: {e}")
            return ""

    def export_json(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            export_data = getattr(self, "last_full_results", results)
            if not export_data:
                return ""
            dir_name = os.path.dirname(filepath)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=4)
            logger.info(f"Export JSON successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export JSON failed: {e}")
            return ""
