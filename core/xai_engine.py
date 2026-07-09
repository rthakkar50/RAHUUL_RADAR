class ExplainableAIEngine:
    """
    EXPLAINABLE AI ENGINE (XAI)
    Generates a human-readable Decision Explanation Panel detailing exactly WHY
    a symbol was given a BUY, SELL, WATCH, or REJECT status, without modifying
    any underlying trading logic or thresholds.
    """
    
    def generate_panel(self, data: dict) -> str:
        """
        Takes a comprehensive dictionary of pipeline results and formats the XAI Panel.
        
        Expected keys in data:
        - symbol (str)
        - decision (str)
        - score (float)
        - confidence (float)
        - tqi (float)
        - engines: dict containing sub-dictionaries for each engine:
            - trend (pass, score, reason)
            - momentum (pass, score, reason)
            - structure (pass, score, reason)
            - adx (pass, current, required)
            - avwap (pass, reason)
            - volume (pass, reason)
            - relative_strength (pass, reason)
            - sector (pass, reason)
            - smart_money (pass, reason)
            - market_regime (pass, reason)
            - risk_reward (pass, rr)
            - institutional_validation (pass, reason)
            - false_breakout (pass, reason)
            - elite_selection (pass, reason)
        """
        decision = str(data.get("decision", "WATCH")).upper()
        score = data.get("score", 0.0)
        conf = data.get("confidence", 0.0)
        tqi = data.get("tqi", 0.0)
        
        engines = data.get("engines", {})
        
        lines = []
        lines.append("====================================================")
        lines.append("EXPLAINABLE AI DECISION PANEL")
        lines.append(f"SYMBOL: {data.get('symbol', 'UNKNOWN')}")
        lines.append("====================================================")
        lines.append(f"Overall Decision: {decision}")
        lines.append(f"Overall Score:    {score:.2f}")
        lines.append(f"Confidence:       {conf:.2f}%")
        lines.append("====================================================")
        
        # Helper to format PASS/FAIL
        def pf(passed: bool) -> str:
            return "PASS" if passed else "FAIL"

        # 1. Trend Engine
        te = engines.get("trend", {})
        lines.append("Trend Engine")
        lines.append(pf(te.get("pass", False)))
        lines.append(f"Score: {te.get('score', 0)}")
        lines.append(f"Reason: {te.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 2. Momentum Engine
        me = engines.get("momentum", {})
        lines.append("Momentum Engine")
        lines.append(pf(me.get("pass", False)))
        lines.append(f"Score: {me.get('score', 0)}")
        lines.append(f"Reason: {me.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 3. Structure Engine
        se = engines.get("structure", {})
        lines.append("Structure Engine")
        lines.append(pf(se.get("pass", False)))
        lines.append(f"Score: {se.get('score', 0)}")
        lines.append(f"Reason: {se.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 4. ADX
        adx = engines.get("adx", {})
        lines.append("ADX")
        lines.append(f"Current Value: {adx.get('current', 0.0)}")
        lines.append(f"Required Value: {adx.get('required', '>22')}")
        lines.append(pf(adx.get("pass", False)))
        lines.append("--------------------------")
        
        # 5. Anchored VWAP
        av = engines.get("avwap", {})
        lines.append("Anchored VWAP")
        lines.append(pf(av.get("pass", False)))
        lines.append(f"Reason: {av.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 6. Volume
        ve = engines.get("volume", {})
        lines.append("Volume")
        lines.append(pf(ve.get("pass", False)))
        lines.append(f"Reason: {ve.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 7. Relative Strength
        rs = engines.get("relative_strength", {})
        lines.append("Relative Strength")
        lines.append(pf(rs.get("pass", False)))
        lines.append(f"Reason: {rs.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 8. Sector Strength
        sec = engines.get("sector", {})
        lines.append("Sector Strength")
        lines.append(pf(sec.get("pass", False)))
        lines.append(f"Reason: {sec.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 9. Smart Money
        sm = engines.get("smart_money", {})
        lines.append("Smart Money")
        lines.append(pf(sm.get("pass", False)))
        lines.append(f"Reason: {sm.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 10. Market Regime
        mr = engines.get("market_regime", {})
        lines.append("Market Regime")
        lines.append(pf(mr.get("pass", False)))
        lines.append(f"Reason: {mr.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 11. Risk Reward
        rr = engines.get("risk_reward", {})
        lines.append("Risk Reward")
        lines.append(pf(rr.get("pass", False)))
        lines.append(f"RR: {rr.get('rr', 'N/A')}")
        lines.append("--------------------------")
        
        # 12. Institutional Validation
        iv = engines.get("institutional_validation", {})
        lines.append("Institutional Validation")
        lines.append(pf(iv.get("pass", False)))
        lines.append(f"Reason: {iv.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 13. False Breakout
        fb = engines.get("false_breakout", {})
        lines.append("False Breakout")
        lines.append(pf(fb.get("pass", False)))
        lines.append(f"Reason: {fb.get('reason', 'N/A')}")
        lines.append("--------------------------")
        
        # 14. Elite Selection
        es = engines.get("elite_selection", {})
        lines.append("Elite Selection")
        lines.append(pf(es.get("pass", False)))
        lines.append(f"Reason: {es.get('reason', 'N/A')}")
        lines.append("====================================================")
        
        # Highlight Logic Based on Decision
        if decision in ["REJECT", "WATCH", "WAIT"]:
            lines.append("Rejected because")
            
            recommendations = []
            
            def get_missing_str(current, required_val):
                missing = round(required_val - current, 1)
                return f"Missing +{missing}" if missing > 0 else f"Missing {missing}"
                
            near_elite = False
            
            # ADX
            if not adx.get("pass", True):
                try:
                    req_val = float(str(adx.get('required', '>22')).replace('>', '').replace('<', '').replace('=', '').strip())
                    curr_val = float(adx.get('current', 0))
                    dist = get_missing_str(curr_val, req_val)
                    sev = "Medium"
                    if req_val - curr_val <= 2: sev = "Minor"
                    elif req_val - curr_val > 5: sev = "Critical"
                    lines.append(f"❌ [{sev}] ADX {curr_val} / {req_val}")
                    lines.append(dist)
                    recommendations.append("Wait for ADX expansion.")
                except:
                    lines.append(f"❌ [Medium] ADX {adx.get('current', 0)}")
                    lines.append(f"Required {adx.get('required', '>22')}")
            
            # Confidence
            if conf < 60.0:
                dist = get_missing_str(conf, 60.0)
                sev = "Medium"
                if 60.0 - conf <= 3: sev = "Minor"
                elif 60.0 - conf > 10: sev = "Critical"
                lines.append(f"❌ [{sev}] Confidence {conf:.0f} / 60")
                lines.append(dist)
                recommendations.append("Wait for confidence confirmation.")
                
            # TQI
            if tqi < 85.0:
                dist = get_missing_str(tqi, 85.0)
                sev = "Critical"
                if 85.0 - tqi <= 4.25: # 5% of 85
                    sev = "Minor"
                    near_elite = True
                elif 85.0 - tqi <= 10:
                    sev = "Medium"
                    
                lines.append(f"❌ [{sev}] TQI {tqi:.0f} / 85")
                lines.append(dist)
                if not near_elite:
                    recommendations.append("Wait for Elite Engine promotion.")
                
            def add_engine_fail(engine_data, name, sev, rec):
                if not engine_data.get("pass", True):
                    lines.append(f"❌ [{sev}] {name}: {engine_data.get('reason', 'Failed')}")
                    if rec not in recommendations:
                        recommendations.append(rec)
                        
            add_engine_fail(te, "Trend Engine", "Critical", "Wait for trend alignment.")
            add_engine_fail(me, "Momentum Engine", "Medium", "Wait for momentum confirmation.")
            add_engine_fail(se, "Structure Engine", "Critical", "Monitor structure breakout.")
            add_engine_fail(av, "Anchored VWAP", "Medium", "Wait for AVWAP support.")
            add_engine_fail(ve, "Volume", "Medium", "Watch for volume breakout.")
            add_engine_fail(rs, "Relative Strength", "Minor", "Monitor relative strength.")
            add_engine_fail(sec, "Sector Strength", "Minor", "Wait for sector tailwind.")
            add_engine_fail(sm, "Smart Money", "Medium", "Watch for institutional footprints.")
            add_engine_fail(mr, "Market Regime", "Medium", "Wait for regime shift.")
            add_engine_fail(rr, "Risk Reward", "Critical", "Wait for better RR entry.")
            add_engine_fail(iv, "Institutional Validation", "Medium", "Wait for institutional validation.")
            add_engine_fail(fb, "False Breakout", "Critical", "Wait for trap clearance.")
            
            # Special Elite Selection logic
            if not es.get("pass", True) and "TQI" not in "".join(lines):
                lines.append(f"❌ [Critical] Elite Selection: {es.get('reason', 'Failed')}")
                recommendations.append("Wait for Elite Selection metrics to align.")
            
            if near_elite:
                lines.append("--------------------------")
                lines.append("🟡 Near Elite")
                lines.append("Likely to qualify within the next 1–3 candles")
                recommendations.append("Monitor next candle.")
                
            lines.append("--------------------------")
            lines.append("Recommendation Engine")
            if recommendations:
                if "Monitor next candle." in recommendations:
                    lines.append("Monitor next candle.")
                else:
                    lines.append(recommendations[0])
            else:
                lines.append("Monitor next candle.")

            lines.append("====================================================")
            
        elif decision in ["BUY", "SELL"]:
            lines.append("Strengths")
            if te.get("pass", False): lines.append("Trend ✔")
            if me.get("pass", False): lines.append("Momentum ✔")
            if se.get("pass", False): lines.append("Structure ✔")
            if ve.get("pass", False): lines.append("Volume ✔")
            if sm.get("pass", False): lines.append("Smart Money ✔")
            if rr.get("pass", False): lines.append("Risk Reward ✔")
            if adx.get("pass", False): lines.append("ADX ✔")
            if iv.get("pass", False): lines.append("Institutional Validation ✔")
            if es.get("pass", False): lines.append("Elite Selection ✔")
            lines.append("====================================================")
            
        return "\n".join(lines)
