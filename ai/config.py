"""
MineGuard AI — AI Risk Prediction Engine Configuration
Defines risk score thresholds, categorical risk levels, data quality statuses,
and standard recommended safety actions.
"""

from enum import Enum
from typing import Dict, Tuple


class RiskLevel(str, Enum):
    """Categorical risk levels matching API_CONTRACT.md conventions."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PredictionStatus(str, Enum):
    """Data quality and operational status of a prediction."""
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# Score threshold boundaries: [min_score, max_score]
RISK_LEVEL_THRESHOLDS: Dict[RiskLevel, Tuple[float, float]] = {
    RiskLevel.LOW: (0.0, 29.99),
    RiskLevel.MODERATE: (30.0, 59.99),
    RiskLevel.HIGH: (60.0, 79.99),
    RiskLevel.CRITICAL: (80.0, 100.0),
}


def score_to_risk_level(score: float) -> RiskLevel:
    """Maps a 0-100 risk score to its corresponding RiskLevel enum."""
    clamped_score = max(0.0, min(100.0, score))
    if clamped_score < 30.0:
        return RiskLevel.LOW
    elif clamped_score < 60.0:
        return RiskLevel.MODERATE
    elif clamped_score < 80.0:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


# Prototype recommended safety actions based on risk level and status
RECOMMENDED_ACTIONS: Dict[RiskLevel, str] = {
    RiskLevel.LOW: "Continue normal monitoring.",
    RiskLevel.MODERATE: "Increase monitoring frequency and inspect the affected zone.",
    RiskLevel.HIGH: "Restrict access to the affected zone and perform immediate inspection.",
    RiskLevel.CRITICAL: "Evacuate personnel from the affected zone and initiate emergency geotechnical assessment.",
}

DEGRADED_DATA_ACTION: str = (
    "Sensor data quality compromised. Verify sensor health before relying on automated risk assessment."
)
