from pathlib import Path
import json

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml"
    / "mineguard_ml_dataset.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "mineguard_risk_model.pkl"
)

ZONE_API_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zone_api_data.json"
)


print("==========================================")
print("MineGuard AI - Zone Risk Prediction")
print("==========================================")


if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"ML dataset not found:\n{DATA_FILE}"
    )


if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"Trained model not found:\n{MODEL_FILE}"
    )


if not ZONE_API_FILE.exists():
    raise FileNotFoundError(
        f"Zone API file not found:\n{ZONE_API_FILE}"
    )


data = pd.read_csv(DATA_FILE)

model = joblib.load(MODEL_FILE)


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


X = data[features]


predictions = model.predict(X)

probabilities = model.predict_proba(X)

classes = list(model.classes_)


high_index = classes.index("HIGH")


high_probabilities = probabilities[:, high_index]


results = data[
    [
        "mine_id",
        "zone_id"
    ]
].copy()


results["ai_risk_level"] = predictions

results["ai_risk_probability"] = high_probabilities


results["ai_risk_probability"] = (
    results["ai_risk_probability"]
    .clip(0, 1)
)


def classify_risk(probability):

    if probability >= 0.70:
        return "HIGH"

    if probability >= 0.35:
        return "MODERATE"

    return "LOW"


results["ai_risk_level"] = (
    results["ai_risk_probability"]
    .apply(classify_risk)
)


print()
print("==========================================")
print("AI RISK PREDICTIONS")
print("==========================================")
print()


for _, row in results.iterrows():

    print(
        f"{row['zone_id']:<12}"
        f"{row['ai_risk_level']:<10}"
        f"{row['ai_risk_probability'] * 100:>7.2f}%"
    )


with open(
    ZONE_API_FILE,
    "r",
    encoding="utf-8"
) as file:

    zone_api_data = json.load(file)


prediction_lookup = {
    str(row["zone_id"]): row
    for _, row in results.iterrows()
}


for zone in zone_api_data:

    zone_id = str(
        zone["zone_id"]
    )

    prediction = prediction_lookup.get(
        zone_id
    )

    if prediction is None:
        continue


    zone["risk"]["level"] = (
        prediction["ai_risk_level"]
    )


    zone["risk"]["probability"] = round(
        float(
            prediction[
                "ai_risk_probability"
            ]
        ),
        4
    )


    zone["risk"]["model"] = (
        "MineGuard Random Forest"
    )


    zone["risk"]["prediction_type"] = (
        "GIS prototype prediction"
    )


with open(
    ZONE_API_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        zone_api_data,
        file,
        indent=2
    )


print()
print("==========================================")
print("ZONE API UPDATED")
print("==========================================")
print()
print(
    f"Updated file:\n{ZONE_API_FILE}"
)
print()
print("AI risk is now connected to the")
print("MineGuard zone data.")
print()
print("==========================================")