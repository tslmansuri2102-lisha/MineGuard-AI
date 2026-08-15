"""
MineGuard AI — Baseline Model Training Module
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from ml.config import RANDOM_SEED, MODEL_FILE, RISK_LEVEL_THRESHOLDS
from ml.utils import logger, ensure_directories


class BaselineModel:
    """
    MineGuard AI Baseline Classifier for Tabular Hazard Prediction.
    """
    def __init__(self, model_type: str = "random_forest", random_seed: int = RANDOM_SEED):
        self.model_type = model_type
        self.random_seed = random_seed
        self.model = None
        self.feature_importances_ = None

        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                min_samples_split=5,
                class_weight="balanced",
                random_state=random_seed,
                n_jobs=-1
            )
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=random_seed
            )
        else:
            raise ValueError(f"Unsupported model_type: '{model_type}'")

    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train baseline model strictly on training data."""
        logger.info("Training %s baseline model on %d training samples...", self.model_type, len(X_train))
        self.model.fit(X_train, y_train)
        
        if hasattr(self.model, "feature_importances_"):
            self.feature_importances_ = self.model.feature_importances_
        elif hasattr(self.model, "coef_"):
            self.feature_importances_ = np.abs(self.model.coef_[0])
            
        logger.info("Model training complete.")
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict rockfall probability (0.0 to 1.0)."""
        probas = self.model.predict_proba(X)
        # Return probability of positive class (rockfall)
        if probas.shape[1] > 1:
            return probas[:, 1]
        return probas[:, 0]

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Predict binary classification using probability threshold."""
        probas = self.predict_proba(X)
        return (probas >= threshold).astype(int)

    def predict_risk_level(self, proba: float) -> str:
        """Map rockfall probability to API_CONTRACT.md risk level string."""
        for level, (low, high) in RISK_LEVEL_THRESHOLDS.items():
            if low <= proba <= high:
                return level
        return "CRITICAL" if proba > 0.75 else "LOW"

    def save(self, filepath: str = MODEL_FILE):
        """Save model artifact."""
        ensure_directories()
        joblib.dump(self, filepath)
        logger.info("Saved baseline model artifact to: %s", filepath)

    @classmethod
    def load(cls, filepath: str = MODEL_FILE):
        """Load baseline model artifact."""
        logger.info("Loading baseline model artifact from: %s", filepath)
        return joblib.load(filepath)
