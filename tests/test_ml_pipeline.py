"""
MineGuard AI — Unit Tests for ML Data Pipeline & Baseline Model
"""

import os
import unittest
import numpy as np
import pandas as pd

from ml.config import BASE_DIR, RAW_DATA_FILE, TARGET_COL
from ml.data_loader import load_raw_dataset
from ml.validation import validate_dataset
from ml.target_builder import build_target
from ml.feature_engineering import engineer_features
from ml.leakage import prevent_leakage, LEAKY_COLUMNS, check_for_leakage
from ml.split import split_data
from ml.preprocessing import PipelinePreprocessor
from ml.baseline_model import BaselineModel
from ml.evaluate import evaluate_model


class TestMLPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load raw dataset once for test execution."""
        cls.df_raw = load_raw_dataset()

    def test_01_data_loader(self):
        """Test dataset loading and structure."""
        self.assertIsNotNone(self.df_raw)
        self.assertGreater(len(self.df_raw), 10000)
        self.assertIn("latitude", self.df_raw.columns)
        self.assertIn("longitude", self.df_raw.columns)

    def test_02_data_validation(self):
        """Test validation checks on raw dataset."""
        is_valid, report = validate_dataset(self.df_raw)
        self.assertTrue(is_valid)
        self.assertTrue(report["passed"])
        self.assertEqual(report["checks"]["invalid_latitude_count"], 0)
        self.assertEqual(report["checks"]["invalid_longitude_count"], 0)

    def test_03_target_building(self):
        """Test binary target construction and class filtering."""
        df_target, stats = build_target(self.df_raw)
        self.assertIn(TARGET_COL, df_target.columns)
        self.assertGreater(stats["positive_samples"], 500)
        unique_targets = set(df_target[TARGET_COL].unique())
        self.assertTrue(unique_targets.issubset({0, 1}))

    def test_04_feature_engineering(self):
        """Test temporal, rainfall, and terrain feature generation."""
        df_target, _ = build_target(self.df_raw)
        df_feat = engineer_features(df_target)
        
        for col in ["year", "month", "day_of_year", "rainfall_mm", "rainfall_3h_sum", "slope_deg", "elevation_m"]:
            self.assertIn(col, df_feat.columns)
            
        self.assertTrue((df_feat["rainfall_mm"] >= 0.0).all())
        self.assertTrue((df_feat["month"] >= 1).all() and (df_feat["month"] <= 12).all())

    def test_05_leakage_prevention(self):
        """Test removal of post-event outcome leakage fields."""
        df_target, _ = build_target(self.df_raw)
        df_feat = engineer_features(df_target)
        df_clean = prevent_leakage(df_feat)
        
        for leaky_col in LEAKY_COLUMNS:
            self.assertNotIn(leaky_col, df_clean.columns)

    def test_06_train_val_test_splitting(self):
        """Test time-aware dataset splitting."""
        df_target, _ = build_target(self.df_raw)
        df_feat = engineer_features(df_target)
        df_clean = prevent_leakage(df_feat)
        
        X_train, y_train, X_val, y_val, X_test, y_test, stats = split_data(df_clean, strategy="time_aware")
        
        total_split = len(X_train) + len(X_val) + len(X_test)
        self.assertEqual(total_split, len(df_clean))
        self.assertGreater(len(X_train), len(X_val))
        self.assertGreater(len(X_train), len(X_test))
        
        # Ensure leakage check passes
        self.assertTrue(check_for_leakage(X_train, X_val, X_test))

    def test_07_preprocessing_no_leakage(self):
        """Test preprocessor fit strictly on training set and transform."""
        df_target, _ = build_target(self.df_raw)
        df_feat = engineer_features(df_target)
        df_clean = prevent_leakage(df_feat)
        X_train, y_train, X_val, y_val, X_test, y_test, _ = split_data(df_clean)
        
        preprocessor = PipelinePreprocessor()
        X_train_proc = preprocessor.fit_transform(X_train)
        X_val_proc = preprocessor.transform(X_val)
        
        self.assertIsInstance(X_train_proc, np.ndarray)
        self.assertIsInstance(X_val_proc, np.ndarray)
        self.assertFalse(np.isnan(X_train_proc).any())
        self.assertFalse(np.isnan(X_val_proc).any())

    def test_08_baseline_model(self):
        """Test baseline model fitting, probability prediction, and risk mapping."""
        df_target, _ = build_target(self.df_raw)
        df_feat = engineer_features(df_target)
        df_clean = prevent_leakage(df_feat)
        X_train, y_train, X_val, y_val, X_test, y_test, _ = split_data(df_clean)
        
        preprocessor = PipelinePreprocessor()
        X_train_proc = preprocessor.fit_transform(X_train)
        X_val_proc = preprocessor.transform(X_val)
        
        model = BaselineModel(model_type="random_forest")
        model.fit(X_train_proc, y_train.values)
        
        probas = model.predict_proba(X_val_proc)
        self.assertTrue((probas >= 0.0).all() and (probas <= 1.0).all())
        
        risk = model.predict_risk_level(0.84)
        self.assertIn(risk, ["LOW", "MODERATE", "HIGH", "CRITICAL"])
        
        metrics = evaluate_model(model, X_val_proc, y_val.values, dataset_name="Validation")
        self.assertIn("accuracy", metrics)
        self.assertIn("recall", metrics)
        self.assertGreater(metrics["recall"], 0.50)


if __name__ == "__main__":
    unittest.main()
