from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

ZONE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zone_features.csv"
)

ZONE_API_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zone_api_data.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "ml"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "mineguard_ml_dataset.csv"
)


print("==========================================")
print("MineGuard AI - ML Dataset Preparation")
print("==========================================")


if not ZONE_FILE.exists():

    raise FileNotFoundError(
        f"Zone feature file not found:\n{ZONE_FILE}"
    )


if not ZONE_API_FILE.exists():

    raise FileNotFoundError(
        f"Zone API file not found:\n{ZONE_API_FILE}"
    )


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


zones = pd.read_csv(
    ZONE_FILE
)


api_data = pd.read_json(
    ZONE_API_FILE
)


gis_data = pd.json_normalize(
    api_data.to_dict(
        orient="records"
    ),
    sep="_"
)


gis_data = gis_data[
    [
        "zone_id",
        "gis_slope_indicator",
        "gis_roughness_indicator",
        "gis_terrain_variability_indicator",
        "gis_gis_terrain_indicator",
        "gis_gis_terrain_condition"
    ]
]


dataset = zones.merge(
    gis_data,
    on="zone_id",
    how="left"
)


dataset = dataset.rename(
    columns={
        "gis_slope_indicator":
            "slope_indicator",

        "gis_roughness_indicator":
            "roughness_indicator",

        "gis_terrain_variability_indicator":
            "terrain_variability_indicator",

        "gis_gis_terrain_indicator":
            "gis_terrain_indicator",

        "gis_gis_terrain_condition":
            "gis_terrain_condition"
    }
)


numeric_columns = [
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
    "terrain_variability_indicator",
    "gis_terrain_indicator"
]


for column in numeric_columns:

    dataset[column] = pd.to_numeric(
        dataset[column],
        errors="coerce"
    )


dataset["terrain_risk_score"] = (
    0.45
    * dataset["slope_indicator"]
    +
    0.35
    * dataset["roughness_indicator"]
    +
    0.20
    * dataset["terrain_variability_indicator"]
)


def assign_risk(score):

    if score >= 0.70:
        return "HIGH"

    if score >= 0.35:
        return "MODERATE"

    return "LOW"


dataset["risk_label"] = (
    dataset["terrain_risk_score"]
    .apply(assign_risk)
)


dataset["risk_probability_proxy"] = (
    dataset["terrain_risk_score"]
    .clip(
        lower=0.0,
        upper=1.0
    )
)


feature_columns = [
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


output_columns = [
    "mine_id",
    "zone_id"
] + feature_columns + [
    "gis_terrain_indicator",
    "gis_terrain_condition",
    "terrain_risk_score",
    "risk_probability_proxy",
    "risk_label"
]


dataset = dataset[
    output_columns
]


dataset = dataset.dropna(
    subset=feature_columns
)


dataset.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("==========================================")
print("ML DATASET CREATED")
print("==========================================")
print()
print(
    f"Records : {len(dataset)}"
)
print(
    f"Features: {len(feature_columns)}"
)
print()
print("Risk distribution:")
print(
    dataset["risk_label"]
    .value_counts()
)
print()
print("Zone predictions:")
print(
    dataset[
        [
            "zone_id",
            "gis_terrain_indicator",
            "terrain_risk_score",
            "risk_label"
        ]
    ].to_string(
        index=False
    )
)
print()
print("Output:")
print(OUTPUT_FILE)
print()
print("==========================================")
print("READY FOR ML MODEL TRAINING")
print("==========================================")