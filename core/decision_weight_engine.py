import os
import json
import logging

class DecisionWeightEngine:
    """
    Combines scores from all analysis modules into a single weighted score.
    """
    
    def __init__(self) -> None:
        self.weights = {}
        self.load_default_weights()
        
    def load_default_weights(self) -> None:
        """
        Loads configured weights from config/weights.json, falling back to 
        built-in default weights if missing or invalid.
        """
        # Built-in fallback weights
        fallback_weights = {
            "trend": 20,
            "momentum": 15,
            "volume": 10,
            "structure": 10,
            "risk": 15,
            "relative_strength": 10,
            "sector_rotation": 10,
            "option_chain": 5,
            "adaptive_strategy": 5,
            "master_ai": 10
        }
        
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/weights.json"))
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    loaded_weights = json.load(f)
                if isinstance(loaded_weights, dict):
                    # Load, cast values to floats, and standardize keys to lowercase
                    self.weights = {str(k).lower(): float(v) for k, v in loaded_weights.items()}
                    return
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger = logging.getLogger("DecisionWeightEngine")
                logger.error(f"Failed to parse weights.json: {e}. Falling back to built-in weights.")
                
        # Default fallback
        self.weights = fallback_weights
        
    def set_weight(self, engine_name: str, weight: float) -> None:
        """
        Updates the weight for a specific engine.
        """
        self.weights[engine_name.lower()] = weight
        
    def get_weight(self, engine_name: str) -> float:
        """
        Retrieves the weight for a specific engine.
        """
        return self.weights.get(engine_name.lower(), 0.0)
        
    def calculate_weighted_score(self, results: dict) -> float:
        """
        Calculates the normalized weighted score based on the provided results.
        
        Args:
            results: A dictionary of scores (0-100) per engine.
                     e.g. {'trend': 85, 'momentum': 72}
                     
        Returns:
            float: The final weighted score (0-100).
        """
        if not results:
            return 0.0
            
        total_weight = 0.0
        total_score = 0.0
        
        for engine, res in results.items():
            if res is None:
                continue
                
            score = 50.0
            if isinstance(res, (int, float)):
                score = float(res)
            elif hasattr(res, "score"):
                try: score = float(res.score)
                except: score = 50.0
            elif isinstance(res, dict) and "score" in res:
                try: score = float(res["score"])
                except: score = 50.0
                
            weight = self.get_weight(engine)
            if weight > 0:
                total_score += (score * weight)
                total_weight += weight
                
        # Normalize to 0-100 scale and round to 2 decimal places
        if total_weight > 0:
            return round(total_score / total_weight, 2)
        return 0.0
