from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zone_features.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "mine_zone_features.csv"
)


print("==========================================")
print("MineGuard AI - GIS Indicator Generator")
print("==========================================")


# --------------------------------------------------
# CHECK INPUT
# --------------------------------------------------

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}\n\n"
        "Run generate_zone_features.py first."
    )


# --------------------------------------------------
# LOAD ZONE FEATURES
# --------------------------------------------------

print("\nLoading zone features...")

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"Zones loaded: {len(df)}"
)

print(
    f"Features loaded: {len(df.columns)}"
)


# --------------------------------------------------
# REQUIRED COLUMNS
# --------------------------------------------------

required_columns = [
    "mine_id",
    "zone_id",
    "mean_elevation_m",
    "elevation_std_m",
    "mean_slope_deg",
    "max_slope_deg",
    "slope_std_deg",
    "mean_curvature",
    "mean_roughness",
    "max_roughness",
    "road_count",
    "road_length_km"
]


missing = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing:

    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(
            f"- {column}"
            for column in missing
        )
    )


# --------------------------------------------------
# NORMALIZATION FUNCTION
# --------------------------------------------------

def normalize(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:

        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        (series - minimum)
        / (maximum - minimum)
    )


# --------------------------------------------------
# TERRAIN INDICATORS
# --------------------------------------------------

print("\nCalculating terrain indicators...")


df["slope_indicator"] = normalize(
    df["mean_slope_deg"]
)


df["slope_extreme_indicator"] = normalize(
    df["max_slope_deg"]
)


df["roughness_indicator"] = normalize(
    df["mean_roughness"]
)


df["roughness_extreme_indicator"] = normalize(
    df["max_roughness"]
)


df["elevation_variability_indicator"] = normalize(
    df["elevation_std_m"]
)


df["slope_variability_indicator"] = normalize(
    df["slope_std_deg"]
)


# --------------------------------------------------
# ROAD EXPOSURE INDICATORS
# --------------------------------------------------

print("Calculating infrastructure indicators...")


df["road_density_indicator"] = normalize(
    df["road_length_km"]
)


df["road_count_indicator"] = normalize(
    df["road_count"]
)


# --------------------------------------------------
# TERRAIN VARIABILITY INDICATOR
# --------------------------------------------------

df["terrain_variability_indicator"] = (
    (
        df["elevation_variability_indicator"]
        +
        df["slope_variability_indicator"]
        +
        df["roughness_indicator"]
    )
    / 3.0
)


# --------------------------------------------------
# CURVATURE INDICATOR
# --------------------------------------------------

df["curvature_magnitude_indicator"] = normalize(
    df["mean_curvature"].abs()
)


# --------------------------------------------------
# GIS FEATURE INDEX
# --------------------------------------------------

# This is NOT the final MineGuard risk score.
# It is only a normalized GIS terrain indicator
# that can later be combined with IoT and ML outputs.

df["gis_terrain_indicator"] = (
    0.30 * df["slope_indicator"]
    +
    0.20 * df["slope_extreme_indicator"]
    +
    0.20 * df["roughness_indicator"]
    +
    0.10 * df["roughness_extreme_indicator"]
    +
    0.10 * df["elevation_variability_indicator"]
    +
    0.10 * df["curvature_magnitude_indicator"]
)


# --------------------------------------------------
# CLIP TO 0-1
# --------------------------------------------------

df["gis_terrain_indicator"] = (
    df["gis_terrain_indicator"]
    .clip(0, 1)
)


# --------------------------------------------------
# CLASSIFY TERRAIN CONDITION
# --------------------------------------------------

def classify_terrain(value):

    if value < 0.33:

        return "LOW"

    elif value < 0.66:

        return "MODERATE"

    else:

        return "HIGH"


df["gis_terrain_condition"] = (
    df["gis_terrain_indicator"]
    .apply(classify_terrain)
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n==========================================")
print("GIS INDICATOR GENERATION COMPLETED")
print("==========================================")

print(
    f"\nOutput file:\n{OUTPUT_FILE}"
)

print(
    f"\nZones processed: "
    f"{len(df)}"
)


print("\nGIS terrain conditions:")

print(
    df[
        "gis_terrain_condition"
    ].value_counts()
)


print("\nZone summary:")

print(
    df[
        [
            "zone_id",
            "gis_terrain_indicator",
            "gis_terrain_condition"
        ]
    ].to_string(
        index=False
    )
)


print("\n==========================================")
print("GIS LAYER READY FOR API / ML INTEGRATION")
print("==========================================")