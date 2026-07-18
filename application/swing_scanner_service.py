import os
import csv
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Union

from config.config import AppConfig
from market.yahoo_provider import YahooFinanceProvider
from market.dhan_provider import DhanProvider
from core.trend_engine import TrendEngine
from core.momentum_engine import MomentumEngine
from core.structure_engine import StructureEngine
from ranking.score_engine import ScoreEngine
from core.sector_engine import SectorEngine
from market.universe import get_all_symbols
from data.stocks import Stock

from core.master_signal_pipeline import MasterSignalPipeline
from core.relative_strength_engine import RelativeStrengthEngine
from core.sector_rotation_engine import SectorRotationEngine
from core.adaptive_strategy_engine import AdaptiveStrategyEngine
from core.master_ai_decision_engine import MasterAIDecisionEngine
from scanner.scanner_engine import ScannerEngine
from utils.validation import validate_trade_levels

logger = logging.getLogger("SwingScannerService")

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


class SwingScannerService:
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
        self.last_results = []
        
    def execute_swing_scan(self, progress_callback=None) -> List[Dict[str, Any]]:
        start_time = time.time()
        logger.info(f"Entered Function: execute_swing_scan in core/swing_scanner_service.py")
        logger.info(f"Input: progress_callback present = {progress_callback is not None}")
        
        try:
            if getattr(self.config, 'data_provider', 'yahoo') == 'dhan':
                data_provider = DhanProvider(
                    client_id=getattr(self.config, 'dhan_client_id', ''),
                    access_token=getattr(self.config, 'dhan_access_token', '')
                )
            else:
                data_provider = YahooFinanceProvider()
                
            logger.info("Connecting to data provider...")
            data_provider.connect()
            
            logger.info("Fetching Symbol Universe...")
            universe_start = time.time()
            fno_data = get_all_symbols()
            
            # Phase 2: Explicit Universe Verification
            if not fno_data:
                logger.error("Swing scanner universe empty")
                raise ValueError("No symbols loaded for Swing Scanner. Empty universe returned.")
                
            logger.info(f"Swing scanner loaded {len(fno_data)} symbols from source F&O Universe")
            logger.info(f"Swing scanner scan started for {len(fno_data)} symbols")
            
            logger.info(f"Output Symbol Universe: {len(fno_data)} symbols loaded")
            logger.info(f"Execution Time (Universe): {time.time() - universe_start:.2f}s")
                
        # Complete Universe Loaded
            
            stock_list = []
            # Build a fast symbol→sector+company lookup from the universe data
            sym_meta = {item["symbol"]: item for item in fno_data}
            for item in fno_data:
                sym = item["symbol"]
                sector = item.get("sector", "F&O")
                company_name = item.get("company_name", sym.replace(".NS", ""))
                stock_list.append(Stock(symbol=sym, company_name=company_name, sector=sector, is_fno=True, is_nifty50=False))
                
            score_engine = ScoreEngine()
            sector_rotation_service = SectorEngine(data_provider)
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
                
            if hasattr(data_provider, 'pre_cache'):
                logger.info("Pre-caching market data for SWING scan...")
                syms = [s.symbol for s in stock_list]
                from concurrent.futures import ThreadPoolExecutor
                def _cache_job(args):
                    interval, period = args
                    data_provider.pre_cache(syms, interval, period)
                with ThreadPoolExecutor(max_workers=4) as executor:
                    executor.map(_cache_job, [
                        ("1d", "3mo"),
                        ("15m", "5d"),
                        ("1h", "1mo"),
                        ("1wk", "1y")
                    ])
                
            raw_results = scanner.scan_market(
                stock_list, 
                mode="SWING", 
                progress_callback=lambda idx, tot: progress_callback(20 + int(idx/tot * 50)) if progress_callback else None
            )
            
            if progress_callback:
                progress_callback(80)
                
            processed_results = []
            
            def process_post_scan(r):
                symbol = r.symbol
                tick_start = time.time()
                
                # Fetch cached price/volume directly from ScanResult instead of hitting Yahoo Finance again
                price = getattr(r, 'price', 0.0)
                volume = getattr(r, 'volume', 0.0)
                    
                decision_str = getattr(r.signal, 'value', str(r.signal))
                
                breakdown = getattr(r, 'breakdown_detail', {}) or {}
                atr_val = breakdown.get("atr", 0.0)
                structure_details = breakdown.get("structure", {})
                
                pipeline_res = self.pipeline.run(
                    symbol=symbol,
                    price=price,
                    decision=decision_str,
                    confidence=safe_float(getattr(r, 'confidence', 80.0), 80.0),
                    trend={"score": getattr(r, 'trend_score', 50.0)},
                    momentum={"score": getattr(r, 'momentum_score', 50.0)},
                    structure={"score": getattr(r, 'structure_score', 50.0), "details": structure_details},
                    volume={"score": getattr(r, 'volume_score', 50.0)},
                    risk={"score": getattr(r, 'risk_score', 50.0)},
                    relative_strength={"score": getattr(r, 'relative_strength_score', 50.0)},
                    adx={"score": getattr(r, 'adx_value', 0.0)},
                    avwap={"position": getattr(r, 'avwap_status', "Neutral")},
                    atr=atr_val,
                    mtf_data=getattr(r, 'mtf_data', None)
                )
                
                data_dict = pipeline_res
                
                # SPRINT-73 FIX: Use the engine's original calculated score, avoid pipeline overwrite of 0.0
                engine_score = getattr(r, "adjusted_score", getattr(r, "total_score", 50))
                score = safe_int(engine_score, 50)
                bullish_score = score
                
                # Normalization Layer before Elite Selection
                if decision_str in ["SELL", "STRONG_SELL"]:
                    score = 100 - bullish_score
                
                # BUG-04 FIX: Use real confidence from the engine, never fabricate 80.0
                # Priority: pipeline calibrated_confidence > ScanResult.confidence > computed from scores
                conf_from_engine = getattr(r, 'confidence', None)
                conf_from_pipeline = pipeline_res.get("calibrated_confidence", None)
                if conf_from_pipeline is not None:
                    confidence = safe_float(conf_from_pipeline, -1)
                elif conf_from_engine is not None:
                    confidence = safe_float(conf_from_engine, -1)
                else:
                    confidence = -1  # Genuinely unavailable
                
                entry = safe_float(pipeline_res.get("recommended_entry", 0.0), 0.0)
                sl = safe_float(pipeline_res.get("stop_loss", 0.0), 0.0)
                t1 = safe_float(pipeline_res.get("target_1", 0.0), 0.0)
                t2 = safe_float(pipeline_res.get("target_2", 0.0), 0.0)

                if entry == 0.0 or sl == 0.0 or t1 == 0.0:
                    return None

                risk_amt = abs(entry - sl)
                    
                # Ensure RR dynamically matches displayed levels
                reward_amt = abs(t1 - entry)
                if risk_amt > 0:
                    rr = reward_amt / risk_amt
                else:
                    rr = pipeline_res.get("risk_reward", 2.0)
                
                # SPRINT-73 Validation Check
                print("=" * 60)
                print("Symbol      :", r.symbol)
                print("Signal      :", decision_str)
                print("Score       :", score)
                print("Confidence  :", r.confidence)
                print("Entry       :", entry)
                print("SL          :", sl)
                print("Target1     :", t1)
                print("RR          :", rr)
                print("=" * 60)
                is_valid, valid_reason = validate_trade_levels(decision_str, entry, sl, t1)
                if not is_valid:
                    decision_str = "WATCH"
                    print("Downgraded because:", valid_reason)
                    if "reasons" not in pipeline_res:
                        pipeline_res["reasons"] = []
                    pipeline_res["reasons"].append(f"Downgraded to WATCH: {valid_reason}")
                
                # BUG-3 FIX: Use exactly what the TrendEngine evaluated, no generic fallbacks
                trend_str = str(getattr(r, "trend_direction", "SIDEWAYS")).upper()
                trend_map = {
                    "STRONG_BULL": "Strong Bullish",
                    "BULL": "Bullish",
                    "BULLISH": "Bullish",
                    "NEUTRAL": "Sideways",
                    "SIDEWAYS": "Sideways",
                    "BEAR": "Bearish",
                    "BEARISH": "Bearish",
                    "STRONG_BEAR": "Strong Bearish"
                }
                trend_display = trend_map.get(trend_str, trend_str.title())
                
                # BUG-05: Sector comes from universe FNO_UNIVERSE — already correct per symbol.
                # Use r.sector which was set from item["sector"] in the stock_list build above.
                sector = getattr(r, "sector", "")
                if not sector or sector in ("N/A", "Unknown", "FNO", "F&O"):
                    # Fallback: check FNO_UNIVERSE directly
                    meta = sym_meta.get(symbol, sym_meta.get(symbol + ".NS", {}))
                    sector = meta.get("sector", "")
                if not sector:
                    sector = ""  # Will display as "--" in GUI
                                
                vol_display = str(int(volume)) if volume > 0 else "--"
                mapping_time = (time.time() - tick_start) * 1000
                
                # Check for Signal/Trend Conflict
                if trend_str in ["BEAR", "BEARISH", "STRONG_BEAR"] and decision_str == "BUY":
                    logger.warning(f"Signal/Trend Conflict for {symbol}: Trend is {trend_display} but Signal is BUY.")
                
                # Attach data for Analysis Panel
                radar_analysis = getattr(r, "breakdown_detail", {}).get("Radar_Analysis", {})
                radar_analysis["Market Trend"] = pipeline_res.get("Market Trend", trend_display)
                pipeline_res["data"] = radar_analysis
                
                pipeline_res["institution_grade"] = getattr(r, "quality_grade", "N/A")
                pipeline_res["risk_level"] = "Medium" if score >= 60 else "High"
                pipeline_res["execution_time_ms"] = mapping_time
                
                logger.info(f"Swing Scanner mapped {symbol} in {mapping_time:.1f}ms")
                
                # BUG-02: Company name — use real name from universe, not just symbol
                company_raw = getattr(r, 'company_name', '')
                if not company_raw or company_raw == symbol:
                    meta = sym_meta.get(symbol, sym_meta.get(symbol + ".NS", {}))
                    company_raw = meta.get("company_name", symbol.replace(".NS", ""))
                
                # Confidence display: use real value, or "--" if not available
                conf_display = round(confidence, 1) if confidence and confidence > 0 else 0
                
                return {
                    "Symbol": symbol,
                    "Company": company_raw,
                    "Sector": sector,
                    "Price": round(price, 2),
                    "Signal": decision_str,
                    "Score": score,
                    "Raw Score": bullish_score,
                    "Confidence": conf_display,
                    "Trend": trend_display,
                    "Volume": vol_display,
                    "Risk Reward": f"1:{round(rr, 1)}" if isinstance(rr, (int, float)) else str(rr),
                    "Entry": round(entry, 2),
                    "Stop Loss": round(sl, 2),
                    "Target 1": round(t1, 2),
                    "Target 2": round(t2, 2),
                    "Trade Grade": "",   # filled by DEE below
                    "Risk Grade": "",    # filled by DEE below
                    "Execution Status": pipeline_res.get("execution_status", "NOT READY"),
                    "Execution Score": pipeline_res.get("execution_score", 0.0),
                    "Execution Reason": pipeline_res.get("execution_reason", ""),
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "_raw_data": pipeline_res,
                    "_reasons": pipeline_res.get("reasons", [])
                }
                
            import concurrent.futures
            import os
            adaptive_workers = min(32, (os.cpu_count() or 1) + 4)
            with concurrent.futures.ThreadPoolExecutor(max_workers=adaptive_workers) as executor:
                futures = [executor.submit(process_post_scan, r) for r in raw_results]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        res = future.result()
                        if res:
                            processed_results.append(res)
                    except Exception as e:
                        import traceback
                        logger.exception("process_post_scan failed")
                        traceback.print_exc()
                
            # --- QUALITY GATE & FILTER ENGINE ---
            qualified_results = []
            
            for item in processed_results:
                # 1. Parse Values
                try: score = float(item["Score"])
                except: score = 0.0
                try: conf = float(item["Confidence"])
                except: conf = 0.0
                try:
                    rr_str = str(item["Risk Reward"]).replace("1:", "").strip()
                    rr = float(rr_str) if rr_str and rr_str != "N/A" else 0.0
                except: rr = 0.0
                
                signal = item["Signal"]
                trend = item["Trend"]
                
                # 2. Hard Conditions (Strict AI Trade Decision Engine V1.0 rules)
                # Very weak setups are ignored entirely to avoid cluttering WATCH
                if score < 50.0 and conf < 50.0: continue
                if signal not in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL", "WATCH"]: continue
                
                # SPRINT-74 FIX: Strictness Modes & Confidence Gating
                mode = getattr(self.config, 'swing_signal_mode', 'Balanced')
                if mode == 'Conservative':
                    min_score = 80.0
                    min_conf = 75.0
                    min_rr = 2.0
                elif mode == 'Aggressive':
                    min_score = 70.0
                    min_conf = 65.0
                    min_rr = 1.5
                else: # Balanced
                    min_score = 75.0
                    min_conf = 70.0
                    min_rr = 1.8
                
                if signal in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
                    downgrade_reasons = []
                    
                    if conf < min_conf:
                        downgrade_reasons.append("Confidence below directional threshold")
                    if score < min_score:
                        downgrade_reasons.append(f"Score below directional threshold")
                    if rr < min_rr:
                        downgrade_reasons.append("RR below minimum threshold")
                        
                    if downgrade_reasons:
                        # signal = "WATCH"
                        print("Threshold Downgrade")
                        print("Score:", score)
                        print("Confidence:", conf)
                        print("RR:", rr)
                        print("Reasons:", downgrade_reasons)
                        # item["Signal"] = "WATCH"
                        if "_reasons" not in item:
                            item["_reasons"] = []
                        item["_reasons"].extend(downgrade_reasons)
                
                # PHASE 3: READY / SETUP Signal Promotion
                # If pipeline outputted WATCH (because breakout pending), but scores/RR are strong enough -> promote to READY
                if signal == "WATCH" and score >= min_score and conf >= min_conf and rr >= min_rr:
                    trend_upper = trend.upper()
                    if trend_upper in ["BULLISH", "STRONG BULLISH", "BULL", "BEARISH", "STRONG BEARISH", "BEAR"]:
                        # Validate the risk levels using inferred direction
                        inferred_dir = "BUY" if "BULL" in trend_upper else "SELL"
                        try: 
                            entry = float(item["Entry"])
                            sl = float(item["Stop Loss"])
                            t1 = float(item["Target 1"])
                        except: 
                            entry = 0; sl = 0; t1 = 0
                        
                        is_valid, _ = validate_trade_levels(inferred_dir, entry, sl, t1)
                        if is_valid:
                            signal = "READY"
                            item["Signal"] = "READY"
                            item["_reasons"] = ["Setup ready; waiting for breakout confirmation"]
                
                # SPRINT-75 FIX: Inject specific reasons for WATCH
                if item["Signal"] == "WATCH":
                    if "_reasons" not in item:
                        item["_reasons"] = []
                    
                    raw_data = item.get("_raw_data", {})
                    t_score = safe_float(raw_data.get("trend", {}).get("score", 50.0), 50.0)
                    m_score = safe_float(raw_data.get("momentum", {}).get("score", 50.0), 50.0)
                    s_score = safe_float(raw_data.get("sector_rotation", {}).get("score", 50.0), 50.0)
                    v_score = safe_float(raw_data.get("volume", {}).get("score", 50.0), 50.0)
                    
                    # Do not duplicate generic reason if we already have specific downgrade reasons
                    has_specific_downgrade = any(r for r in item["_reasons"] if "below directional threshold" in r or "Invalid" in r or "RR below" in r or "Downgraded to WATCH" in r)
                    
                    if not has_specific_downgrade:
                        if t_score < 50.0 and m_score < 50.0:
                            item["_reasons"].append("Trend and momentum not aligned")
                        elif s_score < 50.0:
                            item["_reasons"].append("Sector strength not aligned")
                        elif v_score < 50.0:
                            item["_reasons"].append("Volume confirmation missing")
                        else:
                            # It's a WATCH with good momentum/trend but maybe just low confidence/score
                            if score < min_score or conf < min_conf:
                                item["_reasons"].append("Valid structure but confidence/score too low")
                            else:
                                item["_reasons"].append("Waiting for better setup")
                                
                    # If trend is aligned but still WATCH, might just be pending breakout
                    if trend.upper() in ["BULLISH", "STRONG BULLISH", "BULL"] and "breakout" not in str(item["_reasons"]):
                        item["_reasons"].append("Trend aligned but breakout pending")
                    elif trend.upper() in ["BEARISH", "STRONG BEARISH", "BEAR"] and "breakdown" not in str(item["_reasons"]):
                        item["_reasons"].append("Trend aligned but breakdown pending")
                
                # 3. Generate "Why Selected" Bullet Points via DEE (MASTER-26)
                from core.decision_explanation_engine import DecisionExplanationEngine
                dee = DecisionExplanationEngine()
                
                raw_reasons = item.get("_reasons", [])
                dee_result = dee.explain(
                    signal=signal,
                    confidence=conf,
                    elite_score=score,
                    raw_reasons=raw_reasons
                )
                
                item["_why_selected"] = dee_result["Top Reasons"]
                item["Trade Grade"] = dee_result["Trade Grade"]
                item["Risk Grade"] = dee_result["Risk Grade"]
                qualified_results.append(item)
                
            # --- SORTING & RANKING via Trade Priority Engine (MASTER-28) ---
            from core.trade_priority_engine import TradePriorityEngine
            tpe = TradePriorityEngine()
            qualified_results = tpe.rank_trades(qualified_results)
            best_trades = []
            best_buy = next((item for item in qualified_results if "BUY" in item.get("Signal", "")), None)
            best_sell = next((item for item in qualified_results if "SELL" in item.get("Signal", "")), None)
            if best_buy:
                best_trades.append(best_buy)
            if best_sell:
                best_trades.append(best_sell)
            
            # --- MARKET OPPORTUNITY LEVEL ---
            num_qualified = len(qualified_results)
            if num_qualified >= 10: market_quality = "HIGH"
            elif num_qualified >= 4: market_quality = "MEDIUM"
            elif num_qualified > 0: market_quality = "LOW"
            else: market_quality = "NO TRADE"
            
            self.last_results = qualified_results
            exec_time = time.time() - start_time
            logger.info(f"Scan Completed. Scanned: {len(processed_results)}. Qualified: {num_qualified}. Market Quality: {market_quality}")
            
            if progress_callback:
                progress_callback(100)
                
            print("\n========== FIRST RESULT ==========")
            if qualified_results:
                from pprint import pprint
                pprint(qualified_results[0])
            print("==================================")

            from collections import Counter
            print(Counter(
                str(x.get("Signal", "<missing>"))
                for x in qualified_results
            ))

            scan_stats = getattr(scanner, "last_scan_stats", {})
            no_data_count = scan_stats.get("no_data", 0)
            error_count = scan_stats.get("errors", 0)
            wait_count = len(processed_results) - num_qualified

            return {
                "total_scanned": len(processed_results),
                "total_universe": len(stock_list),
                "qualified_results": qualified_results,
                "wait_count": wait_count,
                "no_data_count": no_data_count,
                "error_count": error_count,
                "best_trades": best_trades,
                "market_quality": market_quality,
                "exec_time": exec_time
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Errors occurred in Swing Scanner: {e}")
            logger.error(traceback.format_exc())
            if progress_callback:
                progress_callback(100)
            # Re-raise the exception to expose the error to the caller, preventing silent failure
            raise

    def export_csv(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            if not results:
                return ""
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Exclude hidden keys
            keys = [k for k in results[0].keys() if not str(k).startswith("_")]
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for r in results:
                    writer.writerow({k: r[k] for k in keys})
            logger.info(f"Export CSV successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export CSV failed: {e}")
            return ""

    def export_excel(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            if not results:
                return ""
            import pandas as pd
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            clean_results = [{k: v for k, v in r.items() if not str(k).startswith("_")} for r in results]
            df = pd.DataFrame(clean_results)
            df.to_excel(filepath, index=False)
            logger.info(f"Export Excel successful to {filepath}")
            return filepath
        except ImportError:
            logger.error("Export Excel failed: pandas or openpyxl not installed")
            return ""
        except Exception as e:
            logger.error(f"Export Excel failed: {e}")
            return ""

    def export_json(self, results: List[Dict[str, Any]], filepath: str) -> str:
        try:
            if not results:
                return ""
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            clean_results = [{k: v for k, v in r.items() if not str(k).startswith("_")} for r in results]
            with open(filepath, 'w') as f:
                json.dump(clean_results, f, indent=4)
            logger.info(f"Export JSON successful to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Export JSON failed: {e}")
            return ""
