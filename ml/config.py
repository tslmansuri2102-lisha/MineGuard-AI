"""
MineGuard AI — ML Pipeline Configuration
"""

import os

# Project Base Directory (E:\MineGuard-AI)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Data Paths
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
RAW_DATA_FILE = os.path.join(RAW_DATA_DIR, "nasa_global_landslide_catalog.csv")

INTERIM_DATA_DIR = os.path.join(BASE_DIR, "data", "interim")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

VALIDATED_DATA_FILE = os.path.join(INTERIM_DATA_DIR, "validated_data.csv")
FEATURES_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, "features.csv")
TRAIN_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, "train.csv")
VAL_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, "validation.csv")
TEST_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, "test.csv")

# Model Artifact Paths
MODELS_DIR = os.path.join(BASE_DIR, "models", "baseline")
PREPROCESSOR_FILE = os.path.join(MODELS_DIR, "preprocessor.joblib")
MODEL_FILE = os.path.join(MODELS_DIR, "model.joblib")
METRICS_FILE = os.path.join(MODELS_DIR, "metrics.json")

# Pipeline Parameters
RANDOM_SEED = 42

# Target Definition
TARGET_COL = "target_rockfall"
POSITIVE_CLASS_VALUE = "rock_fall"

# Feature Definitions
NUMERICAL_FEATURES = [
    "latitude",
    "longitude",
    "year",
    "month",
    "day_of_year",
    "rainfall_mm",
    "rainfall_3h_sum",
    "rainfall_24h_sum",
    "slope_deg",
    "elevation_m",
    "displacement_velocity",
    "displacement_acceleration",
]

CATEGORICAL_FEATURES = [
    "landslide_trigger",
    "landslide_size",
    "landslide_setting",
    "country_code",
]

# Risk Level Mapping (API_CONTRACT.md Section 3)
RISK_LEVEL_THRESHOLDS = {
    "LOW": (0.00, 0.25),
    "MODERATE": (0.25, 0.50),
    "HIGH": (0.50, 0.75),
    "CRITICAL": (0.75, 1.00),
}
