"""
MineGuard AI — Data Preprocessing Pipeline Module
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from ml.config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, PREPROCESSOR_FILE
from ml.utils import logger, ensure_directories


class PipelinePreprocessor:
    """
    Reusable Scikit-Learn ColumnTransformer preprocessor fitted strictly on training data.
    """
    def __init__(self, numerical_cols=None, categorical_cols=None):
        self.numerical_cols = numerical_cols or NUMERICAL_FEATURES
        self.categorical_cols = categorical_cols or CATEGORICAL_FEATURES
        self.pipeline = None
        self.feature_names_out = []

    def build_pipeline(self, X_sample: pd.DataFrame):
        """Construct scikit-learn preprocessing pipeline based on available features."""
        num_cols = [c for c in self.numerical_cols if c in X_sample.columns]
        cat_cols = [c for c in self.categorical_cols if c in X_sample.columns]
        
        logger.info("Building preprocessing pipeline for %d numerical and %d categorical features...",
                    len(num_cols), len(cat_cols))
                    
        num_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        
        cat_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        
        self.pipeline = ColumnTransformer(
            transformers=[
                ("num", num_transformer, num_cols),
                ("cat", cat_transformer, cat_cols)
            ],
            remainder="drop"
        )
        self.active_num_cols = num_cols
        self.active_cat_cols = cat_cols

    def fit(self, X_train: pd.DataFrame):
        """Fit preprocessing pipeline strictly on training features ONLY."""
        logger.info("Fitting preprocessor strictly on training dataset (Rows: %d)...", len(X_train))
        self.build_pipeline(X_train)
        self.pipeline.fit(X_train)
        
        # Capture feature names
        num_feature_names = self.active_num_cols
        cat_encoder = self.pipeline.named_transformers_["cat"].named_steps["encoder"]
        cat_feature_names = cat_encoder.get_feature_names_out(self.active_cat_cols).tolist()
        
        self.feature_names_out = num_feature_names + cat_feature_names
        logger.info("Preprocessor fit completed. Total processed feature dimensions: %d", len(self.feature_names_out))
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform input features using fitted pipeline."""
        if self.pipeline is None:
            raise ValueError("Preprocessor pipeline has not been fitted yet. Call fit() on X_train first.")
        return self.pipeline.transform(X)

    def fit_transform(self, X_train: pd.DataFrame) -> np.ndarray:
        """Fit on training data and transform it."""
        return self.fit(X_train).transform(X_train)

    def save(self, filepath: str = PREPROCESSOR_FILE):
        """Save fitted preprocessor artifact."""
        ensure_directories()
        joblib.dump(self, filepath)
        logger.info("Saved preprocessor artifact to: %s", filepath)

    @classmethod
    def load(cls, filepath: str = PREPROCESSOR_FILE):
        """Load fitted preprocessor artifact."""
        logger.info("Loading preprocessor artifact from: %s", filepath)
        return joblib.load(filepath)


if __name__ == "__main__":
    from ml.run_pipeline import run_pipeline
    run_pipeline()

