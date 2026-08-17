from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter


BASE_DIR = Path(__file__).resolve().parents[2]

DEM_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "dem_features"
    / "kusunda_dem.tif"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "dem_features"
)

CURVATURE_FILE = OUTPUT_DIR / "curvature.tif"
ROUGHNESS_FILE = OUTPUT_DIR / "roughness.tif"


print("==========================================")
print("MineGuard AI - Curvature & Roughness")
print("==========================================")


if not DEM_FILE.exists():
    raise FileNotFoundError(
        f"DEM not found:\n{DEM_FILE}\n"
        "Run process_dem.py first."
    )


with rasterio.open(DEM_FILE) as src:

    elevation = src.read(1).astype(np.float64)

    profile = src.profile.copy()

    transform = src.transform

    print("\nDEM loaded successfully.")
    print(f"Shape     : {elevation.shape}")
    print(f"Resolution: {src.res}")
    print(f"CRS       : {src.crs}")


# --------------------------------------------------
# APPROXIMATE PIXEL SIZE IN METERS
# --------------------------------------------------

mean_latitude = 23.782

meters_per_degree_lat = 111320.0

meters_per_degree_lon = (
    111320.0 *
    np.cos(np.radians(mean_latitude))
)

pixel_width_m = (
    abs(transform.a) *
    meters_per_degree_lon
)

pixel_height_m = (
    abs(transform.e) *
    meters_per_degree_lat
)


# --------------------------------------------------
# SMOOTH ELEVATION
# --------------------------------------------------

smoothed = gaussian_filter(
    elevation,
    sigma=1
)


# --------------------------------------------------
# FIRST DERIVATIVES
# --------------------------------------------------

dy, dx = np.gradient(
    smoothed,
    pixel_height_m,
    pixel_width_m
)


# --------------------------------------------------
# SECOND DERIVATIVES
# --------------------------------------------------

dyy, dyx = np.gradient(
    dy,
    pixel_height_m,
    pixel_width_m
)

dxy, dxx = np.gradient(
    dx,
    pixel_height_m,
    pixel_width_m
)


# --------------------------------------------------
# PROFILE-LIKE CURVATURE
# --------------------------------------------------

gradient_squared = (
    dx ** 2 +
    dy ** 2
)

denominator = np.power(
    1 + gradient_squared,
    1.5
)

denominator[
    denominator == 0
] = np.nan


curvature = -(
    dxx +
    dyy
) / denominator


# --------------------------------------------------
# TERRAIN ROUGHNESS
# --------------------------------------------------

roughness = np.sqrt(
    dx ** 2 +
    dy ** 2
)


# --------------------------------------------------
# REMOVE EXTREME INVALID VALUES
# --------------------------------------------------

curvature = np.nan_to_num(
    curvature,
    nan=0.0,
    posinf=0.0,
    neginf=0.0
)

roughness = np.nan_to_num(
    roughness,
    nan=0.0,
    posinf=0.0,
    neginf=0.0
)


# --------------------------------------------------
# OUTPUT PROFILE
# --------------------------------------------------

profile.update(
    {
        "dtype": "float32",
        "count": 1,
        "compress": "deflate"
    }
)


# --------------------------------------------------
# SAVE CURVATURE
# --------------------------------------------------

with rasterio.open(
    CURVATURE_FILE,
    "w",
    **profile
) as dst:

    dst.write(
        curvature.astype(np.float32),
        1
    )


# --------------------------------------------------
# SAVE ROUGHNESS
# --------------------------------------------------

with rasterio.open(
    ROUGHNESS_FILE,
    "w",
    **profile
) as dst:

    dst.write(
        roughness.astype(np.float32),
        1
    )


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

print("\n==========================================")
print("TERRAIN FEATURES COMPLETED")
print("==========================================")


print("\nCURVATURE")

print(
    f"Minimum : "
    f"{np.min(curvature):.6f}"
)

print(
    f"Maximum : "
    f"{np.max(curvature):.6f}"
)

print(
    f"Mean    : "
    f"{np.mean(curvature):.6f}"
)


print("\nTERRAIN ROUGHNESS")

print(
    f"Minimum : "
    f"{np.min(roughness):.4f}"
)

print(
    f"Maximum : "
    f"{np.max(roughness):.4f}"
)

print(
    f"Mean    : "
    f"{np.mean(roughness):.4f}"
)


print("\nOutput files:")

print(
    f"Curvature : "
    f"{CURVATURE_FILE}"
)

print(
    f"Roughness : "
    f"{ROUGHNESS_FILE}"
)


print("\n==========================================")
print("READY FOR ZONE FEATURE EXTRACTION")
print("==========================================")