import os

file_path = "/Users/pr/RAHUUL_RADAR/backtest/backtest_engine.py"
with open(file_path, "r") as f:
    content = f.read()

# Instead of patching small parts, let's just write the whole class BacktestEngine newly
start_idx = content.find("class BacktestEngine:")

new_engine_class = """class BacktestEngine:
    \"\"\"
    Executes the Unified Ranking Engine over historical data.
    \"\"\"
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def run_backtest(self, symbol_list: List[str], start_date: str, end_date: str, timeframe: str = "1d", hold_days: int = 10, mode: str = "SWING"):
        start_time = time.time()
        
        print("\\n======================================================================")
        print(f"Backtest Synchronization Started")
        print(f"Symbols: {len(symbol_list)}")
        print(f"Period:  {start_date} to {end_date}")
        print("======================================================================")
        print("Initializing Unified Ranking Engine...")
        
        from strategy.ranking_engine import RankingEngine
        ranking_engine = RankingEngine()
        
        # We need a dedicated BacktestDataProvider capable of caching multiple symbols (e.g. Sectors, Nifty)
        data_provider = BacktestDataProvider(start_date, end_date, timeframe)
        data_provider._fetch_symbol("^NSEI")
        for sym in ["BANKNIFTY.NS", "NIFTYIT.NS", "NIFTYAUTO.NS", "NIFTYFMCG.NS", "NIFTYMETAL.NS", "NIFTYPHARMA.NS"]:
            data_provider._fetch_symbol(sym)
        
        all_signals = []
        
        for idx, symbol in enumerate(symbol_list):
            try:
                data_provider.set_main_symbol(symbol)
                main_df = data_provider.cache.get(symbol)
                if main_df is None or main_df.empty:
                    continue
            except Exception as e:
                logger.error(f"Failed to initialize backtest data for {symbol}: {e}")
                continue
                
            min_lookback = 50
            trading_days = len(main_df)
            
            if trading_days <= min_lookback:
                logger.error(f"Insufficient data for {symbol}.")
                continue
                
            for i in range(min_lookback, trading_days):
                data_provider.current_date_index = i
                current_date = main_df.index[i]
                
                # Fetch rolling slices up to current date (simulating live feed)
                df_slice_1d = data_provider.get_ohlcv(symbol, "1d")
                df_slice_intra = data_provider.get_ohlcv(symbol, timeframe)
                
                if not df_slice_1d or not df_slice_intra:
                    continue
                    
                res = ranking_engine.evaluate(symbol, df_slice_intra, df_slice_1d)
                
                if res["status"] == "RANKED":
                    final_decision = res["direction"]
                    score = res["score"]
                    
                    if score >= 70.0:  # Good+ Grade gets executed in Backtest
                        # Basic entry logic simulation since we bypassed PrecisionEntryEngine
                        price = float(df_slice_intra[-1].close)
                        entry = price
                        sl = price * 0.98
                        t1 = price * 1.02
                        t2 = price * 1.05
                        
                        all_signals.append({
                            "Date": current_date,
                            "Symbol": symbol,
                            "Signal": "BUY" if final_decision == "BULLISH" else "SELL",
                            "Entry Price": entry,
                            "Stop Loss": sl,
                            "Target 1": t1,
                            "Target 2": t2,
                            "Trend Score": res["engine_breakdown"].get("Trend", {}).get("Score Contribution", 0),
                            "Momentum Score": res["engine_breakdown"].get("Momentum", {}).get("Score Contribution", 0),
                            "Structure Score": res["engine_breakdown"].get("VWAP", {}).get("Score Contribution", 0),
                            "Raw Score": res["raw_score"],
                            "Adjusted Score": score,
                            "Confidence": res["confidence"]
                        })
                    
            # Print Progress
            progress = ((idx + 1) / len(symbol_list)) * 100
            sys.stdout.write(f"\\rProgress: {progress:.1f}%")
            sys.stdout.flush()
            
        sys.stdout.write("\\nCompleted Pipeline Execution\\n")
        exec_time = time.time() - start_time
        print(f"Pipeline executed in {exec_time:.2f} seconds.")
        
        return all_signals
"""

content = content[:start_idx] + new_engine_class
with open(file_path, "w") as f:
    f.write(content)
