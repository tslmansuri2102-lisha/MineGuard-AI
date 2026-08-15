"""
MineGuard AI — Real-Time ML Inference Engine
"""

from typing import Dict, Any
from inference.model_loader import ModelLoader
from inference.feature_adapter import FeatureAdapter
from ml.utils import logger


class RealTimePredictor:
    """
    Inference Engine providing clean interface for evaluating telemetry events against ML model.
    """
    def __init__(self, model_version: str = "v1.0.0-baseline"):
        self.model_version = model_version
        self.adapter = FeatureAdapter()
        self.preprocessor, self.model = ModelLoader.load_artifacts()

    def predict(self, telemetry: dict, rolling_features: dict = None) -> Dict[str, Any]:
        """
        Execute ML model inference on incoming telemetry.
        
        Returns:
            dict: {
                "ml_probability": float,
                "ml_class": int,
                "model_version": str,
                "status": str
            }
        """
        # Ensure artifacts are loaded
        if self.preprocessor is None or self.model is None:
            self.preprocessor, self.model = ModelLoader.load_artifacts()

        # Fallback if model artifacts are unavailable
        if self.preprocessor is None or self.model is None:
            logger.warning("ML Model artifact unavailable. Using fallback heuristic inference.")
            # Heuristic fallback based on rainfall & displacement
            rain = telemetry.get("rainfall_mm", 0.0)
            disp = telemetry.get("displacement_mm", 0.0)
            fallback_prob = min(1.0, (rain / 200.0) * 0.5 + (disp / 300.0) * 0.5)
            return {
                "ml_probability": float(round(fallback_prob, 4)),
                "ml_class": int(fallback_prob >= 0.5),
                "model_version": f"{self.model_version}-fallback",
                "status": "DEGRADED"
            }

        try:
            # 1. Adapt telemetry into ML feature schema
            df_features = self.adapter.adapt_telemetry_to_ml_features(telemetry, rolling_features)
            
            # 2. Transform through preprocessor
            X_proc = self.preprocessor.transform(df_features)
            
            # 3. Model inference
            ml_prob = float(self.model.predict_proba(X_proc)[0])
            ml_class = int(ml_prob >= 0.5)
            
            return {
                "ml_probability": float(round(ml_prob, 4)),
                "ml_class": ml_class,
                "model_version": self.model_version,
                "status": "SUCCESS"
            }
        except Exception as e:
            logger.error("Inference execution failed: %s", e)
            return {
                "ml_probability": 0.0,
                "ml_class": 0,
                "model_version": f"{self.model_version}-error",
                "status": "ERROR"
            }
