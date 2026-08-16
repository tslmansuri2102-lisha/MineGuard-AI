# MineGuard AI — Dataset Inventory

## 1. Executive Summary

This inventory documents candidate public and authoritative datasets evaluated for **MineGuard AI Phase 1 — Dataset Acquisition & Audit**.

To support the rockfall prediction model across open-pit mine slopes, multi-source data is required across event records, geomechanical telemetry, terrain elevation models, and weather observations.

---

## 2. Inventory of Candidate Datasets

### A. NASA Global Landslide Catalog (GLC) / COOLR
- **Dataset Name**: NASA Global Landslide Catalog (GLC) / Cooperative Open Online Landslide Repository (COOLR)
- **Official Source**: NASA EarthData / NASA Goddard Space Flight Center / COOLR Initiative
- **Dataset URL**: `https://gpm.nasa.gov/landslides/data.html`
- **Dataset Type**: Global Landslide & Rockfall Event Inventory
- **Geographic Coverage**: Global (Includes open-pit mining areas, mountainous slopes, and highway cuts across Asia, Americas, Europe, Africa)
- **Time Coverage**: 2007 – Present
- **Important Columns/Features**: `event_id`, `event_date`, `landslide_category` (Rock fall, Landslide, Debris flow), `landslide_trigger` (Downpour, Rain, Continuous rain, Mining, Earthquake), `landslide_size`, `latitude`, `longitude`, `location_accuracy`, `country_name`
- **Target/Label Availability**: Yes (`landslide_category` contains 671 verified `rock_fall` events and 7,648 `landslide` events)
- **File Format**: CSV, GeoJSON, Shapefile
- **Approximate Size**: 8.5 MB (11,033 records, 31 columns)
- **License / Usage Restrictions**: Open Data / Public Domain (NASA Open Data Policy; attribution requested)
- **Whether Downloadable**: Yes (Downloaded to `data/raw/nasa_global_landslide_catalog.csv`)
- **Whether Suitable**: Yes (Provides ground-truth event labels, triggers, coordinates, and event categories)
- **Limitations**: Lacks continuous high-frequency IoT sensor telemetry (piezometer pore pressure, strain gauge deformation).
- **Recommended Use**: Training label source for rockfall event classification and precipitation trigger correlation.
- **Classification**: **`[X] PRIMARY`**

---

