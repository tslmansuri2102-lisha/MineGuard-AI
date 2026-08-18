from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "nasa_global_landslide_catalog.csv"
)


print("==========================================")
print("MineGuard AI - Historical Dataset Analysis")
print("==========================================")


if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nDataset not found:\n{INPUT_FILE}"
    )


df = pd.read_csv(
    INPUT_FILE
)


print("\nDataset:")
print(
    f"Records : {len(df)}"
)

print(
    f"Columns : {len(df.columns)}"
)


# --------------------------------------------------
# INDIA
# --------------------------------------------------

india = df[
    df["country_name"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "india"
].copy()


print("\n==========================================")
print("INDIA")
print("==========================================")

print(
    f"India events: {len(india)}"
)


print("\nIndian states / regions:")

print(
    india[
        "admin_division_name"
    ]
    .value_counts()
    .head(20)
)


# --------------------------------------------------
# JHARKHAND
# --------------------------------------------------

jharkhand = india[
    india[
        "admin_division_name"
    ]
    .astype(str)
    .str.contains(
        "jharkhand",
        case=False,
        na=False
    )
].copy()


print("\n==========================================")
print("JHARKHAND")
print("==========================================")

print(
    f"Jharkhand events: {len(jharkhand)}"
)


if len(jharkhand) > 0:

    print("\nJharkhand triggers:")

    print(
        jharkhand[
            "landslide_trigger"
        ]
        .value_counts()
    )


    print("\nJharkhand categories:")

    print(
        jharkhand[
            "landslide_category"
        ]
        .value_counts()
    )


    print("\nJharkhand sizes:")

    print(
        jharkhand[
            "landslide_size"
        ]
        .value_counts()
    )


    print("\nJharkhand settings:")

    print(
        jharkhand[
            "landslide_setting"
        ]
        .value_counts()
    )


# --------------------------------------------------
# COORDINATE RANGE
# --------------------------------------------------

print("\n==========================================")
print("COORDINATE COVERAGE")
print("==========================================")


if len(jharkhand) > 0:

    print(
        f"Latitude range : "
        f"{jharkhand['latitude'].min():.4f}"
        f" to "
        f"{jharkhand['latitude'].max():.4f}"
    )

    print(
        f"Longitude range: "
        f"{jharkhand['longitude'].min():.4f}"
        f" to "
        f"{jharkhand['longitude'].max():.4f}"
    )


# --------------------------------------------------
# KUSUNDA BOUNDING BOX
# --------------------------------------------------

MIN_LAT = 23.7790
MAX_LAT = 23.7850

MIN_LON = 86.3900
MAX_LON = 86.3980


kusunda = df[
    df["latitude"].between(
        MIN_LAT,
        MAX_LAT
    )
    &
    df["longitude"].between(
        MIN_LON,
        MAX_LON
    )
].copy()


print("\n==========================================")
print("KUSUNDA STUDY AREA")
print("==========================================")

print(
    f"Events inside current Kusunda box: "
    f"{len(kusunda)}"
)


if len(kusunda) > 0:

    print(
        kusunda[
            [
                "event_id",
                "event_date",
                "landslide_category",
                "landslide_trigger",
                "latitude",
                "longitude"
            ]
        ].to_string(
            index=False
        )
    )


print("\n==========================================")
print("ANALYSIS COMPLETED")
print("==========================================")