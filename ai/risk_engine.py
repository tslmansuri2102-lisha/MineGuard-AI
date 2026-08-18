"""
MineGuard AI — Risk Prediction Engine
Coordinates feature extraction, multi-criteria risk modeling, explainability,
and safety recommendations.
"""

from typing import Any, Dict, Optional

from ai.config import (
    PredictionStatus,
    RiskLevel,
    RECOMMENDED_ACTIONS,
    DEGRADED_DATA_ACTION,
    score_to_risk_level,
)
from ai.explainability import ExplainabilityEngine
from ai.features import FeatureExtractor
from ai.model import BaseRiskModel, RuleBasedRiskModel
from simulation.validation import validate_reading


class RiskEngine:
    """
    Core AI Risk Assessment Engine for MineGuard AI.
    Processes live sensor readings into comprehensive geotechnical risk predictions.
    """

    def __init__(self, model: Optional[BaseRiskModel] = None, window_size: int = 10):
        self.feature_extractor = FeatureExtractor(window_size=window_size)
        self.model: BaseRiskModel = model or RuleBasedRiskModel()
        self.explainer = ExplainabilityEngine()

    def evaluate_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a raw sensor telemetry payload and returns a comprehensive risk prediction.
        
        Args:
            reading: Dictionary conforming to API_CONTRACT.md schema.
            
        Returns:
            Dictionary containing risk score, level, confidence, factors, and action.
        """
        # Validate reading structure
        validate_reading(reading)

        mine_id = reading.get("mine_id", "MINE-001")
        zone_id = reading.get("zone_id", "ZONE-003")
        sensor_id = reading.get("sensor_id", "SENSOR-003")
        timestamp = reading.get("timestamp", "")

        # 1. Feature Extraction
        features, metadata = self.feature_extractor.extract(reading)

        # 2. Risk Model Execution
        risk_score, confidence, status = self.model.predict(features, metadata)

        # 3. Categorical Risk Level
        risk_level = score_to_risk_level(risk_score)

        # 4. Explainability Attribution
        factors = self.explainer.explain(features, risk_score)

        # 5. Recommended Safety Action
        if status == PredictionStatus.DEGRADED:
            recommended_action = DEGRADED_DATA_ACTION
        else:
            recommended_action = RECOMMENDED_ACTIONS.get(risk_level, "Continue normal monitoring.")

        return {
            "mine_id": mine_id,
            "zone_id": zone_id,
            "sensor_id": sensor_id,
            "timestamp": timestamp,
            "risk_score": float(risk_score),
            "risk_level": risk_level.value,
            "confidence": float(confidence),
            "status": status.value,
            "factors": factors,
            "recommended_action": recommended_action,
        }

    def reset(self, mine_id: Optional[str] = None, zone_id: Optional[str] = None, sensor_id: Optional[str] = None) -> None:
        """Resets the internal feature buffers."""
        self.feature_extractor.reset(mine_id, zone_id, sensor_id)


# Global default risk engine instance
risk_engine = RiskEngine()
