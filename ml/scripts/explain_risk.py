from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parents[2]

ZONE_API_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zone_api_data.json"
)


with open(
    ZONE_API_FILE,
    "r",
    encoding="utf-8"
) as file:
    zones = json.load(file)


def explain_zone(zone):

    gis = zone.get("gis", {})
    risk = zone.get("risk", {})

    slope = float(
        gis.get("mean_slope_deg") or 0
    )

    max_slope = float(
        gis.get("max_slope_deg") or 0
    )

    roughness = float(
        gis.get("mean_roughness") or 0
    )

    max_roughness = float(
        gis.get("max_roughness") or 0
    )

    slope_indicator = float(
        gis.get("slope_indicator") or 0
    )

    roughness_indicator = float(
        gis.get("roughness_indicator") or 0
    )

    variability_indicator = float(
        gis.get("terrain_variability_indicator") or 0
    )

    gis_indicator = float(
        gis.get("gis_terrain_indicator") or 0
    )

    risk_level = risk.get(
        "level",
        "UNKNOWN"
    )

    probability = risk.get(
        "probability"
    )

    factors = []

    if slope_indicator >= 0.70:
        factors.append(
            "High terrain slope"
        )
    elif slope_indicator >= 0.35:
        factors.append(
            "Moderate terrain slope"
        )

    if roughness_indicator >= 0.70:
        factors.append(
            "High terrain roughness"
        )
    elif roughness_indicator >= 0.35:
        factors.append(
            "Moderate terrain roughness"
        )

    if variability_indicator >= 0.70:
        factors.append(
            "High terrain variability"
        )
    elif variability_indicator >= 0.35:
        factors.append(
            "Moderate terrain variability"
        )

    if max_slope >= 45:
        factors.append(
            "Very steep local slope"
        )

    if max_roughness >= 100:
        factors.append(
            "High local surface roughness"
        )

    if not factors:
        factors.append(
            "Terrain indicators are currently low"
        )

    if risk_level == "HIGH":

        recommendation = (
            "Prioritize inspection and "
            "continuous monitoring of this zone."
        )

    elif risk_level == "MODERATE":

        recommendation = (
            "Increase monitoring frequency "
            "and inspect terrain conditions."
        )

    elif risk_level == "LOW":

        recommendation = (
            "Continue routine monitoring."
        )

    else:

        recommendation = (
            "Risk assessment requires additional data."
        )

    explanation = {
        "risk_level": risk_level,
        "probability": probability,
        "primary_factors": factors,
        "recommendation": recommendation,
        "metrics": {
            "mean_slope_deg": slope,
            "max_slope_deg": max_slope,
            "mean_roughness": roughness,
            "max_roughness": max_roughness,
            "slope_indicator": slope_indicator,
            "roughness_indicator": roughness_indicator,
            "terrain_variability_indicator":
                variability_indicator,
            "gis_terrain_indicator":
                gis_indicator
        }
    }

    return explanation


for zone in zones:

    zone["risk"]["explanation"] = (
        explain_zone(zone)
    )


with open(
    ZONE_API_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        zones,
        file,
        indent=2
    )


print("==========================================")
print("MineGuard AI - Explainable Risk Engine")
print("==========================================")

for zone in zones:

    explanation = zone[
        "risk"
    ][
        "explanation"
    ]

    probability = explanation[
        "probability"
    ]

    if probability is not None:
        probability_text = (
            f"{float(probability) * 100:.2f}%"
        )
    else:
        probability_text = "N/A"

    print()
    print(
        f"{zone['zone_id']} | "
        f"{explanation['risk_level']} | "
        f"{probability_text}"
    )

    print(
        "Factors:"
    )

    for factor in explanation[
        "primary_factors"
    ]:

        print(
            f"  - {factor}"
        )

    print(
        f"Recommendation: "
        f"{explanation['recommendation']}"
    )


print()
print("==========================================")
print("EXPLAINABLE RISK DATA SAVED")
print("==========================================")
print()
print(ZONE_API_FILE)