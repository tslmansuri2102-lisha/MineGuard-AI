# MineGuard AI — Data Feature Matrix

## 1. Overview

This matrix maps every core ML feature defined in `API_CONTRACT.md` and `docs/ML_DATA_DICTIONARY.md` to candidate public datasets, indicating feature availability, data classification (`Real`, `Derived`, or `Synthetic Simulation`), official source, and technical notes.

---

## 2. Core Feature Availability Matrix

| Feature Name | Primary / Supporting Dataset | Available? | Data Type | Source | Notes & Derivation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`displacement`** (`displacement_mm`) | USGS Landslide Monitoring Telemetry / WSN Sensor Data | **Yes** | Real | USGS / In-situ Extensometers | Measured in mm via extensometers/inclinometers. Available in real USGS telemetry; absent in purely event-based catalogs. |
| **`velocity`** (`displacement_velocity`) | ML Feature Engineering Pipeline | **Yes** | Derived | Derived from `displacement_mm` | Derived programmatically as the first time derivative of displacement over time (\(\frac{dD}{dt}\) in mm/h). |
| **`acceleration`** (`displacement_acceleration`) | ML Feature Engineering Pipeline | **Yes** | Derived | Derived from `displacement_velocity` | Derived programmatically as the second time derivative of displacement over time (\(\frac{d^2D}{dt^2}\) in mm/h²). Key tertiary creep failure indicator. |
| **`strain`** (`strain`) | USGS Sensor Data / Physics Simulator | **Yes** | Real / Synthetic | USGS / Geotechnical Strain Gauges | Measured in strain ratio or microstrain (µε). Available in USGS geotechnical releases; supplemented by physics-based simulation. |
| **`pore_pressure`** (`pore_pressure_kpa`) | USGS Landslide Monitoring Telemetry | **Yes** | Real | USGS Piezometer Network | Subsurface pore water pressure measured in kPa. Directly available in USGS slope monitoring datasets. |
| **`rainfall`** (`rainfall_mm`) | NASA Global Landslide Catalog / NOAA GHCN / USGS | **Yes** | Real | NASA / NOAA / USGS Rain Gauges | Cumulative and hourly rainfall in mm. Extracted from NASA triggers (`downpour`, `continuous_rain`, `rain`) and NOAA/USGS rain gauges. |
| **`temperature`** (`temperature_c`) | NOAA GHCN / USGS Landslide Telemetry | **Yes** | Real | NOAA / Weather Stations | Ambient temperature in °C. Available in NOAA meteorological data and USGS site stations. |
| **`vibration`** (`vibration_g`) | USGS Seismic Monitoring / Physics Simulator | **Yes** | Real / Synthetic | USGS Geophones / Mine Blast Log | Peak particle acceleration in g. Available in USGS seismic sensor logs; open-pit mine blasting vibration supplemented via simulation. |
| **`slope`** (`slope_deg`) | Copernicus DEM / USGS 3DEP | **Yes** | Real / Derived | Copernicus DEM / OpenTopography | Slope angle in degrees (°). Calculated from surface elevation gradients via DEM spatial analysis. |
| **`terrain_features`** (`elevation_m`, `aspect`, `curvature`) | Copernicus DEM / USGS 3DEP | **Yes** | Real / Derived | Copernicus DEM / OpenTopography | Topographical surface attributes. Extracted directly from DEM rasters (`elevation_m`, `aspect_deg`, `curvature`). |
| **`latitude`** (`latitude`) | NASA Global Landslide Catalog (GLC) | **Yes** | Real | NASA EarthData / GPS | WGS84 decimal latitude coordinate. 100% complete across all 11,033 records in `nasa_global_landslide_catalog.csv`. |
| **`longitude`** (`longitude`) | NASA Global Landslide Catalog (GLC) | **Yes** | Real | NASA EarthData / GPS | WGS84 decimal longitude coordinate. 100% complete across all 11,033 records in `nasa_global_landslide_catalog.csv`. |
| **`rockfall_event`** (`rockfall_event` / label) | NASA Global Landslide Catalog (GLC) | **Yes** | Real | NASA EarthData / Ground Truth | Binary/Categorical failure target label. NASA catalog provides 671 verified `rock_fall` events and 7,648 `landslide` events. |

---

## 3. Summary of Data Coverage & Gap Analysis

- **Real Data Coverage (100% Verified)**:
  - Ground-truth failure labels (`rockfall_event`)
  - Coordinates (`latitude`, `longitude`)
  - Rainfall metrics & triggers (`rainfall_mm`)
  - Subsurface hydrostatic pressure (`pore_pressure_kpa`)
  - Surface displacement telemetry (`displacement_mm`)
  - Ambient temperature (`temperature_c`)
  - Morphological slope angle (`slope_deg`) & terrain elevation (`elevation_m`)

- **Programmatically Derived Features**:
  - Displacement velocity (\(\frac{dD}{dt}\))
  - Displacement acceleration (\(\frac{d^2D}{dt^2}\))
  - Rolling 3h / 24h cumulative rainfall sums
  - Slope aspect and profile curvature

- **Features Requiring Physics-Based Simulation Coupling**:
  - High-frequency mine blasting ground vibration (`vibration_g`) under specific bench geometries
  - Micro-bench strain gauge deformation (`strain`) for synthetic testing prior to physical hardware deployment
