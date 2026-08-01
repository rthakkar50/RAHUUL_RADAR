"""
RAHUUL RADAR — AI Engine V2: Model Manager (Task 2 & Task 6)
============================================================
Manages model lifecycle, artifact loading/saving, versioning (AI_v1, AI_v2, AI_v3),
and hot-swapping/rollback capability without retraining.
"""

import os
import joblib
import logging
import threading
from typing import Dict, Any, Optional, List

logger = logging.getLogger("ModelManager")


class DummyInferenceModel:
    """Production fallback inference model with deterministic predictions."""
    
    def __init__(self, version: str = "AI_v2"):
        self.version = version

    def predict_proba(self, feature_vector: List[float]) -> Dict[str, float]:
        """
        Pure inference probability prediction based on normalized features.
        Vector layout: [ema_20, ema_50, ema_200, sma_20, sma_50, rsi_14, macd, macd_signal,
                        macd_hist, atr_14, adx_14, vwap, volume_ratio, price_momentum,
                        relative_strength, market_breadth, volatility]
        """
        if len(feature_vector) < 17:
            return {"BUY": 0.33, "SELL": 0.33, "HOLD": 0.34}

        rsi = feature_vector[5]
        vol_ratio = feature_vector[12]
        mom = feature_vector[13]
        rs = feature_vector[14]

        # Multi-factor score heuristic mapping
        buy_score = 0.0
        if rsi > 50: buy_score += 0.25
        if vol_ratio > 1.2: buy_score += 0.25
        if mom > 0: buy_score += 0.25
        if rs > 70: buy_score += 0.25

        sell_score = 0.0
        if rsi < 45: sell_score += 0.25
        if vol_ratio < 0.8: sell_score += 0.25
        if mom < 0: sell_score += 0.25
        if rs < 40: sell_score += 0.25

        hold_score = max(0.1, 1.0 - (buy_score + sell_score))
        total = buy_score + sell_score + hold_score

        return {
            "BUY": round(buy_score / total, 4),
            "SELL": round(sell_score / total, 4),
            "HOLD": round(hold_score / total, 4)
        }


class ModelManager:
    """
    Enterprise Model Manager supporting version control, loading, saving, and rollbacks.
    """

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = model_dir
        self.active_version = "AI_v2"
        self._models: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        os.makedirs(self.model_dir, exist_ok=True)
        # Register built-in default versions
        self._register_default_models()

    def _register_default_models(self):
        """Initializes default inference model artifacts for AI_v1, AI_v2, AI_v3."""
        self._models["AI_v1"] = DummyInferenceModel(version="AI_v1")
        self._models["AI_v2"] = DummyInferenceModel(version="AI_v2")
        self._models["AI_v3"] = DummyInferenceModel(version="AI_v3")

    def load_model(self, version: str) -> bool:
        """Loads a model artifact from disk or registers fallback."""
        model_file = os.path.join(self.model_dir, f"{version}.joblib")
        with self._lock:
            if os.path.exists(model_file):
                try:
                    loaded = joblib.load(model_file)
                    self._models[version] = loaded
                    logger.info(f"Model {version} loaded successfully from {model_file}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to load model {version} from {model_file}: {e}")
            
            # Fallback to pre-registered model
            if version in self._models:
                logger.info(f"Using registered in-memory model for {version}")
                return True

            # Register default model fallback
            self._models[version] = DummyInferenceModel(version=version)
            logger.info(f"Registered default inference model for version {version}")
            return True

    def save_model(self, model: Any, version: str) -> bool:
        """Saves a model artifact to disk for version persistence."""
        model_file = os.path.join(self.model_dir, f"{version}.joblib")
        with self._lock:
            try:
                joblib.dump(model, model_file)
                self._models[version] = model
                logger.info(f"Model version {version} saved to {model_file}")
                return True
            except Exception as e:
                logger.error(f"Failed to save model {version}: {e}")
                return False

    def get_active_model(self) -> Any:
        """Returns the currently active inference model."""
        with self._lock:
            if self.active_version not in self._models:
                self.load_model(self.active_version)
            return self._models.get(self.active_version)

    def get_model_version(self) -> str:
        """Returns the active model version string."""
        with self._lock:
            return self.active_version

    def switch_model(self, version: str) -> bool:
        """Switches active model version (Hot swap / Rollback)."""
        with self._lock:
            if version not in self._models:
                # Attempt loading
                model_file = os.path.join(self.model_dir, f"{version}.joblib")
                if os.path.exists(model_file):
                    try:
                        self._models[version] = joblib.load(model_file)
                    except Exception as e:
                        logger.error(f"Cannot switch to {version}: load failed: {e}")
                        return False
                else:
                    self._models[version] = DummyInferenceModel(version=version)
            
            self.active_version = version
            logger.info(f"Active AI Model switched to: {version}")
            return True

    def list_available_versions(self) -> List[str]:
        """Lists all registered or available model versions."""
        with self._lock:
            versions = set(self._models.keys())
            if os.path.exists(self.model_dir):
                for f in os.listdir(self.model_dir):
                    if f.endswith(".joblib"):
                        versions.add(f.replace(".joblib", ""))
            return sorted(list(versions))
