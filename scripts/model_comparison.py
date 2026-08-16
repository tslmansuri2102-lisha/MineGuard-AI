"""
MineGuard-AI
Model Comparison Script

Compares the existing baseline Random Forest against
Logistic Regression using the same processed dataset,
same train/validation/test split, and same preprocessing
strategy.

This script does NOT overwrite the existing baseline model.
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

from ml.preprocessing import PipelinePreprocessor


# ============================================================
# Configuration
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
VAL_FILE = ROOT / "data" / "processed" / "validation.csv"
TEST_FILE = ROOT / "data" / "processed" / "test.csv"

OUTPUT_DIR = ROOT / "models" / "comparison"
OUTPUT_FILE = OUTPUT_DIR / "model_comparison.json"

TARGET_COLUMN = "target_rockfall"
RANDOM_SEED = 42


# ============================================================
# Data loading
# ============================================================

def load_split(path):
    df = pd.read_csv(path)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' not found in {path}"
        )

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    return X, y


# ============================================================
# Evaluation
# ============================================================

def evaluate_model(model, X, y, dataset_name):
    probabilities = model.predict_proba(X)[:, 1]

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "dataset": dataset_name,
        "sample_count": int(len(y)),
        "positive_count": int(y.sum()),
        "negative_count": int((y == 0).sum()),
        "accuracy": round(
            accuracy_score(y, predictions), 4
        ),
        "precision": round(
            precision_score(
                y,
                predictions,
                zero_division=0,
            ),
            4,
        ),
        "recall": round(
            recall_score(
                y,
                predictions,
                zero_division=0,
            ),
            4,
        ),
        "f1_score": round(
            f1_score(
                y,
                predictions,
                zero_division=0,
            ),
            4,
        ),
        "roc_auc": round(
            roc_auc_score(y, probabilities),
            4,
        ),
        "pr_auc": round(
            average_precision_score(
                y,
                probabilities,
            ),
            4,
        ),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
    }


# ============================================================
# Main comparison
# ============================================================

def main():

    print("=" * 65)
    print("MINEGUARD-AI MODEL COMPARISON")
    print("=" * 65)

    # --------------------------------------------------------
    # Load existing split datasets
    # --------------------------------------------------------

    print("\nLoading existing datasets...")

    X_train, y_train = load_split(TRAIN_FILE)
    X_val, y_val = load_split(VAL_FILE)
    X_test, y_test = load_split(TEST_FILE)

    print(f"Training samples   : {len(X_train)}")
    print(f"Validation samples : {len(X_val)}")
    print(f"Test samples       : {len(X_test)}")

    # --------------------------------------------------------
    # Verify target distribution
    # --------------------------------------------------------

    print("\nTarget distribution:")

    print(
        f"Train positives: {int(y_train.sum())} "
        f"/ {len(y_train)}"
    )

    print(
        f"Validation positives: {int(y_val.sum())} "
        f"/ {len(y_val)}"
    )

    print(
        f"Test positives: {int(y_test.sum())} "
        f"/ {len(y_test)}"
    )

    # --------------------------------------------------------
    # Preprocessing
    # --------------------------------------------------------

    print("\nFitting preprocessing ONLY on training data...")

    preprocessor = PipelinePreprocessor()

    X_train_proc = preprocessor.fit_transform(
        X_train
    )

    X_val_proc = preprocessor.transform(
        X_val
    )

    X_test_proc = preprocessor.transform(
        X_test
    )

    print(
        f"Processed feature count: "
        f"{len(preprocessor.feature_names_out)}"
    )

    # --------------------------------------------------------
    # Define models
    # --------------------------------------------------------

    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            class_weight="balanced",
            random_state=RANDOM_SEED,
            n_jobs=-1,
        ),

        "logistic_regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
    }

    comparison = {}

    # --------------------------------------------------------
    # Train and evaluate
    # --------------------------------------------------------

    for model_name, model in models.items():

        print("\n" + "-" * 65)
        print(f"Training: {model_name}")
        print("-" * 65)

        model.fit(
            X_train_proc,
            y_train.to_numpy(),
        )

        validation_metrics = evaluate_model(
            model,
            X_val_proc,
            y_val.to_numpy(),
            "Validation",
        )

        test_metrics = evaluate_model(
            model,
            X_test_proc,
            y_test.to_numpy(),
            "Test",
        )

        comparison[model_name] = {
            "validation": validation_metrics,
            "test": test_metrics,
        }

        print(
            f"Validation | "
            f"Recall={validation_metrics['recall']:.4f} | "
            f"F1={validation_metrics['f1_score']:.4f} | "
            f"ROC-AUC={validation_metrics['roc_auc']:.4f} | "
            f"PR-AUC={validation_metrics['pr_auc']:.4f}"
        )

        print(
            f"Test       | "
            f"Recall={test_metrics['recall']:.4f} | "
            f"F1={test_metrics['f1_score']:.4f} | "
            f"ROC-AUC={test_metrics['roc_auc']:.4f} | "
            f"PR-AUC={test_metrics['pr_auc']:.4f}"
        )

    # --------------------------------------------------------
    # Model selection recommendation
    # --------------------------------------------------------

    rf = comparison["random_forest"]["validation"]
    lr = comparison["logistic_regression"]["validation"]

    # Safety-oriented selection:
    # prioritize recall, then F1, then PR-AUC.
    ranking = sorted(
        comparison.keys(),
        key=lambda name: (
            comparison[name]["validation"]["recall"],
            comparison[name]["validation"]["f1_score"],
            comparison[name]["validation"]["pr_auc"],
        ),
        reverse=True,
    )

    recommended_model = ranking[0]

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    report = {
        "comparison_status": "COMPLETED",
        "selection_criterion": [
            "validation_recall",
            "validation_f1",
            "validation_pr_auc",
        ],
        "recommended_model": recommended_model,
        "models": comparison,
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Final report
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("MODEL SELECTION RESULT")
    print("=" * 65)

    print(
        f"Recommended model: {recommended_model}"
    )

    print(
        "\nComparison report saved to:"
    )

    print(OUTPUT_FILE)

    print("=" * 65)


if __name__ == "__main__":
    main()