# MineGuard AI — Data Team Handoff Notes

## 1. Overview

This handoff document provides clear guidelines for all sub-teams (`feature/gis-dem-drone`, `feature/simulation-iot-alerts`, `feature/frontend`) following **Phase 1 — Dataset Acquisition & Audit**.

It details exact feature expectations, naming conventions, missing real-world variables, and simulation requirements for Phase 2 pipeline development.

---

## 2. Handoff Notes for GIS / DEM / Drone Teammate (`feature/gis-dem-drone`)

### Required Features & Expected Formats
The ML pipeline requires topographical and location attributes extracted from DEM rasters or drone photogrammetry for each bench/zone (`zone_id`):

| Feature Name | Expected Data Type | Unit | Range / Format | Description |
| :--- | :--- | :--- | :--- | :--- |
| `latitude` | Float | Decimal Degrees (°) | -90.0 to 90.0 (WGS84) | Center coordinate of slope bench or sensor location |
| `longitude` | Float | Decimal Degrees (°) | -180.0 to 180.0 (WGS84) | Center coordinate of slope bench or sensor location |
| `elevation_m` | Float | Meters (m) | -500.0 to 9000.0 | Surface elevation extracted from DEM |
| `slope_deg` | Float | Degrees (°) | 0.0 to 90.0 | Slope inclination angle (critical gravitational factor) |
| `aspect_deg` | Float | Degrees (°) | 0.0 to 360.0 | Azimuth direction of max slope (0° = North) |
| `curvature` | Float | m⁻¹ | -1.0 to 1.0 | Profile/planform surface curvature index |

### Key GIS Guidelines
- **Zone Boundary Mapping**: Ensure spatial polygon mapping links coordinates (`latitude`, `longitude`) to standardized zone identifiers (`zone_id`, e.g., `ZONE-003`).
- **Feature Extraction**: DEM rasters (GeoTIFF) should be clipped per mine zone to compute mean `slope_deg` and `elevation_m`.

---

## 3. Handoff Notes for Simulation & IoT Teammate (`feature/simulation-iot-alerts`)

### Required Sensor Variables & Mappings
Real-time or simulated sensor streams must match the key names and units established in `API_CONTRACT.md` Section 5 and `docs/ML_DATA_DICTIONARY.md`:

| Contract Sensor Field | Data Type | Unit | Real Data Availability | Simulation Requirement |
| :--- | :--- | :--- | :--- | :--- |
| `displacement_mm` | Float | mm | Available in USGS telemetry | Simulate tertiary creep acceleration before slope failure |
| `strain` | Float | µε / ratio | Partial in USGS sensor releases | **Simulate strain gauge deformation under bench loading** |
| `pore_pressure_kpa` | Float | kPa | Available in USGS piezometer logs | Simulate pore pressure spikes following heavy rainfall |
| `rainfall_mm` | Float | mm | Available in NOAA / NASA datasets | Simulate localized downpours and continuous rain events |
| `temperature_c` | Float | °C | Available in NOAA datasets | Simulate diurnal thermal expansion/freeze-thaw cycles |
| `vibration_g` | Float | g (PPA) | Partial in USGS seismic releases | **Simulate peak particle acceleration from open-pit bench blasting** |

### Simulation Recommendations
- **Gaps in Real Datasets**: Real open-source datasets rarely capture open-pit mine bench blasting (`vibration_g`) combined with high-frequency micro-strain deformation (`strain`).
- **Synthetic Stream Generation**: The simulation module should generate synthetic sensor sequences for `vibration_g` (0.0 to 5.0 g) and `strain` (0.0 to 2.5 µε) during simulated blasting events to complement real USGS/NASA baseline telemetry.

---

## 4. Handoff Notes for Frontend Teammate (`feature/frontend`)

- **Status**: No immediate action required for Phase 1.
- **Contract Guarantee**: The input/output API contracts established in Phase 0 (`API_CONTRACT.md`, `docs/examples/ml_request_example.json`, `docs/examples/ml_response_example.json`) remain **100% unchanged**.
- **Output Expectations**: The ML model in Phase 2 will return `rockfall_probability` (float `0.0`–`1.0`), categorical `risk_level` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), and `contributing_factors` array for explainability charts as originally contracted.
