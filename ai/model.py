"""
MineGuard AI — Risk Prediction Model Interface & Baseline Geotechnical Engine
Implements extensible BaseRiskModel architecture with a multi-criteria geotechnical engine.
"""

from abc import ABC, abstractmethod
import math
from typing import Any, Dict, Tuple

from ai.config import PredictionStatus, RiskLevel, score_to_risk_level


class BaseRiskModel(ABC):
    """
    Abstract Base Class for MineGuard risk prediction models.
    Enables plug-and-play replacement with trained ML models (RandomForest, XGBoost, etc.).
    """

    @abstractmethod
    def predict(
        self,
        features: Dict[str, float],
        metadata: Dict[str, Any],
    ) -> Tuple[float, float, PredictionStatus]:
        """
        Calculates risk score, confidence, and prediction status.

        Args:
            features: Extracted numerical features dictionary.
            metadata: Quality and buffer metadata.

        Returns:
            Tuple of (risk_score, confidence, status):
                risk_score: float in [0.0, 100.0]
                confidence: float in [0.0, 1.0]
                status: PredictionStatus enum
        """
        pass


class RuleBasedRiskModel(BaseRiskModel):
    """
    Deterministic multi-criteria geotechnical risk evaluation model.
    Evaluates slope instability using coupled rock mechanics principles:
    - Kinematic displacement magnitude, velocity, and acceleration
    - Groundwater pore pressure and hydraulic head
    - Rainfall intensity and infiltration
    - Dynamic blasting / seismic vibration load
    - Rock mass shear strain
    """

    def predict(
        self,
        features: Dict[str, float],
        metadata: Dict[str, Any],
    ) -> Tuple[float, float, PredictionStatus]:
        # Handle sensor failure / zeroed telemetry dropout
        if metadata.get("is_zero_signal", False):
            # Degraded status with low confidence
            return 10.0, 0.20, PredictionStatus.DEGRADED

        # Check history completeness
        has_history = metadata.get("has_history", False)
        base_confidence = 0.95 if has_history else 0.80
        status = PredictionStatus.NORMAL if has_history else PredictionStatus.INSUFFICIENT_DATA

        disp = features.get("displacement_mm", 4.2)
        disp_rate = features.get("displacement_rate", 0.0)
        disp_accel = features.get("displacement_accel", 0.0)
        pore = features.get("pore_pressure_kpa", 31.5)
        pore_rate = features.get("pore_pressure_rate", 0.0)
        rain = features.get("rainfall_mm", 3.2)
        vib = features.get("vibration_g", 0.18)
        strain = features.get("strain", 0.21)

        # 1. Displacement sub-score (0-100)
        disp_mag_score = min(100.0, max(0.0, (disp - 4.0) * 5.0))
        disp_rate_score = min(100.0, max(0.0, disp_rate * 30.0))
        disp_accel_score = min(100.0, max(0.0, disp_accel * 40.0))
        disp_comp = 0.45 * disp_mag_score + 0.40 * disp_rate_score + 0.15 * disp_accel_score

        # 2. Pore Water Pressure sub-score (0-100)
        pore_excess = max(0.0, pore - 31.0)
        pore_score = min(100.0, pore_excess * 3.5 + max(0.0, pore_rate * 6.0))

        # 3. Rainfall sub-score (0-100)
        rain_excess = max(0.0, rain - 3.0)
        rain_score = min(100.0, rain_excess * 2.0)

        # 4. Vibration sub-score (0-100)
        vib_excess = max(0.0, vib - 0.18)
        vib_score = min(100.0, vib_excess * 80.0)

        # 5. Strain sub-score (0-100)
        strain_excess = max(0.0, strain - 0.20)
        strain_score = min(100.0, strain_excess * 200.0)

        # Weighted baseline aggregation
        raw_score = (
            0.35 * disp_comp
            + 0.25 * pore_score
            + 0.15 * rain_score
            + 0.15 * vib_score
            + 0.10 * strain_score
        )

        # Dominant threat envelope (prevents severe single hazards like high vibration or severe creep from being suppressed)
        dominant_threat = max(
            disp_comp * 0.85,
            vib_score * 0.65,
            pore_score * 0.70,
            strain_score * 0.70,
            rain_score * 0.50,
        )
        raw_score = max(raw_score, dominant_threat)

        # Synergistic non-linear compound coupling (when multiple hazards coincide)
        if disp_comp > 25.0 and pore_score > 25.0:
            raw_score += 15.0  # Infiltration-induced shear failure synergy
        if disp_comp > 25.0 and vib_score > 25.0:
            raw_score += 15.0  # Dynamic blast/seismic failure synergy
        if pore_score > 30.0 and rain_score > 30.0:
            raw_score += 10.0  # Extreme storm infiltration synergy
        if disp_rate > 1.8:
            raw_score += 18.0  # Tertiary creep collapse threshold

        final_score = min(100.0, max(0.0, raw_score))

        # Clamp confidence to valid [0.0, 1.0]
        confidence = min(1.0, max(0.0, base_confidence))

        return round(final_score, 2), round(confidence, 2), status
