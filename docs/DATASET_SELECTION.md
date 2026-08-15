# MineGuard AI — Dataset Selection Strategy

## 1. Executive Summary

This document outlines the multi-source dataset selection strategy for **MineGuard AI Phase 1**.

Rather than relying on a single incomplete dataset, we adopt a defensible, multi-source data fusion strategy combining:
1. **Primary Ground-Truth Event Dataset**: NASA Global Landslide Catalog (GLC)
2. **Primary Geomechanical Telemetry Dataset**: USGS Landslide Monitoring Telemetry
3. **Supporting GIS & Terrain Dataset**: Copernicus DEM / USGS 3DEP
4. **Supporting Meteorological Dataset**: NOAA GHCN Weather Data

---

## 2. Selected Primary Datasets

### A. NASA Global Landslide Catalog (GLC) / COOLR
- **Selection Rationale**:
  - Authoritative global dataset published by NASA Goddard Space Flight Center.
  - Contains 11,033 verified real-world slope failure events with 100% complete latitude/longitude coordinates and event timestamps.
  - Includes explicit category labels, featuring **671 verified rockfall events (`rock_fall`)** and **7,648 landslide events (`landslide`)**, providing authentic ground-truth targets for model training.
  - Contains trigger categorizations (`downpour`, `continuous_rain`, `mining` open-pit activity), linking precipitation drivers directly to failure occurrences.
- **Features Contributed**:
  - Target labels (`rockfall_event`, `landslide_category`)
  - Trigger metadata (`landslide_trigger`)
  - Event timestamps (`event_date`)
  - Spatial coordinates (`latitude`, `longitude`)
  - Event scale & setting (`landslide_size`, `landslide_setting`)

### B. USGS Landslide Monitoring Telemetry Datasets
- **Selection Rationale**:
  - Published by the United States Geological Survey (USGS) Landslide Hazards Program.
  - Provides continuous high-frequency temporal streams of in-situ geotechnical sensors installed on unstable slopes.
  - Supplies physical distributions for subsurface pore water pressure and displacement movement necessary for time-series modeling.
- **Features Contributed**:
  - `displacement_mm` (extensometer movement)
  - `pore_pressure_kpa` (piezometer hydrostatic pressure)
  - `rainfall_mm` (high-resolution rain gauge data)
  - `temperature_c` (ambient thermistor data)

---

## 3. Selected Supporting Datasets

### A. Copernicus DEM / USGS 3DEP Elevation Data
- **Selection Rationale**:
  - Provides standardized global Digital Elevation Models at 30m / 10m resolutions.
  - Enables extraction of topographical slope geometry without manual surveying.
- **Features Contributed**:
  - `elevation_m`
  - `slope_deg`
  - `aspect_deg`
  - `curvature`

### B. NOAA GHCN Climate Data
- **Selection Rationale**:
  - Comprehensive long-term meteorological records.
  - Complements event catalogs with continuous precipitation and temperature baseline sequences.
- **Features Contributed**:
  - `rainfall_mm` (continuous precipitation streams)
  - `temperature_c` (thermal weathering cycles)

---

## 4. Feature Source Mapping & Gap Analysis

| Feature Category | Core Field Name | Primary / Supporting Dataset Source | Status |
| :--- | :--- | :--- | :--- |
| **Ground Truth Label** | `rockfall_event` | NASA Global Landslide Catalog (`rock_fall` / `landslide`) | **Available (Real)** |
| **Spatial Coordinates** | `latitude`, `longitude` | NASA Global Landslide Catalog | **Available (Real)** |
| **Event Timestamp** | `timestamp` | NASA GLC / USGS Telemetry | **Available (Real)** |
| **Rainfall Driver** | `rainfall_mm` | NASA Triggers / NOAA GHCN / USGS | **Available (Real)** |
| **Subsurface Hydrostatics** | `pore_pressure_kpa` | USGS Landslide Piezometer Data | **Available (Real)** |
| **Geomechanical Movement**| `displacement_mm` | USGS Extensometer Telemetry | **Available (Real)** |
| **Ambient Temperature** | `temperature_c` | NOAA GHCN / USGS Station Data | **Available (Real)** |
| **Slope Geometry** | `slope_deg`, `elevation_m` | Copernicus DEM / USGS 3DEP | **Available (Real/Derived)** |
| **Movement Velocity** | `displacement_velocity` | ML Feature Engineering Pipeline | **To Be Derived (\(\frac{dD}{dt}\))** |
| **Movement Acceleration** | `displacement_acceleration` | ML Feature Engineering Pipeline | **To Be Derived (\(\frac{d^2D}{dt^2}\))** |
| **Cumulative Rain Sums** | `rainfall_3h_sum`, `24h_sum` | ML Feature Engineering Pipeline | **To Be Derived (Rolling Sum)** |
| **Bench Strain** | `strain` | Physics Simulator / USGS Sensor Releases | **Synthetic / Real** |
| **Mine Blast Vibration** | `vibration_g` | Physics Simulator / USGS Geophones | **Synthetic / Real** |

---

## 5. Strategy for Derived & Synthetic Features

1. **Programmatically Derived Features**:
   - Time derivatives of displacement (\(v = \frac{\Delta D}{\Delta t}\) and \(a = \frac{\Delta v}{\Delta t}\)) will be generated in Phase 2 during feature engineering.
   - Rolling cumulative rainfall (\(3\text{h}\), \(24\text{h}\), \(72\text{h}\)) will be computed from precipitative time-series.

2. **Synthetic Telemetry Integration Strategy**:
   - Real datasets provide authentic distributions for rainfall, slope angle, displacement, and pore pressure.
   - For open-pit mining specific edge cases (such as extreme blast vibrations `vibration_g` and strain gauge micro-deformations `strain`), the simulation module (`feature/simulation-iot-alerts`) will generate physics-constrained synthetic streams adhering to `docs/ML_DATA_DICTIONARY.md`.
