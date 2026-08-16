"""
MineGuard AI — Utility Functions for ML Pipeline
"""

import os
import json
import logging
from ml.config import BASE_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("MineGuard-ML")


def ensure_directories():
    """Ensure all required interim, processed, and model directories exist."""
    for directory in [INTERIM_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
        os.makedirs(directory, exist_ok=True)
    logger.info("All pipeline directories verified/created.")


def save_json(data: dict, filepath: str):
    """Save dictionary as JSON formatting NumPy types safely."""
    ensure_directories()
    
    def convert_types(obj):
        if hasattr(obj, "item"):
            return obj.item()
        if hasattr(obj, "tolist"):
            return obj.tolist()
        return str(obj)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=convert_types)
    logger.info("Saved JSON metrics to %s", filepath)


def load_json(filepath: str) -> dict:
    """Load dictionary from JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
