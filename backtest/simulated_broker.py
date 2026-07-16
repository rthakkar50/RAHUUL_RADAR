from datetime import datetime, timedelta
from typing import List, Dict, Any
import yfinance as yf
from utils.logger import get_logger

logger = get_logger(__name__)

class SimulatedBroker:
    """
    Evaluates the performance of generated trading signals by calculating
    realistic simulated trades (Entry, Target, Stop Loss, End of Holding Period).
    """
    
    def __init__(self):
        pass

    def execute_trades(self, results: List[Dict[str, Any]], n_days: int = 10) -> List[Dict[str, Any]]:
        """
        Takes a list of dictionaries containing fully processed trade signals and evaluates them.
        Returns the evaluated trades ledger.
        """
        logger.info(f"Starting Simulated Broker on {len(results)} signals (Max Hold: {n_days} days)...")
        
        symbols = set(r["Symbol"] for r in results)
        if not symbols:
            logger.warning("No signals to evaluate.")
            return []
            
        earliest_date = min(r["Date"] for r in results)
        
        start_fetch = (earliest_date - timedelta(days=5)).strftime("%Y-%m-%d")
        end_fetch = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        price_data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_fetch, end=end_fetch, interval="1d")
                if not df.empty and df.index.tz is not None:
                    df.index = df.index.tz_localize(None)
                price_data[symbol] = df
            except Exception as e:
                logger.error(f"Failed to fetch evaluation data for {symbol}: {e}")
                
        evaluated_trades = []
        
        for r in results:
            decision = r["Signal"]
            
            # Simulator only trades BUY and SELL
            if decision not in ["BUY", "SELL"]:
                continue
                
            df = price_data.get(r["Symbol"])
            if df is None or df.empty:
                continue
                
            signal_date = r["Date"].date() if isinstance(r["Date"], datetime) else r["Date"]
            if hasattr(signal_date, 'date'):
                signal_date = signal_date.date()
                
            # Future data strictly AFTER the signal day
            future_df = df[df.index.date > signal_date]
            
            if len(future_df) == 0:
                continue
                
            # Planned Entry/Targets from Pipeline
            pipeline_entry = r["Entry Price"]
            sl = r["Stop Loss"]
            t1 = r["Target 1"]
            t2 = r["Target 2"]
            
            # Attempt Entry on Day 1
            day1 = future_df.iloc[0]
            day1_open = float(day1['Open'])
            day1_low = float(day1['Low'])
            day1_high = float(day1['High'])
            
            actual_entry = 0.0
            
            if decision == "BUY":
                if day1_open <= pipeline_entry:
                    actual_entry = day1_open
                elif day1_low <= pipeline_entry:
                    actual_entry = pipeline_entry
                else:
                    # Gap up beyond entry, ignore trade
                    continue
            else: # SELL
                if day1_open >= pipeline_entry:
                    actual_entry = day1_open
                elif day1_high >= pipeline_entry:
                    actual_entry = pipeline_entry
                else:
                    # Gap down beyond entry, ignore trade
                    continue
                    
            # Trade is active
            active = True
            exit_price = 0.0
            actual_holding_days = 0
            exit_reason = "Max Hold Time"
            
            for i in range(len(future_df)):
                if not active:
                    break
                    
                if i >= n_days:
                    # Force exit at Open of the next day or Close of n_days if that's easier
                    exit_price = float(future_df.iloc[i]['Close'])
                    actual_holding_days = i
                    exit_reason = "Time Stop"
                    active = False
                    break
                    
                current_day = future_df.iloc[i]
                c_open = float(current_day['Open'])
                c_high = float(current_day['High'])
                c_low = float(current_day['Low'])
                c_close = float(current_day['Close'])
                
                actual_holding_days += 1
                
                if decision == "BUY":
                    # Check Gap Down Stop Loss
                    if c_open <= sl:
                        exit_price = c_open
                        exit_reason = "Stop Loss (Gap Down)"
                        active = False
                    # Check Intraday Stop Loss
                    elif c_low <= sl:
                        exit_price = sl
                        exit_reason = "Stop Loss Hit"
                        active = False
                    # Check Target 2
                    elif c_high >= t2:
                        exit_price = t2
                        exit_reason = "Target 2 Hit"
                        active = False
                    # Check Gap Up Target 2
                    elif c_open >= t2:
                        exit_price = c_open
                        exit_reason = "Target 2 (Gap Up)"
                        active = False
                elif decision == "SELL":
                    if c_open >= sl:
                        exit_price = c_open
                        exit_reason = "Stop Loss (Gap Up)"
                        active = False
                    elif c_high >= sl:
                        exit_price = sl
                        exit_reason = "Stop Loss Hit"
                        active = False
                    elif c_low <= t2:
                        exit_price = t2
                        exit_reason = "Target 2 Hit"
                        active = False
                    elif c_open <= t2:
                        exit_price = c_open
                        exit_reason = "Target 2 (Gap Down)"
                        active = False
                        
            if active:
                # Still holding at end of available data
                exit_price = float(future_df.iloc[-1]['Close'])
                exit_reason = "Live Trade (Mark to Market)"
                actual_holding_days = len(future_df)
                
            # Calculate Return %
            if decision == "BUY":
                ret_pct = ((exit_price - actual_entry) / actual_entry) * 100.0
            else:
                ret_pct = ((actual_entry - exit_price) / actual_entry) * 100.0
                
            if ret_pct > 0:
                win_loss = "WIN"
            elif ret_pct < 0:
                win_loss = "LOSS"
            else:
                win_loss = "BREAKEVEN"
            
            d_obj = r["Date"]
            if hasattr(d_obj, 'strftime'):
                d_str = d_obj.strftime("%Y-%m-%d")
            else:
                d_str = str(d_obj)
                
            evaluated_trades.append({
                "Date": d_str,
                "Symbol": r["Symbol"],
                "Signal": decision,
                "Pipeline Entry": pipeline_entry,
                "Actual Entry": actual_entry,
                "Exit Price": exit_price,
                "Exit Reason": exit_reason,
                "Holding Days": actual_holding_days,
                "Return %": ret_pct,
                "Win / Loss": win_loss,
                "Trend Score": r.get("Trend Score", 0),
                "Momentum Score": r.get("Momentum Score", 0),
                "Structure Score": r.get("Structure Score", 0),
                "Raw Score": r.get("Raw Score", 0),
                "Adjusted Score": r.get("Adjusted Score", 0),
                "Confidence": r.get("Confidence", 0)
            })
            
        return evaluated_trades
