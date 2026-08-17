from pathlib import Path

import numpy as np
import rasterio
import geopandas as gpd
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import generic_filter


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

SLOPE_FILE = OUTPUT_DIR / "slope.tif"
ASPECT_FILE = OUTPUT_DIR / "aspect.tif"
CURVATURE_FILE = OUTPUT_DIR / "curvature.tif"
ROUGHNESS_FILE = OUTPUT_DIR / "roughness.tif"


TARGET_CRS = "EPSG:32645"


print("==========================================")
print("MineGuard AI - Advanced Terrain Analysis")
print("==========================================")


# --------------------------------------------------
# CHECK DEM
# --------------------------------------------------

if not DEM_FILE.exists():

    raise FileNotFoundError(
        f"\nDEM not found:\n{DEM_FILE}\n"
        "Run process_dem.py first."
    )


# --------------------------------------------------
# READ DEM
# --------------------------------------------------

with rasterio.open(DEM_FILE) as src:

    print("\nOriginal DEM:")
    print(f"CRS        : {src.crs}")
    print(f"Shape      : {src.shape}")
    print(f"Resolution : {src.res}")

    source_data = src.read(1).astype(np.float32)

    source_transform = src.transform
    source_crs = src.crs
    source_profile = src.profile.copy()


# --------------------------------------------------
# REPROJECT DEM TO METRIC CRS
# --------------------------------------------------

print("\nReprojecting DEM to metric CRS...")
print(f"Target CRS : {TARGET_CRS}")


with rasterio.open(DEM_FILE) as src:

    transform, width, height = calculate_default_transform(
        src.crs,
        TARGET_CRS,
        src.width,
        src.height,
        *src.bounds
    )

    projected_dem = np.empty(
        (height, width),
        dtype=np.float32
    )

    reproject(
        source=rasterio.band(src, 1),
        destination=projected_dem,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=TARGET_CRS,
        resampling=Resampling.bilinear
    )


print(
    f"Projected resolution: "
    f"{transform.a:.2f} m x "
    f"{abs(transform.e):.2f} m"
)


# --------------------------------------------------
# VALID ELEVATION MASK
# --------------------------------------------------

valid_mask = np.isfinite(
    projected_dem
)

valid_values = projected_dem[
    valid_mask
]


if valid_values.size == 0:

    raise ValueError(
        "No valid elevation values found."
    )


print("\nElevation statistics:")
print(
    f"Minimum : "
    f"{np.min(valid_values):.2f} m"
)

print(
    f"Maximum : "
    f"{np.max(valid_values):.2f} m"
)

print(
    f"Mean    : "
    f"{np.mean(valid_values):.2f} m"
)


# --------------------------------------------------
# SMOOTH DEM SLIGHTLY
# --------------------------------------------------

# Small smoothing reduces isolated DEM noise
# before calculating derivatives.

from scipy.ndimage import gaussian_filter

smoothed_dem = gaussian_filter(
    projected_dem,
    sigma=0.8
)


# --------------------------------------------------
# PIXEL SIZE
# --------------------------------------------------

pixel_size_x = abs(
    transform.a
)

pixel_size_y = abs(
    transform.e
)


# --------------------------------------------------
# FIRST DERIVATIVES
# --------------------------------------------------

dy, dx = np.gradient(
    smoothed_dem,
    pixel_size_y,
    pixel_size_x
)


# --------------------------------------------------
# SLOPE
# --------------------------------------------------

slope_radians = np.arctan(
    np.sqrt(
        dx ** 2 +
        dy ** 2
    )
)

slope_degrees = np.degrees(
    slope_radians
)


# --------------------------------------------------
# ASPECT
# --------------------------------------------------

aspect_degrees = np.degrees(
    np.arctan2(
        -dx,
        dy
    )
)

aspect_degrees = (
    90.0 - aspect_degrees
) % 360.0


# --------------------------------------------------
# SECOND DERIVATIVES
# --------------------------------------------------

dyy, dyx = np.gradient(
    dy,
    pixel_size_y,
    pixel_size_x
)

dxy, dxx = np.gradient(
    dx,
    pixel_size_y,
    pixel_size_x
)


# --------------------------------------------------
# PROFILE CURVATURE
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
    denominator < 1e-12
] = np.nan


curvature = -(
    dxx +
    dyy
) / denominator


# --------------------------------------------------
# TRUE TERRAIN ROUGHNESS
# --------------------------------------------------

# Roughness is calculated as the local
# elevation range inside a 3x3 neighborhood.

def elevation_range(values):

    center = values[
        len(values) // 2
    ]

    valid = values[
        np.isfinite(values)
    ]

    if len(valid) == 0:

        return np.nan

    return (
        np.max(valid)
        -
        np.min(valid)
    )


