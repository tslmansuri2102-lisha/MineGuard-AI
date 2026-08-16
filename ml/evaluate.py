"""
MineGuard AI — Model Evaluation & Explainability Preparation Module
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    average_precision_score
)

from ml.utils import logger, save_json
from ml.config import METRICS_FILE


def evaluate_model(
    model,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list = None,
    dataset_name: str = "Validation"
) -> dict:
    """
    Compute comprehensive evaluation metrics for MineGuard AI hazard predictions.
    
    Args:
        model: Trained BaselineModel instance.
        X (np.ndarray): Processed feature matrix.
        y (np.ndarray): True ground-truth binary targets.
        feature_names (list, optional): List of feature names for explainability.
        dataset_name (str): Name of split ('Validation' or 'Test').
        
    Returns:
        dict: Evaluation metrics and feature importances report.
    """
    logger.info("Evaluating baseline model on %s dataset (%d samples)...", dataset_name, len(X))
    
    y_true = np.array(y)
    y_proba = model.predict_proba(X)
    y_pred = model.predict(X, threshold=0.5)
    
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))  # Critical metric: Hazard Recall
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    
    # Calculate ROC-AUC & PR-AUC if both classes present
    if len(np.unique(y_true)) > 1:
        roc_auc = float(roc_auc_score(y_true, y_proba))
        pr_auc = float(average_precision_score(y_true, y_proba))
    else:
        roc_auc = 0.0
        pr_auc = 0.0
        
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = (int(x) for x in cm.ravel()) if cm.shape == (2, 2) else (0, 0, 0, 0)
    
    # Feature Importances / Explainability preparation
    top_features = []
    if feature_names and hasattr(model, "feature_importances_") and model.feature_importances_ is not None:
        importances = model.feature_importances_
        feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        top_features = [
            {"feature": f, "importance": float(round(imp, 4)), "description": f"Feature {f} influence score"}
            for f, imp in feat_imp[:10]
        ]
        
    metrics = {
        "dataset": dataset_name,
        "sample_count": len(y_true),
        "positive_count": int(np.sum(y_true)),
        "negative_count": int(len(y_true) - np.sum(y_true)),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),  # Hazard Recall
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp
        },
        "top_contributing_features": top_features
    }
    
    logger.info("[%s Evaluation] Acc: %.4f | Prec: %.4f | Recall (Hazard Sensitivity): %.4f | F1: %.4f | ROC-AUC: %.4f",
                dataset_name, acc, prec, rec, f1, roc_auc)
    logger.info("[%s Confusion Matrix] TP: %d | FP: %d | FN: %d | TN: %d", dataset_name, tp, fp, fn, tn)
    
    return metrics
