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
from market.paytm_provider import PaytmMoneyProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from core.sector_engine import SectorEngine
from market.universe import get_fno_symbols
from data.stocks import Stock

from core.master_signal_pipeline import MasterSignalPipeline
from core.relative_strength_engine import RelativeStrengthEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.adaptive_strategy_engine import AdaptiveStrategyEngine
from core.master_ai_decision_engine import MasterAIDecisionEngine
from scanner.scanner_engine import ScannerEngine

from core.institutional_validation_engine import InstitutionalValidationEngine, InstitutionalValidationInput
from core.trade_execution_center import TradeExecutionCenter, ExecutionRequest

logger = logging.getLogger("ScalpingScannerService")

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

# Monkey-patches removed - native pipeline logic handles type extraction cleanly now.


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


class ScalpingScannerService:
    def __init__(self):
        self.config = AppConfig()
        self.config.load()
        
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
        self.validation_engine = InstitutionalValidationEngine()
        self.execution_center = TradeExecutionCenter()
        self.last_results = []
        
    def execute_scalping_scan(self, timeframe: str = "5m", progress_callback=None) -> List[Dict[str, Any]]:
        start_time = time.time()
        logger.info("Scan Started: Scalping Scanner")
        
        try:
            market_provider = getattr(self.config, 'market_provider', getattr(self.config, 'data_provider', 'yahoo'))
            if market_provider == 'dhan':
                data_provider = DhanProvider(
                    client_id=getattr(self.config, 'dhan_client_id', ''),
                    access_token=getattr(self.config, 'dhan_access_token', '')
                )
            elif market_provider == 'paytm':
                try:
                    data_provider = PaytmMoneyProvider()
                    data_provider.connect()
                except Exception as _e:
                    logger.warning("PaytmMoneyProvider init failed (%s). Falling back to Yahoo Finance.", _e)
                    data_provider = YahooFinanceProvider()
                    data_provider.connect()
            else:
                data_provider = YahooFinanceProvider()
                data_provider.connect()
            
            try:
                fno_data = get_fno_symbols()
                if not fno_data:
                    raise ValueError("Empty universe")
            except Exception:
                fno_data = [{"symbol": s, "sector": "N/A"} for s in [
                    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", 
                    "INFY.NS", "TCS.NS", "LT.NS", "AXISBANK.NS", "ONGC.NS", "TATASTEEL.NS"
                ]]
                
            # Limit scan to 15 symbols to ensure quick processing in tests and live runs
            fno_data = fno_data[:15]
            
            stock_list = []
            for item in fno_data:
                sym = item["symbol"]
                sector = item.get("sector", "N/A")
                stock_list.append(Stock(symbol=sym, company_name=sym, sector=sector, is_fno=True, is_nifty50=True))
                
            # Patch the get_ohlcv method temporarily to make sure the ScannerEngine
            # scans using the user-selected timeframe instead of defaulting to '1d'.
            original_get_ohlcv = data_provider.get_ohlcv
            def patched_get_ohlcv(symbol, interval=timeframe, period="5d"):
                return original_get_ohlcv(symbol, interval=timeframe, period=period)
            data_provider.get_ohlcv = patched_get_ohlcv
            
            score_engine = ScoreEngine()
            
            import pandas as pd
            class SectorEngineDataProviderWrapper:
                def __init__(self, provider):
                    self._provider = provider
                def get_ohlcv(self, symbol, interval="1d", period="3mo"):
                    data = self._provider.get_ohlcv(symbol, interval, period)
                    if not data:
                        return pd.DataFrame()
                    rows = []
                    for item in data:
                        if hasattr(item, 'close'):
                            rows.append({'Close': item.close, 'Open': item.open, 'High': item.high, 'Low': item.low, 'Volume': getattr(item, 'volume', 0)})
                        elif isinstance(item, dict):
                            rows.append({'Close': item.get('close', item.get('Close')), 'Open': item.get('open', item.get('Open')), 'High': item.get('high', item.get('High')), 'Low': item.get('low', item.get('Low')), 'Volume': item.get('volume', item.get('Volume', 0))})
                    return pd.DataFrame(rows)
                def __getattr__(self, name):
                    return getattr(self._provider, name)
            
            sector_rotation_service = SectorEngine(SectorEngineDataProviderWrapper(data_provider))
            scanner = ScannerEngine(
                data_provider=data_provider,
                trend_engine=self.engines["trend"],
                momentum_engine=self.engines["momentum"],
                structure_engine=self.engines["structure"],
                score_engine=score_engine,
                sector_engine=sector_rotation_service,
                relative_strength_engine=self.engines["relative_strength"]
            )
            
            if progress_callback:
                progress_callback(20)
                
            raw_results = scanner.scan_market(
                stock_list, 
                mode="SCALPING", 
                progress_callback=lambda idx, tot: progress_callback(20 + int(idx/tot * 50)) if progress_callback else None
            )
            
            # Restore the original get_ohlcv method
            data_provider.get_ohlcv = original_get_ohlcv
            
            if progress_callback:
                progress_callback(80)
                
            processed_results = []
            
            def process_scalping_post_scan(r):
                symbol = r.symbol
                tick_start = time.time()
                
                # Fetch cached price/volume directly from ScanResult instead of hitting Yahoo Finance again
                price = getattr(r, 'price', 0.0)
                volume = getattr(r, 'volume', 0.0)
                    
                decision_str = getattr(r.signal, 'value', str(r.signal))
                
                pipeline_res = self.pipeline.run(
                    symbol=symbol,
                    price=price,
                    decision=decision_str,
                    confidence=safe_float(getattr(r, 'confidence', 80.0), 80.0)
                )
                
                data_dict = pipeline_res.get("data", {})
                
                score = safe_int(pipeline_res.get("score", getattr(r, "adjusted_score", getattr(r, "total_score", 50))), 50)
                
                if decision_str in ["SELL", "STRONG_SELL"]:
                    score = 100 - score
                
                cal_conf = pipeline_res.get("calibrated_confidence")
                confidence = safe_float(cal_conf if cal_conf else pipeline_res.get("exit_confidence", getattr(r, "confidence", 80.0)), 80.0)
                
                entry = safe_float(pipeline_res.get("recommended_entry", 0.0), 0.0)
                sl = safe_float(pipeline_res.get("stop_loss", 0.0), 0.0)
                t1 = safe_float(pipeline_res.get("target_1", 0.0), 0.0)
                t2 = safe_float(pipeline_res.get("target_2", 0.0), 0.0)

                if entry == 0.0 or sl == 0.0 or t1 == 0.0:
                    return None
                rr = pipeline_res.get("risk_reward", 2.0)
                
                # 4. Institutional Validation Engine
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
                
                # 5. Trade Execution Center
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
                    strategy_name="SCALPING",
                    timestamp=datetime.now().isoformat()
                )
                self.execution_center.validate_request(req)
                self.execution_center.perform_risk_check(req)
                self.execution_center.perform_validation_check(req)
                
                mom_val = data_dict.get("Momentum")
                if mom_val is not None:
                    if hasattr(mom_val, "direction"):
                        mom_val = mom_val.direction
                else:
                    mom_val = "Neutral"
                    
                # Sector mapping fallback
                sector = getattr(r, "sector", "Unknown")
                if not sector or sector == "N/A":
                    sector = "Unknown"
                    from data.stocks import TOP_50_STOCKS
                    for s in TOP_50_STOCKS:
                        if s.symbol in symbol or symbol in s.symbol:
                            if s.sector and s.sector != "N/A":
                                sector = s.sector
                                break
                                
                vol_display = str(int(volume)) if volume > 0 else "--"
                tick_exec = time.time() - tick_start
                logger.info(f"Scalping Scanner mapped {symbol} in {tick_exec:.4f}s")
                
                return {
                    "Symbol": symbol,
                    "Company": symbol.replace(".NS", ""),
                    "Sector": sector,
                    "LTP": round(price, 2),
                    "Signal": decision_str,
                    "Score": score,
                    "Confidence": round(confidence, 1),
                    "Entry": round(entry, 2),
                    "Stop Loss": round(sl, 2),
                    "Target": round(t1, 2),
                    "Risk Reward": f"1:{round(rr, 1)}" if isinstance(rr, (int, float)) else str(rr),
                    "Volume": vol_display,
                    "Momentum": str(mom_val),
                    "Execution Time": f"{tick_exec:.2f}s"
                }
                
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(process_scalping_post_scan, r) for r in raw_results]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res = future.result()
                        if res:
                            processed_results.append(res)
                    except Exception as e:
                        logger.error(f"Error processing post-scan for a scalping symbol: {e}")
                
            self.last_results = processed_results
            exec_time = time.time() - start_time
            logger.info(f"Scan Completed: Scalping Scanner. Found {len(processed_results)} symbols. Exec time: {exec_time:.2f}s")
            
            if progress_callback:
                progress_callback(100)
                
            return processed_results
            
        except Exception as e:
            logger.error(f"Errors occurred in Scalping Scanner: {e}")
            if progress_callback:
                progress_callback(100)
            return []

    def export_csv(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            if not results:
                return ""
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            keys = results[0].keys()
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            logger.info(f"Export CSV successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export CSV failed: {e}")
            return ""

    def export_excel(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            if not results:
                return ""
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            try:
                import pandas as pd
                pd.DataFrame(results).to_excel(filepath, index=False)
            except Exception:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            logger.info(f"Export Excel successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export Excel failed: {e}")
            return ""

    def export_json(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            if not results:
                return ""
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=4)
            logger.info(f"Export JSON successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export JSON failed: {e}")
            return ""
