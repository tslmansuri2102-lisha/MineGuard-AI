from pathlib import Path

import geopandas as gpd
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "nasa_global_landslide_catalog.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "historical_landslides.geojson"
)


print("==========================================")
print("MineGuard AI - Landslide GIS Preparation")
print("==========================================")


# --------------------------------------------------
# CHECK INPUT FILE
# --------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nDataset not found:\n{INPUT_FILE}\n\n"
        "Make sure the CSV is inside data/raw/"
    )


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

print("\nLoading NASA Global Landslide Catalog...")

df = pd.read_csv(INPUT_FILE)

print(f"Records loaded : {len(df)}")
print(f"Columns        : {len(df.columns)}")


# --------------------------------------------------
# REQUIRED COLUMNS
# --------------------------------------------------

required_columns = [
    "event_id",
    "event_date",
    "landslide_category",
    "landslide_trigger",
    "landslide_size",
    "landslide_setting",
    "country_name",
    "latitude",
    "longitude"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(
            f"- {column}"
            for column in missing_columns
        )
    )


# --------------------------------------------------
# CLEAN COORDINATES
# --------------------------------------------------

print("\nCleaning coordinates...")

df["latitude"] = pd.to_numeric(
    df["latitude"],
    errors="coerce"
)

df["longitude"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)

before = len(df)

df = df.dropna(
    subset=[
        "latitude",
        "longitude"
    ]
).copy()

removed_missing = before - len(df)

print(
    f"Removed records with missing coordinates: "
    f"{removed_missing}"
)


# --------------------------------------------------
# VALIDATE COORDINATE RANGES
# --------------------------------------------------

valid_coordinates = (
    df["latitude"].between(-90, 90)
    &
    df["longitude"].between(-180, 180)
)

invalid_count = (~valid_coordinates).sum()

if invalid_count > 0:

    print(
        f"Removing invalid coordinates: "
        f"{invalid_count}"
    )

    df = df[
        valid_coordinates
    ].copy()


# --------------------------------------------------
# REMOVE DUPLICATE EVENTS
# --------------------------------------------------

before_duplicates = len(df)

df = df.drop_duplicates(
    subset=["event_id"]
)

duplicates_removed = (
    before_duplicates - len(df)
)

print(
    f"Duplicate events removed: "
    f"{duplicates_removed}"
)


# --------------------------------------------------
# CREATE GEOMETRY
# --------------------------------------------------

print("\nCreating spatial points...")

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
)


# --------------------------------------------------
# SAVE GEOJSON
# --------------------------------------------------

print("\nSaving GIS dataset...")

gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n==========================================")
print("GIS DATASET CREATED")
print("==========================================")

print(
    f"Original records : {before}"
)

print(
    f"Final records    : {len(gdf)}"
)

print(
    f"Output file      :\n{OUTPUT_FILE}"
)

print(
    f"\nCountries represented: "
    f"{gdf['country_name'].nunique()}"
)

india_count = (
    gdf["country_name"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("india")
    .sum()
)

print(
    f"India records: "
    f"{india_count}"
)


# --------------------------------------------------
# LANDSLIDE CATEGORY SUMMARY
# --------------------------------------------------

print("\nTop landslide categories:")

print(
    gdf["landslide_category"]
    .value_counts()
    .head(10)
)


# --------------------------------------------------
# TRIGGER SUMMARY
# --------------------------------------------------

print("\nTop landslide triggers:")

print(
    gdf["landslide_trigger"]
    .value_counts()
    .head(10)
)


# --------------------------------------------------
# SIZE SUMMARY
# --------------------------------------------------

print("\nLandslide sizes:")

print(
    gdf["landslide_size"]
    .value_counts()
    .head(10)
)


print("\n==========================================")
print("READY FOR SPATIAL ANALYSIS")
print("==========================================")