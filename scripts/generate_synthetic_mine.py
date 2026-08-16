"""
Mineguard-AI
Synthetic Open-Pit Mine Sensor Dataset Generator

Generates reproducible synthetic sensor data for rockfall prediction.
This dataset is intended for development, testing, and demonstration.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

SEED = 42
N_RECORDS = 30_000

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "synthetic"
    / "synthetic_mine.csv"
)


# ============================================================
# Dataset generation
# ============================================================

def generate_dataset(n_records: int = N_RECORDS, seed: int = SEED):
    rng = np.random.default_rng(seed)

    # --------------------------------------------------------
    # Mine and zone identifiers
    # --------------------------------------------------------

    mines = np.array(["MINE_01", "MINE_02", "MINE_03", "MINE_04"])

    mine_id = rng.choice(
        mines,
        size=n_records,
        p=[0.30, 0.25, 0.25, 0.20],
    )

    zone_id = np.array(
        [
            f"{mine}_ZONE_{rng.integers(1, 11):02d}"
            for mine in mine_id
        ]
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    start_date = pd.Timestamp("2024-01-01")

    timestamps = pd.date_range(
        start=start_date,
        periods=n_records,
        freq="1h",
    )

    # Shuffle timestamps so different zones/mines receive
    # observations throughout the period.
    timestamps = rng.permutation(timestamps)

    timestamp = pd.to_datetime(timestamps)

    # --------------------------------------------------------
    # Environmental variables
    # --------------------------------------------------------

    month = timestamp.month.to_numpy()

    # Seasonal rainfall pattern.
    seasonal_rain = np.where(
        np.isin(month, [6, 7, 8, 9]),
        rng.gamma(shape=2.5, scale=8.0, size=n_records),
        rng.gamma(shape=1.5, scale=3.0, size=n_records),
    )

    rainfall = np.clip(seasonal_rain, 0, 150)

    temperature = (
        27
        + 5 * np.sin((month - 1) / 12 * 2 * np.pi)
        + rng.normal(0, 2.5, n_records)
    )

    temperature = np.clip(temperature, 10, 45)

    # --------------------------------------------------------
    # Geotechnical variables
    # --------------------------------------------------------

    # Steeper slopes generally represent greater instability.
    slope_angle = rng.normal(48, 8, n_records)
    slope_angle = np.clip(slope_angle, 25, 75)

    # Rainfall contributes to pore pressure.
    pore_pressure = (
        35
        + 0.55 * rainfall
        + rng.normal(0, 12, n_records)
    )
    pore_pressure = np.clip(pore_pressure, 5, 180)

    # --------------------------------------------------------
    # Displacement
    # --------------------------------------------------------

    # Base displacement influenced by slope, rainfall and noise.
    displacement = (
        5
        + 0.15 * (slope_angle - 40)
        + 0.025 * rainfall
        + rng.gamma(2.0, 2.5, n_records)
    )

    displacement = np.clip(displacement, 0.1, 100)

    # --------------------------------------------------------
    # Displacement velocity
    # --------------------------------------------------------

    displacement_velocity = (
        0.03
        + 0.008 * displacement
        + 0.0015 * rainfall
        + rng.normal(0, 0.025, n_records)
    )

    displacement_velocity = np.clip(
        displacement_velocity,
        0.001,
        5,
    )

    # --------------------------------------------------------
    # Displacement acceleration
    # --------------------------------------------------------

    displacement_acceleration = (
        0.001
        + 0.025 * displacement_velocity
        + rng.normal(0, 0.008, n_records)
    )

    displacement_acceleration = np.clip(
        displacement_acceleration,
        0.0001,
        1,
    )

    # --------------------------------------------------------
    # Strain
    # --------------------------------------------------------

    strain = (
        0.10
        + 0.015 * displacement
        + 0.04 * displacement_velocity
        + rng.normal(0, 0.04, n_records)
    )

    strain = np.clip(strain, 0.001, 5)

    # --------------------------------------------------------
    # Vibration
    # --------------------------------------------------------

    vibration = (
        0.5
        + 0.02 * displacement_velocity
        + 0.005 * slope_angle
        + rng.normal(0, 0.15, n_records)
    )

    vibration = np.clip(vibration, 0.01, 10)

    # ========================================================
    # Rockfall risk mechanism
    # ========================================================

    # Standardize important variables approximately around
    # their typical ranges.
    slope_risk = (slope_angle - 45) / 10
    displacement_risk = (displacement - 15) / 10
    velocity_risk = (displacement_velocity - 0.15) / 0.10
    acceleration_risk = (
        displacement_acceleration - 0.01
    ) / 0.02
    strain_risk = (strain - 0.4) / 0.3
    pressure_risk = (pore_pressure - 60) / 30
    rainfall_risk = (rainfall - 20) / 20
    vibration_risk = (vibration - 0.8) / 0.5

    # Combined risk score.
    #
    # Importantly, this is NOT a deterministic threshold.
    # A probability is calculated from the score and then
    # the event is sampled probabilistically.
    risk_score = (
        0.75 * slope_risk
        + 1.20 * displacement_risk
        + 1.35 * velocity_risk
        + 0.90 * acceleration_risk
        + 0.75 * strain_risk
        + 1.05 * pressure_risk
        + 0.80 * rainfall_risk
        + 0.65 * vibration_risk
        + rng.normal(0, 1.0, n_records)
    )

    # Logistic transformation to probability.
    probability = 1 / (1 + np.exp(-risk_score))

    # Reduce the overall event rate so the dataset is
    # imbalanced like a safety-event prediction problem.
    probability = probability * 0.22

    probability = np.clip(probability, 0.001, 0.85)

    rockfall_event = (
        rng.random(n_records) < probability
    ).astype(int)

    # ========================================================
    # Create DataFrame
    # ========================================================

    df = pd.DataFrame(
        {
            "mine_id": mine_id,
            "zone_id": zone_id,
            "timestamp": timestamp,
            "slope_angle": slope_angle,
            "displacement": displacement,
            "displacement_velocity": displacement_velocity,
            "displacement_acceleration": displacement_acceleration,
            "strain": strain,
            "pore_pressure": pore_pressure,
            "rainfall": rainfall,
            "temperature": temperature,
            "vibration": vibration,
            "rockfall_event": rockfall_event,
        }
    )

    # Sort chronologically.
    df = df.sort_values(
        ["timestamp", "mine_id", "zone_id"]
    ).reset_index(drop=True)

    return df


# ============================================================
# Validation
# ============================================================

def validate_dataset(df: pd.DataFrame):
    expected_columns = [
        "mine_id",
        "zone_id",
        "timestamp",
        "slope_angle",
        "displacement",
        "displacement_velocity",
        "displacement_acceleration",
        "strain",
        "pore_pressure",
        "rainfall",
        "temperature",
        "vibration",
        "rockfall_event",
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    if df[expected_columns].isnull().any().any():
        raise ValueError(
            "Dataset contains missing values."
        )

    duplicate_count = df.duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"Dataset contains {duplicate_count} duplicate rows."
        )

    if not set(df["rockfall_event"].unique()).issubset({0, 1}):
        raise ValueError(
            "rockfall_event must contain only 0 and 1."
        )

    numeric_ranges = {
        "slope_angle": (25, 75),
        "displacement": (0, 100),
        "displacement_velocity": (0, 5),
        "displacement_acceleration": (0, 1),
        "strain": (0, 5),
        "pore_pressure": (0, 180),
        "rainfall": (0, 150),
        "temperature": (10, 45),
        "vibration": (0, 10),
    }

    for column, (lower, upper) in numeric_ranges.items():
        if not df[column].between(
            lower, upper
        ).all():
            raise ValueError(
                f"Values outside expected range in {column}."
            )

    return duplicate_count


# ============================================================
# Report
# ============================================================

def print_report(df: pd.DataFrame, duplicate_count: int):
    event_count = int(
        df["rockfall_event"].sum()
    )

    event_rate = (
        event_count / len(df) * 100
    )

    print("\n" + "=" * 60)
    print("MINEGUARD-AI SYNTHETIC DATASET REPORT")
    print("=" * 60)

    print(f"Records              : {len(df):,}")
    print(
        f"Mines                : {df['mine_id'].nunique()}"
    )
    print(
        f"Zones                : {df['zone_id'].nunique()}"
    )
    print(
        f"Date range           : "
        f"{df['timestamp'].min()} -> "
        f"{df['timestamp'].max()}"
    )

    print(
        f"Rockfall events      : {event_count:,}"
    )
    print(
        f"Rockfall event rate  : {event_rate:.2f}%"
    )

    print(
        f"Missing values       : "
        f"{df.isnull().sum().sum()}"
    )

    print(
        f"Duplicate rows       : {duplicate_count}"
    )

    print("\nSensor statistics:")
    print("-" * 60)

    sensor_columns = [
        "slope_angle",
        "displacement",
        "displacement_velocity",
        "displacement_acceleration",
        "strain",
        "pore_pressure",
        "rainfall",
        "temperature",
        "vibration",
    ]

    for column in sensor_columns:
        print(
            f"{column:28s}"
            f"min={df[column].min():8.3f} "
            f"max={df[column].max():8.3f} "
            f"mean={df[column].mean():8.3f}"
        )

    print("=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Generating synthetic mine dataset...")

    df = generate_dataset()

    duplicate_count = validate_dataset(df)

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print_report(
        df,
        duplicate_count,
    )

    print(
        f"\nSaved successfully to:\n{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()