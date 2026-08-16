"""
MineGuard AI — XAI Test

Loads the existing train/validation/test datasets,
fits the selected Logistic Regression model using the
same preprocessing pipeline, and generates a local
explanation for one test prediction.
"""

from pathlib import Path
import json

import pandas as pd
from sklearn.linear_model import LogisticRegression

from ml.preprocessing import PipelinePreprocessor
from ml.xai import MineGuardXAI


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

TRAIN_FILE = ROOT / "data" / "processed" / "train.csv"
TEST_FILE = ROOT / "data" / "processed" / "test.csv"

OUTPUT_DIR = ROOT / "models" / "xai"
OUTPUT_FILE = OUTPUT_DIR / "sample_explanation.json"

TARGET_COLUMN = "target_rockfall"
RANDOM_SEED = 42


# ============================================================
# Load data
# ============================================================

train_df = pd.read_csv(TRAIN_FILE)
test_df = pd.read_csv(TEST_FILE)

X_train = train_df.drop(columns=[TARGET_COLUMN])
y_train = train_df[TARGET_COLUMN]

X_test = test_df.drop(columns=[TARGET_COLUMN])
y_test = test_df[TARGET_COLUMN]


# ============================================================
# Preprocessing
# ============================================================

print("=" * 65)
print("MINEGUARD-AI XAI TEST")
print("=" * 65)

print("\nFitting preprocessor on training data only...")

preprocessor = PipelinePreprocessor()

X_train_proc = preprocessor.fit_transform(X_train)
X_test_proc = preprocessor.transform(X_test)


# ============================================================
# Train Logistic Regression
# ============================================================

print("Training Logistic Regression...")

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=RANDOM_SEED
)

model.fit(
    X_train_proc,
    y_train.to_numpy()
)


# ============================================================
# XAI engine
# ============================================================

xai = MineGuardXAI(
    model=model,
    feature_names=preprocessor.feature_names_out
)


# ============================================================
# Global explanation
# ============================================================

global_features = xai.global_feature_importance(
    top_n=10
)

print("\nTop global features:")
print("-" * 65)

for _, row in global_features.iterrows():
    print(
        f"{row['feature']:<35} "
        f"{row['importance']:.6f}"
    )


# ============================================================
# Select one test sample
# ============================================================

sample_index = 0

sample_X = X_test_proc[sample_index:sample_index + 1]
sample_y = int(y_test.iloc[sample_index])

sample_probability = float(
    model.predict_proba(sample_X)[0, 1]
)

sample_prediction = int(
    sample_probability >= 0.5
)


# ============================================================
# Local explanation
# ============================================================

local_explanation = xai.explain_prediction(
    sample_X
)[0]


# ============================================================
# Risk level
# ============================================================

if sample_probability <= 0.25:
    risk_level = "LOW"
elif sample_probability <= 0.50:
    risk_level = "MEDIUM"
elif sample_probability <= 0.75:
    risk_level = "HIGH"
else:
    risk_level = "CRITICAL"


# ============================================================
# Build report
# ============================================================

report = {
    "sample_index": sample_index,
    "actual_label": sample_y,
    "predicted_label": sample_prediction,
    "rockfall_probability": round(
        sample_probability,
        4
    ),
    "risk_level": risk_level,
    "top_contributors":
        local_explanation["top_contributors"]
}


# ============================================================
# Print result
# ============================================================

print("\n" + "=" * 65)
print("LOCAL XAI EXPLANATION")
print("=" * 65)

print(
    f"Actual label          : {sample_y}"
)

print(
    f"Predicted label       : {sample_prediction}"
)

print(
    f"Rockfall probability   : "
    f"{sample_probability:.2%}"
)

print(
    f"Risk level             : {risk_level}"
)

print("\nTop contributing features:")
print("-" * 65)

for item in local_explanation["top_contributors"][:10]:

    direction = item["direction"]

    print(
        f"{item['feature']:<35} "
        f"{direction:<18} "
        f"contribution="
        f"{item['contribution']:.6f}"
    )


# ============================================================
# Save report
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        report,
        f,
        indent=2
    )

print("\nXAI report saved to:")
print(OUTPUT_FILE)

print("=" * 65)