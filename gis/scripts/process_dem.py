from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping


BASE_DIR = Path(__file__).resolve().parents[2]

DEM_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "gis"
    / "dem"
    / "N23E086.tif"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "dem_features"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = OUTPUT_DIR / "kusunda_dem.tif"


# --------------------------------------------------
# KUSUNDA STUDY AREA
# --------------------------------------------------

MIN_LAT = 23.7790
MAX_LAT = 23.7850

MIN_LON = 86.3900
MAX_LON = 86.3980


print("==========================================")
print("MineGuard AI - DEM Processing")
print("==========================================")


# --------------------------------------------------
# CHECK DEM
# --------------------------------------------------

if not DEM_FILE.exists():
    raise FileNotFoundError(
        f"\nDEM file not found:\n{DEM_FILE}\n"
    )

print("\nDEM found:")
print(DEM_FILE)


# --------------------------------------------------
# STUDY AREA
# --------------------------------------------------

study_area = box(
    MIN_LON,
    MIN_LAT,
    MAX_LON,
    MAX_LAT
)

geometry = [mapping(study_area)]


# --------------------------------------------------
# OPEN AND CLIP DEM
# --------------------------------------------------

with rasterio.open(DEM_FILE) as src:

    print("\nInput DEM information:")
    print(f"CRS       : {src.crs}")
    print(f"Width     : {src.width}")
    print(f"Height    : {src.height}")
    print(f"Resolution: {src.res}")
    print(f"Bounds    : {src.bounds}")
    print(f"NoData    : {src.nodata}")

    clipped_dem, clipped_transform = mask(
        src,
        geometry,
        crop=True
    )

    clipped_dem = clipped_dem.astype(
        np.float32
    )

    profile = src.profile.copy()

    profile.update(
        {
            "height": clipped_dem.shape[1],
            "width": clipped_dem.shape[2],
            "transform": clipped_transform,
            "dtype": "float32",
            "compress": "deflate"
        }
    )


# --------------------------------------------------
# EXTRACT ELEVATION
# --------------------------------------------------

elevation = clipped_dem[0]

valid_mask = np.isfinite(elevation)

valid = elevation[valid_mask]


if valid.size == 0:
    raise ValueError(
        "No valid elevation pixels were found "
        "inside the study area."
    )


# --------------------------------------------------
# SAVE CLIPPED DEM
# --------------------------------------------------

with rasterio.open(
    OUTPUT_FILE,
    "w",
    **profile
) as dst:

    dst.write(clipped_dem)


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

print("\n==========================================")
print("DEM CLIPPING COMPLETED")
print("==========================================")

print(f"Output file : {OUTPUT_FILE}")

print(
    f"Pixels      : "
    f"{elevation.size}"
)

print(
    f"Valid pixels: "
    f"{valid.size}"
)

print(
    f"Minimum elevation : "
    f"{np.min(valid):.2f} m"
)

print(
    f"Maximum elevation : "
    f"{np.max(valid):.2f} m"
)

print(
    f"Mean elevation    : "
    f"{np.mean(valid):.2f} m"
)

print(
    f"Median elevation  : "
    f"{np.median(valid):.2f} m"
)


# --------------------------------------------------
# STUDY AREA INFORMATION
# --------------------------------------------------

print("\nStudy area:")

print(
    f"Latitude  : "
    f"{MIN_LAT} - {MAX_LAT}"
)

print(
    f"Longitude : "
    f"{MIN_LON} - {MAX_LON}"
)


print("\n==========================================")
print("READY FOR TERRAIN ANALYSIS")
print("==========================================")