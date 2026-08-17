from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import accuracy_score, classification_report


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml"
    / "mineguard_ml_dataset.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

MODEL_FILE = (
    MODEL_DIR
    / "mineguard_risk_model.pkl"
)


print("==========================================")
print("MineGuard AI - Risk Model Training")
print("==========================================")


if not DATA_FILE.exists():

    raise FileNotFoundError(
        f"ML dataset not found:\n{DATA_FILE}"
    )


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


data = pd.read_csv(
    DATA_FILE
)


features = [
    "area_sq_km",
    "mean_elevation_m",
    "min_elevation_m",
    "max_elevation_m",
    "elevation_std_m",
    "mean_slope_deg",
    "max_slope_deg",
    "slope_std_deg",
    "mean_aspect_deg",
    "mean_curvature",
    "mean_roughness",
    "max_roughness",
    "road_count",
    "road_length_km",
    "slope_indicator",
    "roughness_indicator",
    "terrain_variability_indicator"
]


target = "risk_label"


X = data[features]

y = data[target]


print()
print("Dataset information")
print("------------------------------------------")
print(f"Records  : {len(data)}")
print(f"Features : {len(features)}")
print()
print("Risk classes:")
print(y.value_counts())


model = RandomForestClassifier(
    n_estimators=300,
    max_depth=5,
    min_samples_leaf=1,
    random_state=42,
    class_weight="balanced"
)


model.fit(
    X,
    y
)


predictions = model.predict(
    X
)


accuracy = accuracy_score(
    y,
    predictions
)


print()
print("==========================================")
print("MODEL TRAINING COMPLETED")
print("==========================================")

print()
print(
    f"Training accuracy: {accuracy:.3f}"
)

print()
print("Classification report:")
print(
    classification_report(
        y,
        predictions,
        zero_division=0
    )
)


print()
print("Feature importance:")
print("------------------------------------------")


importance = pd.DataFrame(
    {
        "feature": features,
        "importance": model.feature_importances_
    }
).sort_values(
    "importance",
    ascending=False
)


for _, row in importance.iterrows():

    print(
        f"{row['feature']:<35}"
        f"{row['importance']:.4f}"
    )


joblib.dump(
    model,
    MODEL_FILE
)


print()
print("==========================================")
print("MODEL SAVED")
print("==========================================")
print()
print(
    f"Model: {MODEL_FILE}"
)
print()
print("READY FOR ZONE RISK PREDICTION")
print("==========================================")