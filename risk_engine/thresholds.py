"""
MineGuard AI — Risk Engine Configurable Thresholds & Weights
"""

DEFAULT_RISK_WEIGHTS = {
    "ml_probability": 0.35,
    "vibration_trend": 0.15,
    "displacement_trend": 0.15,
    "slope_velocity": 0.12,
    "strain_trend": 0.10,
    "sensor_anomaly": 0.08,
    "rainfall": 0.03,
    "human_reports": 0.02  # Auxiliary signal ONLY
}

RISK_LEVEL_BOUNDS = [
    (0, 25, "LOW"),
    (26, 50, "MODERATE"),
    (51, 75, "HIGH"),
    (76, 100, "CRITICAL")
]

RECOMMENDED_ACTIONS = {
    "LOW": "Routine slope stability monitoring. All bench operations normal.",
    "MODERATE": "Heightened vigilance. Increase sensor polling frequency and inspect drainage.",
    "HIGH": "WARNING: Restrict heavy machinery on bench. Alert slope stability engineer.",
    "CRITICAL": "EMERGENCY: IMMEDIATELY EVACUATE BENCH WORKERS AND MACHINERY! TRIGGER AUDIO ALARM!"
}
