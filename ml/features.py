"""
MineGuard AI — Phase 6 feature column contract.

Prototype / synthetic-data pipeline only. Feature names must match
`ai.features.FeatureExtractor` output. Scenario name is NEVER an ML input.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from ai.config import RiskLevel

# Ordered feature vector used for training and inference.
FEATURE_COLUMNS: tuple[str, ...] = (
    "displacement_mm",
    "strain",
    "pore_pressure_kpa",
    "rainfall_mm",
    "temperature_c",
    "vibration_g",
    "displacement_rate",
    "displacement_accel",
    "pore_pressure_rate",
    "rainfall_intensity",
    "vibration_severity",
    "strain_severity",
    "combined_instability_index",
)

RISK_LEVELS: tuple[str, ...] = tuple(level.value for level in RiskLevel)


class FeatureContractError(ValueError):
    """Raised when a feature row violates the Phase 6 contract."""


def vector_from_features(features: Mapping[str, Any]) -> List[float]:
    """Extract the ordered numeric feature vector from a FeatureExtractor dict."""
    row: List[float] = []
    missing: List[str] = []
    for name in FEATURE_COLUMNS:
        if name not in features:
            missing.append(name)
            continue
        value = features[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise FeatureContractError(
                f"Feature '{name}' must be numeric, got {type(value).__name__}"
            )
        number = float(value)
        if not math.isfinite(number):
            raise FeatureContractError(f"Feature '{name}' is not finite: {number}")
        row.append(number)
    if missing:
        raise FeatureContractError(
            f"Missing required ML features: {', '.join(missing)}"
        )
    return row


def row_dict_from_features(features: Mapping[str, Any]) -> Dict[str, float]:
    """Return an ordered dict of validated ML features (no scenario field)."""
    values = vector_from_features(features)
    return {name: values[i] for i, name in enumerate(FEATURE_COLUMNS)}


def validate_feature_matrix(rows: Sequence[Mapping[str, Any]]) -> None:
    """Validate that every dataset row has finite required features and no extras required for X."""
    if not rows:
        raise FeatureContractError("Dataset contains no feature rows")
    for index, row in enumerate(rows):
        vector_from_features(row)


def assert_no_nan_or_inf(values: Iterable[Any], *, context: str) -> None:
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            raise FeatureContractError(f"Non-finite value in {context}: {value}")
