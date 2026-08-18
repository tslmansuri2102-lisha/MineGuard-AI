from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[2]

DEM_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "dem_features"
    / "kusunda_dem.tif"
)

SLOPE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "dem_features"
    / "slope.tif"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "map_layers"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def normalize(data):

    data = data.astype(
        np.float32
    )

    valid = np.isfinite(data)

    if not np.any(valid):
        raise ValueError(
            "Raster contains no valid pixels."
        )

    minimum = np.nanmin(
        data[valid]
    )

    maximum = np.nanmax(
        data[valid]
    )

    if maximum == minimum:

        return np.zeros(
            data.shape,
            dtype=np.uint8
        )

    normalized = (
        (data - minimum)
        / (maximum - minimum)
        * 255
    )

    normalized[
        ~valid
    ] = 0

    return normalized.astype(
        np.uint8
    )


def create_elevation_png():

    with rasterio.open(
        DEM_FILE
    ) as src:

        data = src.read(
            1
        ).astype(
            np.float32
        )

        if src.nodata is not None:

            data[
                data == src.nodata
            ] = np.nan

        image_data = normalize(
            data
        )

        image = Image.fromarray(
            image_data,
            mode="L"
        )

        output = (
            OUTPUT_DIR
            / "elevation.png"
        )

        image.save(
            output
        )

        print()
        print(
            f"Elevation PNG: {output}"
        )

        print(
            f"Elevation CRS: {src.crs}"
        )

        print(
            f"Elevation bounds: {src.bounds}"
        )


def create_slope_png():

    with rasterio.open(
        SLOPE_FILE
    ) as src:

        target_crs = "EPSG:4326"

        transform, width, height = (
            calculate_default_transform(
                src.crs,
                target_crs,
                src.width,
                src.height,
                *src.bounds
            )
        )

        destination = np.full(
            (height, width),
            np.nan,
            dtype=np.float32
        )

        reproject(
            source=rasterio.band(
                src,
                1
            ),
            destination=destination,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=target_crs,
            resampling=Resampling.bilinear
        )

        image_data = normalize(
            destination
        )

        image = Image.fromarray(
            image_data,
            mode="L"
        )

        output = (
            OUTPUT_DIR
            / "slope.png"
        )

        image.save(
            output
        )

        west = transform.c

        north = transform.f

        east = (
            west
            + width * transform.a
        )

        south = (
            north
            + height * transform.e
        )

        print()
        print(
            f"Slope PNG: {output}"
        )

        print(
            f"Slope CRS: {target_crs}"
        )

        print(
            "Slope bounds:"
        )

        print(
            f"West  : {west}"
        )

        print(
            f"South : {south}"
        )

        print(
            f"East  : {east}"
        )

        print(
            f"North : {north}"
        )


print(
    "=========================================="
)

print(
    "MineGuard AI - Web Raster Preparation"
)

print(
    "=========================================="
)


if not DEM_FILE.exists():

    raise FileNotFoundError(
        f"DEM not found:\n{DEM_FILE}"
    )


if not SLOPE_FILE.exists():

    raise FileNotFoundError(
        f"Slope raster not found:\n{SLOPE_FILE}"
    )


create_elevation_png()

create_slope_png()


print()
print(
    "=========================================="
)

print(
    "WEB RASTER PREPARATION COMPLETED"
)

print(
    "=========================================="
)

print(
    "Elevation and slope are now in"
)

print(
    "EPSG:4326 for Leaflet integration."
)

print(
    "=========================================="
)