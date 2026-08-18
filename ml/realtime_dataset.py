"""
MineGuard AI — Real-Time Sensor Dataset Generator

Generates a simulator-derived temporal dataset for the dedicated
real-time sensor ML model.

IMPORTANT:
The labels in this dataset are derived from simulator scenarios.
They are NOT real-world rockfall ground truth.
"""

import json
import os
from collections import Counter

import pandas as pd

from ml.utils import logger
from simulation.sensor_simulator import run_simulation
from inference.rolling_window import RollingWindowBuffer


REALTIME_SENSOR_FEATURES = [
    "vibration_g",
    "vibration_change_rate",
    "vibration_acceleration",
    "strain",
    "strain_change_rate",
    "displacement_mm",
    "displacement_change_rate",
    "slope_velocity_mm_s",
    "slope_velocity_change_rate",
    "rainfall_mm",
    "rainfall_1h",
    "rainfall_6h",
    "sensor_anomaly_score",
]

TARGET_COL = "sensor_rockfall_risk"

SCENARIO_LABELS = {
    "NORMAL": 0,
    "DEVELOPING_INSTABILITY": 0,
    "HIGH_RISK": 1,
    "CRITICAL_ROCKFALL": 1,
}

SCENARIOS = list(SCENARIO_LABELS.keys())

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

OUTPUT_DIR = os.path.join(BASE_DIR, "data", "realtime")
DATASET_FILE = os.path.join(OUTPUT_DIR, "sensor_training.csv")
METADATA_FILE = os.path.join(OUTPUT_DIR, "dataset_metadata.json")


def extract_realtime_features(
    telemetry: dict,
    rolling_features: dict
) -> dict:
    """
    Extract exactly the 13 features used by the real-time model.
    """

    return {
        "vibration_g": float(
            telemetry.get("vibration_g", 0.0)
        ),

        "vibration_change_rate": float(
            rolling_features.get("vibration_change_rate", 0.0)
        ),

        "vibration_acceleration": float(
            rolling_features.get("vibration_acceleration", 0.0)
        ),

        "strain": float(
            telemetry.get("strain", 0.0)
        ),

        "strain_change_rate": float(
            rolling_features.get("strain_change_rate", 0.0)
        ),

        "displacement_mm": float(
            telemetry.get("displacement_mm", 0.0)
        ),

        "displacement_change_rate": float(
            rolling_features.get("displacement_change_rate", 0.0)
        ),

        "slope_velocity_mm_s": float(
            telemetry.get("slope_velocity_mm_s", 0.0)
        ),

        "slope_velocity_change_rate": float(
            rolling_features.get(
                "slope_velocity_change_rate",
                0.0
            )
        ),

        "rainfall_mm": float(
            telemetry.get("rainfall_mm", 0.0)
        ),

        "rainfall_1h": float(
            telemetry.get(
                "rainfall_1h",
                rolling_features.get("rainfall_1h", 0.0)
            )
        ),

        "rainfall_6h": float(
            telemetry.get(
                "rainfall_6h",
                rolling_features.get("rainfall_6h", 0.0)
            )
        ),

        "sensor_anomaly_score": float(
            rolling_features.get("sensor_anomaly_score", 0.0)
        ),
    }


def generate_dataset(
    sequences_per_scenario: int = 100,
    sequence_length: int = 30,
    seed: int = 42,
) -> tuple[pd.DataFrame, dict]:
    """
    Generate simulator-derived temporal training data.

    Each sequence gets its own sensor ID so rolling-window state does not
    leak between independent sequences.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows = []

    logger.info("Generating real-time sensor training dataset...")
    logger.info(
        "Scenarios=%d | Sequences/scenario=%d | Length=%d",
        len(SCENARIOS),
        sequences_per_scenario,
        sequence_length,
    )

    for scenario_index, scenario in enumerate(SCENARIOS):

        label = SCENARIO_LABELS[scenario]

        for sequence_index in range(sequences_per_scenario):

            # Every sequence gets a deterministic but unique seed.
            sequence_seed = (
                seed
                + scenario_index * 100000
                + sequence_index
            )

            sensor_id = (
                f"RT-{scenario_index:02d}-"
                f"{sequence_index:04d}"
            )

            events = run_simulation(
                scenario=scenario,
                zone_id="ZONE-003",
                sensor_id=sensor_id,
                interval=1.0,
                duration=sequence_length,
                seed=sequence_seed,
                api_url=None,
                sleep_enabled=False,
            )

            # Fresh rolling buffer for every independent sequence.
            rolling_buffer = RollingWindowBuffer(
                window_size=60
            )

            for step_index, telemetry in enumerate(events):

                rolling_features = (
                    rolling_buffer.add_telemetry(
                        telemetry
                    )
                )

                features = extract_realtime_features(
                    telemetry,
                    rolling_features,
                )

                row = {
                    **features,
                    TARGET_COL: label,
                    "scenario": scenario,
                    "sequence_id": sensor_id,
                    "step_index": step_index,
                }

                rows.append(row)

    df = pd.DataFrame(rows)

    # Ensure deterministic feature ordering.
    ordered_columns = (
        REALTIME_SENSOR_FEATURES
        + [
            TARGET_COL,
            "scenario",
            "sequence_id",
            "step_index",
        ]
    )

    df = df[ordered_columns]

    # Save dataset.
    df.to_csv(DATASET_FILE, index=False)

    scenario_counts = Counter(
        df["scenario"].tolist()
    )

    positive_count = int(
        (df[TARGET_COL] == 1).sum()
    )

    negative_count = int(
        (df[TARGET_COL] == 0).sum()
    )

    metadata = {
        "dataset_type": "simulator_derived_realtime_sensor_dataset",
        "warning": (
            "Labels are derived from simulator scenarios and "
            "are NOT real-world rockfall ground truth."
        ),
        "random_seed": seed,
        "sequences_per_scenario": sequences_per_scenario,
        "sequence_length": sequence_length,
        "scenario_labels": SCENARIO_LABELS,
        "feature_count": len(REALTIME_SENSOR_FEATURES),
        "features": REALTIME_SENSOR_FEATURES,
        "target": TARGET_COL,
        "total_samples": len(df),
        "positive_samples": positive_count,
        "negative_samples": negative_count,
        "positive_ratio": (
            positive_count / len(df)
            if len(df) > 0
            else 0.0
        ),
        "scenario_sample_counts": dict(scenario_counts),
    }

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2
        )

    logger.info(
        "Real-time dataset generated successfully: %s",
        DATASET_FILE
    )

    logger.info(
        "Total samples: %d | Positive: %d | Negative: %d",
        len(df),
        positive_count,
        negative_count,
    )

    return df, metadata


if __name__ == "__main__":

    df, metadata = generate_dataset()

    print("\n==============================================")
    print("MINEGUARD AI REAL-TIME DATASET")
    print("==============================================")
    print("Dataset:", DATASET_FILE)
    print("Metadata:", METADATA_FILE)
    print("Samples:", len(df))
    print("Features:", len(REALTIME_SENSOR_FEATURES))
    print("Positive:", metadata["positive_samples"])
    print("Negative:", metadata["negative_samples"])
    print(
        "Positive ratio:",
        round(metadata["positive_ratio"], 4)
    )

    print("\nScenario counts:")
    for scenario, count in metadata[
        "scenario_sample_counts"
    ].items():
        print(f"  {scenario}: {count}")

    print("\nFeature columns:")
    for feature in REALTIME_SENSOR_FEATURES:
        print(f"  - {feature}")

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))