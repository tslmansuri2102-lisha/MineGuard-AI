from pathlib import Path
import json
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "mine_zone_features.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "zone_api_data.json"
)


print("==========================================")
print("MineGuard AI - Zone API Data Generator")
print("==========================================")


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"File not found:\n{INPUT_FILE}"
    )


df = pd.read_csv(INPUT_FILE)

zones = []

for _, row in df.iterrows():

    zone = {
        "mine_id": row["mine_id"],
        "zone_id": row["zone_id"],

        "gis": {
            "area_sq_km": row["area_sq_km"],
            "mean_elevation_m": row["mean_elevation_m"],
            "min_elevation_m": row["min_elevation_m"],
            "max_elevation_m": row["max_elevation_m"],
            "mean_slope_deg": row["mean_slope_deg"],
            "max_slope_deg": row["max_slope_deg"],
            "mean_aspect_deg": row["mean_aspect_deg"],
            "mean_curvature": row["mean_curvature"],
            "mean_roughness": row["mean_roughness"],
            "max_roughness": row["max_roughness"],
            "road_count": row["road_count"],
            "road_length_km": row["road_length_km"],

            "slope_indicator": row["slope_indicator"],
            "roughness_indicator": row["roughness_indicator"],
            "terrain_variability_indicator": row[
                "terrain_variability_indicator"
            ],
            "gis_terrain_indicator": row[
                "gis_terrain_indicator"
            ],
            "gis_terrain_condition": row[
                "gis_terrain_condition"
            ]
        },

        "realtime": {
            "displacement_mm": None,
            "strain": None,
            "pore_pressure_kpa": None,
            "rainfall_mm": None,
            "temperature_c": None,
            "vibration_g": None
        },

        "risk": {
            "level": "UNKNOWN",
            "probability": None
        }
    }

    zones.append(zone)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        zones,
        f,
        indent=2,
        allow_nan=False
    )


print("\n==========================================")
print("ZONE API DATA CREATED")
print("==========================================")

print(
    f"\nZones: {len(zones)}"
)

print(
    f"Output:\n{OUTPUT_FILE}"
)

print("\n==========================================")
print("READY FOR BACKEND INTEGRATION")
print("==========================================")