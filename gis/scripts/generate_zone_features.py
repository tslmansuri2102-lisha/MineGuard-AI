from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask


BASE_DIR = Path(__file__).resolve().parents[2]

ZONE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zones.geojson"
)

ROAD_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "gis"
    / "roads.geojson"
)

DEM_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "dem_features"
)

DEM_FILE = DEM_DIR / "kusunda_dem.tif"
SLOPE_FILE = DEM_DIR / "slope.tif"
ASPECT_FILE = DEM_DIR / "aspect.tif"
CURVATURE_FILE = DEM_DIR / "curvature.tif"
ROUGHNESS_FILE = DEM_DIR / "roughness.tif"

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
)

OUTPUT_FILE = OUTPUT_DIR / "zone_features.csv"


print("==========================================")
print("MineGuard AI - Zone Feature Generator")
print("==========================================")


# --------------------------------------------------
# CHECK FILES
# --------------------------------------------------

required_files = [
    ZONE_FILE,
    ROAD_FILE,
    DEM_FILE,
    SLOPE_FILE,
    ASPECT_FILE,
    CURVATURE_FILE,
    ROUGHNESS_FILE
]

for file in required_files:

    if not file.exists():

        raise FileNotFoundError(
            f"\nRequired file not found:\n{file}"
        )


# --------------------------------------------------
# LOAD ZONES
# --------------------------------------------------

print("\nLoading mine zones...")

zones = gpd.read_file(
    ZONE_FILE
)

if zones.empty:
    raise ValueError(
        "zones.geojson contains no zones."
    )

zones = zones.to_crs(
    "EPSG:4326"
)

print(
    f"Zones loaded: {len(zones)}"
)


# --------------------------------------------------
# LOAD ROADS
# --------------------------------------------------

print("\nLoading road network...")

roads = gpd.read_file(
    ROAD_FILE
)

roads = roads.to_crs(
    zones.crs
)

print(
    f"Road features loaded: {len(roads)}"
)


# --------------------------------------------------
# PROJECT ZONES AND ROADS
# --------------------------------------------------

METRIC_CRS = "EPSG:32645"

zones_metric = zones.to_crs(
    METRIC_CRS
)

roads_metric = roads.to_crs(
    METRIC_CRS
)


# --------------------------------------------------
# ROAD FEATURES
# --------------------------------------------------

road_counts = []

road_lengths = []

for _, zone in zones_metric.iterrows():

    zone_geometry = zone.geometry

    intersecting_roads = roads_metric[
        roads_metric.geometry.intersects(
            zone_geometry
        )
    ]

    road_count = len(
        intersecting_roads
    )

    road_length_km = (
        intersecting_roads.geometry
        .intersection(
            zone_geometry
        )
        .length
        .sum()
        / 1000
    )

    road_counts.append(
        road_count
    )

    road_lengths.append(
        road_length_km
    )


# --------------------------------------------------
# RASTER STATISTICS
# --------------------------------------------------

def raster_statistics(
    raster_file,
    zone_geometry,
    zone_crs,
    circular=False
):

    with rasterio.open(
        raster_file
    ) as src:

        # ------------------------------------------
        # CONVERT ZONE TO THIS RASTER'S CRS
        # ------------------------------------------

        zone = gpd.GeoSeries(
            [zone_geometry],
            crs=zone_crs
        )

        zone = zone.to_crs(
            src.crs
        )

        geometry = [
            zone.iloc[0]
        ]

        # ------------------------------------------
        # CLIP RASTER
        # ------------------------------------------

        try:

            clipped, _ = mask(
                src,
                geometry,
                crop=True,
                filled=False
            )

        except ValueError:

            return {
                "mean": np.nan,
                "minimum": np.nan,
                "maximum": np.nan,
                "std": np.nan,
                "circular_mean": np.nan
            }

        values = clipped[0]

        values = values.compressed()

        values = values[
            np.isfinite(values)
        ]

        if len(values) == 0:

            return {
                "mean": np.nan,
                "minimum": np.nan,
                "maximum": np.nan,
                "std": np.nan,
                "circular_mean": np.nan
            }

        # ------------------------------------------
        # CIRCULAR MEAN FOR ASPECT
        # ------------------------------------------

        if circular:

            radians = np.radians(
                values
            )

            sin_mean = np.mean(
                np.sin(radians)
            )

            cos_mean = np.mean(
                np.cos(radians)
            )

            circular_mean = (
                np.degrees(
                    np.arctan2(
                        sin_mean,
                        cos_mean
                    )
                )
                % 360
            )

        else:

            circular_mean = np.nan

        return {

            "mean": float(
                np.mean(values)
            ),

            "minimum": float(
                np.min(values)
            ),

            "maximum": float(
                np.max(values)
            ),

            "std": float(
                np.std(values)
            ),

            "circular_mean": float(
                circular_mean
            )
        }


