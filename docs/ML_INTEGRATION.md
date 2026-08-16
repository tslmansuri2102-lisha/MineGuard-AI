# MineGuard AI — ML Integration Guide

## 1. Overview & System Architecture

This guide outlines how the various modules developed by different team members across branches integrate into a cohesive end-to-end rockfall prediction and early-warning system.

The integration architecture follows a standardized data flow pipeline based on `API_CONTRACT.md`:

```
+------------------+
| IoT / Simulation |
+------------------+
         | (sensor features)
         v
+--------------------+
| Data Preprocessing |
+--------------------+
         |
         +-----------------------+
         |                       |
         v                       v
+------------------+   +-------------------+
|  GIS / DEM Data  |   | Feature Engineering|
+------------------+   +-------------------+
         |                       |
         +----------+------------+
                    | (unified feature vector)
                    v
            +---------------+
            |   ML Model    |
            +---------------+
                    | (rockfall probability & risk level)
                    v
            +---------------+
            |  Backend API  |
            +---------------+
                    |
         +----------+----------+
         |                     |
         v                     v
+------------------+   +---------------+
| Frontend Dashboard|  | Alert System  |
+------------------+   +---------------+
```

---

## 2. Team Module Responsibilities

Each feature branch is responsible for specific domain features, metrics, and components:

### A. GIS / DEM / Drone Team (`feature/gis-dem-drone`)
- **Provides**:
  - Spatial coordinates (`latitude`, `longitude` in WGS84 decimal degrees).
  - Terrain morphology (`elevation_m`, `slope_deg`, `aspect_deg`, `curvature`).
  - Drone photogrammetry maps and high-resolution DEM bench models.
  - Spatial mapping of sensors to specific mine zones (`zone_id`).

### B. Simulation / IoT / Alerts Team (`feature/simulation-iot-alerts`)
- **Provides**:
  - Telemetry sensor readings (`displacement_mm`, `strain`, `pore_pressure_kpa`, `rainfall_mm`, `temperature_c`, `vibration_g`).
  - Physics-based synthetic dataset generation during initial testing.
  - Real-time ESP32 / IoT device data streaming.
  - Alert trigger execution based on downstream risk levels (`CRITICAL`, `HIGH`).

### C. ML / AI / Data Team (`feature/ml-ai-data`)
- **Provides**:
  - Raw telemetry data validation and missing-value imputation.
  - Feature engineering (calculating velocity `displacement_velocity`, acceleration `displacement_acceleration`, rolling rainfall sums).
  - Merging IoT sensor streams with GIS/DEM spatial features.
  - Model training, validation, evaluation, and artifact versioning (`model_version`).
  - Model inference producing `rockfall_probability` (0.0 – 1.0) and `risk_level` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
  - Explainability module generating SHAP / feature importances (`contributing_factors`).

### D. Backend / API Layer
- **Provides**:
  - Ingestion endpoint: `POST /api/v1/sensors/readings` per `API_CONTRACT.md`.
  - Routing sensor readings and GIS features to the ML inference service.
  - Response formatting and returning prediction outputs.
  - Storage and historical persistence of readings and predictions (`PRED-XXXXXX`).

### E. Frontend / Dashboard Team (`feature/frontend`)
- **Provides**:
  - Visualizing mine zones (`ZONE-003`) on interactive maps.
  - Displaying real-time risk gauges (`rockfall_probability`, e.g., `84%`).
  - Color-coded risk status badges (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
  - Rendering AI explainability charts for `contributing_factors`.
  - Triggering UI alerts when `risk_level` escalates to `HIGH` or `CRITICAL`.

---

## 3. End-to-End Data Pipeline Flow

1. **Ingestion & Data Collection**:
   IoT sensors or simulators send POST payloads to `/api/v1/sensors/readings` containing `mine_id`, `zone_id`, `timestamp`, and `sensors` dictionary.

2. **GIS Feature Enrichment**:
   The backend retrieves terrain attributes (`slope_deg`, `elevation_m`, `aspect_deg`) for `zone_id` from the GIS/DEM module.

3. **Feature Preprocessing & Engineering**:
   The ML data pipeline normalizes input values and computes temporal derivatives (e.g., velocity \(\frac{dD}{dt}\) and acceleration \(\frac{d^2D}{dt^2}\) of displacement).

4. **ML Inference & Explainability**:
   The preprocessed feature vector is evaluated by the trained ML model. The engine outputs `rockfall_probability`, determines `risk_level`, and generates `contributing_factors` via SHAP explanation metrics.

5. **API Response & Visualization**:
   The prediction response (`PRED-XXXXXX`) is returned via JSON to the backend and broadcasted to the frontend dashboard. If `risk_level` is `HIGH` or `CRITICAL`, an alert notification event (`ALERT-XXXXXX`) is published to the alerts system.

---

## 4. Contract Standards & Rules

- **Timestamp Standard**: All timestamps must strictly use **UTC ISO 8601** format (e.g., `2026-08-14T10:30:00Z`).
- **Identifier Formats**:
  - Mine: `MINE-001`
  - Zone: `ZONE-001`
  - Sensor: `SENSOR-001`
  - Reading: `READ-000001`
  - Prediction: `PRED-000001`
  - Alert: `ALERT-000001`
- **Probability Representation**: Floating-point values strictly between `0.0` and `1.0` (e.g., `0.84` represents 84%).
- **Risk Level Enums**: Must strictly match one of: `LOW`, `MODERATE`, `HIGH`, `CRITICAL`.

---

## 5. Demo / Example Data Disclaimer

> [!IMPORTANT]
> All sample values provided in `docs/examples/` (such as `rockfall_probability: 0.84` or `displacement_mm: 24.2`) are illustrative demonstration values used solely for contract validation and interface alignment across sub-teams. They do not represent real-world physical measurements or evaluated model performance metrics.