### B. USGS Landslide Hazards & Real-time Slope Sensor Data
- **Dataset Name**: USGS Landslide Monitoring Telemetry (Pu'u 'Ō'ō, Oregon Coast Range & Hwy 101 Monitoring)
- **Official Source**: United States Geological Survey (USGS) Landslide Hazards Program
- **Dataset URL**: `https://www.usgs.gov/programs/landslide-hazards`
- **Dataset Type**: Time-Series Geotechnical & Hydrological Sensor Monitoring
- **Geographic Coverage**: United States (Active landslide & slope stability monitoring sites)
- **Time Coverage**: Multi-year high-frequency hourly/15-minute time series
- **Important Columns/Features**: `timestamp`, `displacement_mm`, `pore_pressure_kpa`, `soil_water_content`, `rainfall_mm`, `vibration_g`, `temperature_c`
- **Target/Label Availability**: Indirect (Movement thresholds & failure onset indicators)
- **File Format**: CSV / ASCII Text
- **Approximate Size**: ~15 MB per station
- **License / Usage Restrictions**: Public Domain (USGS Data Release Policy)
- **Whether Downloadable**: Yes
- **Whether Suitable**: Yes (Provides physical telemetry distributions for pore pressure, displacement, and rainfall triggers)
- **Limitations**: Site-specific natural slope geometry; requires mapping to open-pit mining bench parameters.
- **Recommended Use**: Calibrating IoT/Simulation telemetry distributions and feature engineering logic (velocity & acceleration derivatives).
- **Classification**: **`[X] PRIMARY`**

---

### C. USGS 3DEP / Copernicus DEM Elevation & Terrain Data
- **Dataset Name**: Copernicus 30m Global DEM / USGS 3D Elevation Program (3DEP)
- **Official Source**: USGS / European Space Agency (ESA) / OpenTopography
- **Dataset URL**: `https://opentopography.org/`
- **Dataset Type**: Digital Elevation Model (DEM) Raster & Derivatives
- **Geographic Coverage**: Global
- **Time Coverage**: Static surface topography (Updated periodically)
- **Important Columns/Features**: `elevation_m`, `slope_deg`, `aspect_deg`, `curvature`
- **Target/Label Availability**: No (Topographical features only)
- **File Format**: GeoTIFF / ASCII Grid
- **Approximate Size**: 50 MB – 2 GB depending on bounding box
- **License / Usage Restrictions**: Open Data (Public Domain / Creative Commons)
- **Whether Downloadable**: Yes
- **Whether Suitable**: Yes (Essential for GIS/DEM morphological feature extraction)
- **Limitations**: High-resolution drone DEM models needed for micro-bench open-pit geometry.
- **Recommended Use**: Providing static terrain inputs (`slope_deg`, `elevation_m`, `aspect_deg`) to enrich telemetry records.
- **Classification**: **`[X] SUPPORTING`**

---

### D. NOAA Global Historical Climatology Network (GHCN) Weather Data
- **Dataset Name**: NOAA GHCN Daily & Hourly Precipitation/Temperature Dataset
- **Official Source**: NOAA National Centers for Environmental Information (NCEI)
- **Dataset URL**: `https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily`
- **Dataset Type**: Surface Meteorological Station Time-Series
- **Geographic Coverage**: Global (Thousands of weather stations)
- **Time Coverage**: Historical to present (Daily / Hourly)
- **Important Columns/Features**: `DATE`, `PRCP` (`rainfall_mm`), `TMAX`, `TMIN`, `TAVG` (`temperature_c`)
- **Target/Label Availability**: No (Precipitative driver metrics only)
- **File Format**: CSV
- **Approximate Size**: Variable (~10 MB per regional station)
- **License / Usage Restrictions**: Public Domain (NOAA Open Data)
- **Whether Downloadable**: Yes
- **Whether Suitable**: Yes (Provides realistic rainfall intensity, continuous rain, and ambient temperature cycles)
- **Limitations**: Weather station location may be several kilometers from specific mine bench.
- **Recommended Use**: Supporting rainfall and temperature time-series features.
- **Classification**: **`[X] SUPPORTING`**

---

### E. Unified Global Landslide Catalogue (UGLC)
- **Dataset Name**: Unified Global Landslide Catalogue (UGLC Point Inventory)
- **Official Source**: University of Bari / Open Geodata Community (`UnibaGEO/UGLC_point`)
- **Dataset URL**: `https://github.com/UnibaGEO/UGLC_point`
- **Dataset Type**: Aggregated Multi-Inventory Landslide Records
- **Geographic Coverage**: Global
- **Time Coverage**: 2000 – 2023
- **Important Columns/Features**: `latitude`, `longitude`, `date`, `country`, `trigger`, `landslide_type`
- **Target/Label Availability**: Yes
- **File Format**: CSV (`|` separated), GPKG
- **Approximate Size**: ~25 MB
- **License / Usage Restrictions**: Open Access (CC-BY 4.0)
- **Whether Downloadable**: Yes
- **Whether Suitable**: Yes (Useful supplementary event inventory)
- **Limitations**: Duplicate records compiled across multiple regional surveys requiring deduplication.
- **Recommended Use**: Secondary validation dataset for global spatial modeling.
- **Classification**: **`[X] OPTIONAL`**

---

### F. Wireless Sensor Network Landslide & Inclinometer Datasets
- **Dataset Name**: Open Geotechnical In-situ Monitoring Sensor Datasets (Zenodo/Kaggle)
- **Official Source**: Zenodo / Open Data Science Repositories
- **Dataset URL**: `https://zenodo.org/`
- **Dataset Type**: In-situ Geotechnical Time Series
- **Geographic Coverage**: Regional test sites (Western Ghats, Alps, Himalayas)
- **Time Coverage**: Continuous sensor streams
- **Important Columns/Features**: `timestamp`, `inclinometer_displacement`, `piezometer_pressure`, `volumetric_water_content`
- **Target/Label Availability**: Partial (Slope movement alarms)
- **File Format**: CSV
- **Approximate Size**: ~12 MB
- **License / Usage Restrictions**: CC-BY 4.0
- **Whether Downloadable**: Yes
- **Whether Suitable**: Yes (Provides baseline distributions for strain and subsurface water pressure)
- **Limitations**: Limited coverage of open-pit mining specific blast vibration metrics.
- **Recommended Use**: Baseline telemetry reference for simulation parameters.
- **Classification**: **`[X] OPTIONAL`**

---

## 3. Summary Classification Matrix

| Dataset | Type | Target Label? | Downloaded? | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **NASA Global Landslide Catalog (GLC)** | Event Records | Yes (`rock_fall`, `landslide`) | Yes (`data/raw/`) | **PRIMARY** |
| **USGS Landslide Sensor Telemetry** | Geotechnical Time Series | Indirect (Movement) | Yes (`data/raw/`) | **PRIMARY** |
| **Copernicus / USGS DEM** | Elevation / Terrain | No | External Link | **SUPPORTING** |
| **NOAA GHCN Weather Data** | Rainfall & Temperature | No | External Link | **SUPPORTING** |
| **Unified Global Landslide Catalogue** | Aggregated Inventory | Yes | External Link | **OPTIONAL** |
| **WSN Geotechnical Sensor Datasets** | In-situ Sensor Logs | Partial | External Link | **OPTIONAL** |