# --------------------------------------------------
# GENERATE FEATURES
# --------------------------------------------------

records = []


for index, zone in zones.iterrows():

    zone_id = zone[
        "zone_id"
    ]

    mine_id = zone[
        "mine_id"
    ]

    print(
        f"\nProcessing {zone_id}..."
    )


    # ----------------------------------------------
    # DEM
    # ----------------------------------------------

    dem_stats = raster_statistics(
        DEM_FILE,
        zone.geometry,
        zones.crs
    )


    # ----------------------------------------------
    # SLOPE
    # ----------------------------------------------

    slope_stats = raster_statistics(
        SLOPE_FILE,
        zone.geometry,
        zones.crs
    )


    # ----------------------------------------------
    # ASPECT
    # ----------------------------------------------

    aspect_stats = raster_statistics(
        ASPECT_FILE,
        zone.geometry,
        zones.crs,
        circular=True
    )


    # ----------------------------------------------
    # CURVATURE
    # ----------------------------------------------

    curvature_stats = raster_statistics(
        CURVATURE_FILE,
        zone.geometry,
        zones.crs
    )


    # ----------------------------------------------
    # ROUGHNESS
    # ----------------------------------------------

    roughness_stats = raster_statistics(
        ROUGHNESS_FILE,
        zone.geometry,
        zones.crs
    )


    # ----------------------------------------------
    # ZONE AREA
    # ----------------------------------------------

    area_sq_km = (
        zones_metric.iloc[index]
        .geometry
        .area
        / 1_000_000
    )


    # ----------------------------------------------
    # BUILD RECORD
    # ----------------------------------------------

    record = {

        "mine_id": mine_id,

        "zone_id": zone_id,

        "area_sq_km": round(
            area_sq_km,
            6
        ),

        "mean_elevation_m": round(
            dem_stats["mean"],
            3
        ),

        "min_elevation_m": round(
            dem_stats["minimum"],
            3
        ),

        "max_elevation_m": round(
            dem_stats["maximum"],
            3
        ),

        "elevation_std_m": round(
            dem_stats["std"],
            3
        ),

        "mean_slope_deg": round(
            slope_stats["mean"],
            3
        ),

        "max_slope_deg": round(
            slope_stats["maximum"],
            3
        ),

        "slope_std_deg": round(
            slope_stats["std"],
            3
        ),

        "mean_aspect_deg": round(
            aspect_stats["circular_mean"],
            3
        ),

        "mean_curvature": round(
            curvature_stats["mean"],
            6
        ),

        "mean_roughness": round(
            roughness_stats["mean"],
            3
        ),

        "max_roughness": round(
            roughness_stats["maximum"],
            3
        ),

        "road_count": road_counts[index],

        "road_length_km": round(
            road_lengths[index],
            4
        )
    }

    records.append(
        record
    )


# --------------------------------------------------
# CREATE DATAFRAME
# --------------------------------------------------

features = pd.DataFrame(
    records
)


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

features.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n==========================================")
print("ZONE FEATURE GENERATION COMPLETED")
print("==========================================")

print(
    f"\nOutput:\n{OUTPUT_FILE}"
)

print(
    f"\nZones processed: "
    f"{len(features)}"
)

print(
    f"Features generated: "
    f"{len(features.columns)}"
)

print("\nGenerated columns:")

for column in features.columns:

    print(
        f"  - {column}"
    )

print("\nPreview:")

print(
    features.to_string(
        index=False
    )
)

print("\n==========================================")
print("GIS FEATURES READY FOR ML INTEGRATION")
print("==========================================")