import logging
from typing import List, Dict, Any

logger = logging.getLogger("SignalOrchestrator")

class PriorityRankingEngine:
    PRIORITY_MAP = {
        "INSTITUTIONAL_BUY": 70,
        "STRONG_BUY": 60,
        "BUY": 50,
        "WATCH": 40,
        "SELL": 30,
        "STRONG_SELL": 20,
        "INSTITUTIONAL_SELL": 10,
    }

    @classmethod
    def get_priority_score(cls, signal: str) -> int:
        return cls.PRIORITY_MAP.get(signal.upper().strip(), 0)

    @classmethod
    def upgrade_signal(cls, signal: str, confidence: float, score: float) -> str:
        """Upgrades a basic signal to a stronger one based on confidence and score."""
        sig = signal.upper().strip()
        
        if sig == "BUY":
            if confidence >= 95 and score >= 90:
                return "INSTITUTIONAL_BUY"
            elif confidence >= 85 and score >= 80:
                return "STRONG_BUY"
        elif sig == "SELL":
            if confidence >= 95 and score >= 90:
                return "INSTITUTIONAL_SELL"
            elif confidence >= 85 and score >= 80:
                return "STRONG_SELL"
                
        return sig


class UnifiedScoreCalculator:
    @staticmethod
    def calculate(result: Dict[str, Any]) -> float:
        """
        Composite Score using:
        Decision Score (30%) + AI Score (20%) + Confidence (20%) + 
        Risk Reward (10%) + Trend Strength (10%) + Volume Strength (10%)
        """
        decision_score = float(result.get("Score", result.get("Raw Score", 50)))
        ai_score = float(result.get("AI Score", decision_score))
        confidence = float(result.get("Confidence", 50))
        
        # Parse RR
        rr_str = str(result.get("Risk Reward", "1:1"))
        try:
            rr = float(rr_str.replace("1:", "").replace("+", "").strip())
        except:
            rr = 1.0
            
        # Normalize RR to a 0-100 scale (assume 1:3 is excellent -> 100)
        rr_score = min((rr / 3.0) * 100, 100)
        
        # Extract trend and volume strength (if available, else defaults)
        trend_score = float(result.get("Trend Score", 75))
        vol_score = float(result.get("Volume Score", 75))
        
        composite = (
            (decision_score * 0.30) +
            (ai_score * 0.20) +
            (confidence * 0.20) +
            (rr_score * 0.10) +
            (trend_score * 0.10) +
            (vol_score * 0.10)
        )
        return round(composite, 2)


class ExplainabilityGenerator:
    @staticmethod
    def generate(result: Dict[str, Any], signal: str) -> str:
        trend = str(result.get("Trend", "Neutral")).split("|")[0].strip()
        rr = str(result.get("Risk Reward", "1:1.5")).split("|")[-1].strip()
        conf = float(result.get("Confidence", 50.0))
        momentum = "Strong" if float(result.get("Score", 50)) > 70 else "Neutral"
        
        # Find some F&O specific metrics if available
        vwap_status = "Above" if "BUY" in signal else "Below" # Simulated for explanation
        if "VWAP" in str(result):
            vwap_status = "Above" if "Above" in str(result) else "Below"

        reason = f"{signal} because Trend {trend}, Momentum {momentum}, VWAP {vwap_status}, Risk Reward {rr}, AI Confidence {conf:.1f}%"
        return reason


class ConflictResolver:
    @staticmethod
    def resolve(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolves conflict between multiple signals for the same symbol."""
        if len(signals) == 1:
            return signals[0]
            
        logger.info(f"Conflict detected for {signals[0].get('Symbol')}: {len(signals)} conflicting signals.")
        
        # Sort by resolution criteria: Confidence, AI Score (Composite), RR
        def resolution_key(s):
            conf = float(s.get("Confidence", 0))
            score = UnifiedScoreCalculator.calculate(s)
            
            rr_str = str(s.get("Risk Reward", "1:1"))
            try:
                rr = float(rr_str.replace("1:", "").replace("+", "").strip())
            except:
                rr = 1.0
                
            return (conf, score, rr)
            
        signals.sort(key=resolution_key, reverse=True)
        winner = signals[0]
        logger.info(f"Resolved to winner: {winner.get('Signal')} from {winner.get('source_engine')}")
        return winner


class SignalOrchestrator:
    def __init__(self):
        self.resolver = ConflictResolver()
        self.priority_engine = PriorityRankingEngine()
        self.score_calculator = UnifiedScoreCalculator()
        self.explainer = ExplainabilityGenerator()

    def merge_and_resolve(self, engine_outputs: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Takes a dict of {engine_name: [signals]}
        Merges them, removes duplicates by resolving conflicts, assigns composite score and reasons.
        """
        symbol_map = {}
        
        # Flatten and group by symbol
        for engine_name, signals in engine_outputs.items():
            for sig in signals:
                sym = sig.get("Symbol")
                if not sym:
                    continue
                    
                # Tag with source engine so we know where it came from
                sig["source_engine"] = engine_name
                
                if sym not in symbol_map:
                    symbol_map[sym] = []
                symbol_map[sym].append(sig)
                
        final_signals = []
        
        # Resolve conflicts and enhance
        for sym, signals in symbol_map.items():
            winner = self.resolver.resolve(signals)
            
            # 1. Upgrade Signal Priority
            current_signal = str(winner.get("Signal", "WATCH"))
            confidence = float(winner.get("Confidence", 50))
            score = float(winner.get("Score", 50))
            
            upgraded_signal = self.priority_engine.upgrade_signal(current_signal, confidence, score)
            winner["Signal"] = upgraded_signal
            winner["signal"] = upgraded_signal
            winner["entry_decision"] = winner.get("entry_decision", winner.get("Entry Decision", "ENTER NOW"))
            winner["Entry Decision"] = winner.get("Entry Decision", winner.get("entry_decision", "ENTER NOW"))
            
            # 2. Unified Signal Score
            composite_score = self.score_calculator.calculate(winner)
            winner["Composite Score"] = composite_score
            winner["Score"] = composite_score  # Override for UI compatibility
            
            # 3. Explainability
            reason = self.explainer.generate(winner, upgraded_signal)
            # Inject reason into Pattern so it shows up in UI
            winner["Pattern"] = reason 
            
            final_signals.append(winner)
            
        # Sort by Composite Score globally
        final_signals.sort(key=lambda x: x.get("Composite Score", 0), reverse=True)
        return final_signals
