"""
MineGuard AI — Phase 2 ML Data Pipeline & Model Training Orchestrator
"""

import sys
import pandas as pd
from ml.config import (
    VALIDATED_DATA_FILE,
    FEATURES_DATA_FILE,
    TRAIN_DATA_FILE,
    VAL_DATA_FILE,
    TEST_DATA_FILE,
    METRICS_FILE,
    TARGET_COL
)
from ml.utils import logger, ensure_directories, save_json
from ml.data_loader import load_raw_dataset
from ml.validation import validate_dataset
from ml.target_builder import build_target
from ml.feature_engineering import engineer_features
from ml.leakage import prevent_leakage, check_for_leakage
from ml.split import split_data
from ml.preprocessing import PipelinePreprocessor
from ml.baseline_model import BaselineModel
from ml.evaluate import evaluate_model


def run_pipeline() -> dict:
    """
    Execute the full end-to-end Phase 2 ML data pipeline.
    
    Returns:
        dict: Complete pipeline execution summary report.
    """
    logger.info("==================================================")
    logger.info("   MINEGUARD-AI — STARTING PHASE 2 ML PIPELINE   ")
    logger.info("==================================================")
    
    ensure_directories()
    
    # Step 1: Data Loading
    df_raw = load_raw_dataset()
    
    # Step 2: Data Validation
    is_valid, validation_report = validate_dataset(df_raw)
    if not is_valid:
        logger.error("Dataset validation FAILED. Pipeline aborted.")
        sys.exit(1)
        
    # Save interim validated dataset
    df_raw.to_csv(VALIDATED_DATA_FILE, index=False)
    logger.info("Saved interim validated data to: %s", VALIDATED_DATA_FILE)
    
    # Step 3: Target Construction
    df_target, target_stats = build_target(df_raw)
    
    # Step 4: Feature Engineering
    df_engineered = engineer_features(df_target)
    
    # Step 5: Leakage Prevention
    df_clean = prevent_leakage(df_engineered)
    
    # Save processed features dataset
    df_clean.to_csv(FEATURES_DATA_FILE, index=False)
    logger.info("Saved processed feature dataset to: %s", FEATURES_DATA_FILE)
    
    # Step 6: Train / Validation / Test Splitting
    X_train_df, y_train, X_val_df, y_val, X_test_df, y_test, split_stats = split_data(
        df_clean, target_col=TARGET_COL, strategy="time_aware"
    )
    
    # Verify Leakage Prevention
    check_for_leakage(X_train_df, X_val_df, X_test_df)
    
    # Save Split Datasets to data/processed/
    pd.concat([X_train_df, y_train], axis=1).to_csv(TRAIN_DATA_FILE, index=False)
    pd.concat([X_val_df, y_val], axis=1).to_csv(VAL_DATA_FILE, index=False)
    pd.concat([X_test_df, y_test], axis=1).to_csv(TEST_DATA_FILE, index=False)
    logger.info("Saved train/validation/test split datasets to data/processed/")
    
    # Step 7: Preprocessing Pipeline (Fitted ONLY on X_train)
    preprocessor = PipelinePreprocessor()
    X_train_proc = preprocessor.fit_transform(X_train_df)
    X_val_proc = preprocessor.transform(X_val_df)
    X_test_proc = preprocessor.transform(X_test_df)
    
    # Save preprocessor artifact
    preprocessor.save()
    
    # Step 8: Baseline Model Training (Trained ONLY on X_train)
    model = BaselineModel(model_type="random_forest")
    model.fit(X_train_proc, y_train.values)
    
    # Save model artifact
    model.save()
    
    # Step 9: Model Evaluation
    val_metrics = evaluate_model(model, X_val_proc, y_val.values, 
                                 feature_names=preprocessor.feature_names_out, 
                                 dataset_name="Validation")
                                 
    test_metrics = evaluate_model(model, X_test_proc, y_test.values, 
                                  feature_names=preprocessor.feature_names_out, 
                                  dataset_name="Test")
                                  
    pipeline_summary = {
        "pipeline_status": "COMPLETED",
        "raw_samples": len(df_raw),
        "target_samples": len(df_target),
        "feature_count": len(preprocessor.feature_names_out),
        "target_stats": target_stats,
        "split_stats": split_stats,
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics
    }
    
    save_json(pipeline_summary, METRICS_FILE)
    
    logger.info("==================================================")
    logger.info("   MINEGUARD-AI — PHASE 2 PIPELINE SUCCESSFUL    ")
    logger.info("==================================================")
    
    return pipeline_summary


if __name__ == "__main__":
    summary = run_pipeline()
    print("\n--- PHASE 2 PIPELINE SUMMARY ---")
    print("Raw Samples:", summary["raw_samples"])
    print("Features:", summary["feature_count"])
    print("Test Hazard Recall (Sensitivity):", summary["test_metrics"]["recall"])
    print("Test ROC-AUC:", summary["test_metrics"]["roc_auc"])