roughness = generic_filter(
    smoothed_dem,
    elevation_range,
    size=3,
    mode="nearest"
)


# --------------------------------------------------
# CLEAN INVALID VALUES
# --------------------------------------------------

slope_degrees = np.where(
    np.isfinite(slope_degrees),
    slope_degrees,
    np.nan
)

aspect_degrees = np.where(
    np.isfinite(aspect_degrees),
    aspect_degrees,
    np.nan
)

curvature = np.where(
    np.isfinite(curvature),
    curvature,
    np.nan
)

roughness = np.where(
    np.isfinite(roughness),
    roughness,
    np.nan
)


# --------------------------------------------------
# OUTPUT PROFILE
# --------------------------------------------------

output_profile = source_profile.copy()

output_profile.update(
    {
        "driver": "GTiff",
        "height": projected_dem.shape[0],
        "width": projected_dem.shape[1],
        "transform": transform,
        "crs": TARGET_CRS,
        "dtype": "float32",
        "count": 1,
        "compress": "deflate",
        "nodata": -9999.0
    }
)


# --------------------------------------------------
# SAVE SLOPE
# --------------------------------------------------

slope_output = np.where(
    np.isfinite(slope_degrees),
    slope_degrees,
    -9999.0
)

with rasterio.open(
    SLOPE_FILE,
    "w",
    **output_profile
) as dst:

    dst.write(
        slope_output.astype(np.float32),
        1
    )


# --------------------------------------------------
# SAVE ASPECT
# --------------------------------------------------

aspect_output = np.where(
    np.isfinite(aspect_degrees),
    aspect_degrees,
    -9999.0
)

with rasterio.open(
    ASPECT_FILE,
    "w",
    **output_profile
) as dst:

    dst.write(
        aspect_output.astype(np.float32),
        1
    )


# --------------------------------------------------
# SAVE CURVATURE
# --------------------------------------------------

curvature_output = np.where(
    np.isfinite(curvature),
    curvature,
    -9999.0
)

with rasterio.open(
    CURVATURE_FILE,
    "w",
    **output_profile
) as dst:

    dst.write(
        curvature_output.astype(np.float32),
        1
    )


# --------------------------------------------------
# SAVE ROUGHNESS
# --------------------------------------------------

roughness_output = np.where(
    np.isfinite(roughness),
    roughness,
    -9999.0
)

with rasterio.open(
    ROUGHNESS_FILE,
    "w",
    **output_profile
) as dst:

    dst.write(
        roughness_output.astype(np.float32),
        1
    )


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

print("\n==========================================")
print("ADVANCED TERRAIN ANALYSIS COMPLETED")
print("==========================================")


valid_slope = slope_degrees[
    np.isfinite(slope_degrees)
]

valid_aspect = aspect_degrees[
    np.isfinite(aspect_degrees)
]

valid_curvature = curvature[
    np.isfinite(curvature)
]

valid_roughness = roughness[
    np.isfinite(roughness)
]


print("\nSLOPE")

print(
    f"Minimum : "
    f"{np.min(valid_slope):.2f}°"
)

print(
    f"Maximum : "
    f"{np.max(valid_slope):.2f}°"
)

print(
    f"Mean    : "
    f"{np.mean(valid_slope):.2f}°"
)


print("\nASPECT")

print(
    f"Minimum : "
    f"{np.min(valid_aspect):.2f}°"
)

print(
    f"Maximum : "
    f"{np.max(valid_aspect):.2f}°"
)


print("\nCURVATURE")

print(
    f"Minimum : "
    f"{np.min(valid_curvature):.6f}"
)

print(
    f"Maximum : "
    f"{np.max(valid_curvature):.6f}"
)

print(
    f"Mean    : "
    f"{np.mean(valid_curvature):.6f}"
)


print("\nTERRAIN ROUGHNESS")

print(
    f"Minimum : "
    f"{np.min(valid_roughness):.3f} m"
)

print(
    f"Maximum : "
    f"{np.max(valid_roughness):.3f} m"
)

print(
    f"Mean    : "
    f"{np.mean(valid_roughness):.3f} m"
)


print("\nOutput files:")

print(
    f"Slope     : {SLOPE_FILE}"
)

print(
    f"Aspect    : {ASPECT_FILE}"
)

print(
    f"Curvature : {CURVATURE_FILE}"
)

print(
    f"Roughness : {ROUGHNESS_FILE}"
)


print("\n==========================================")
print("READY FOR ZONE FEATURE REGENERATION")
print("==========================================")