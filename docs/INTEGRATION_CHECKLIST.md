# MineGuard AI — Integration Checklist

## Phase 0 — Team Contract Alignment & Setup

This checklist tracks cross-team contract validation and integration milestones for **MineGuard AI** across feature branches (`feature/ml-ai-data`, `feature/frontend`, `feature/gis-dem-drone`, `feature/simulation-iot-alerts`).

---

## 1. Contract & Schema Alignment

- [x] **API contract understood**: Reviewed `API_CONTRACT.md` rules, base paths (`/api/v1`), identifier patterns, and payload formats.
- [x] **ML input schema finalized**: Input schema documented in `docs/ML_DATA_DICTIONARY.md` and validated via `docs/examples/ml_request_example.json`.
- [x] **ML output schema finalized**: Response payload schema defined, supporting probability (`0.0`–`1.0`), risk levels (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), and `contributing_factors`.
- [x] **IoT fields mapped**: Sensor fields (`displacement_mm`, `strain`, `pore_pressure_kpa`, `rainfall_mm`, `temperature_c`, `vibration_g`) mapped to `API_CONTRACT.md`.
- [x] **GIS/DEM fields mapped**: Terrain features (`latitude`, `longitude`, `elevation_m`, `slope_deg`, `aspect_deg`, `curvature`) mapped for integration with `feature/gis-dem-drone`.
- [x] **Simulation fields mapped**: Synthetic sensor streams aligned with physical sensor specifications and data dictionary requirements.
- [x] **Frontend response format understood**: Standardized prediction structure defined to support dashboard visualization, risk badges, and explainability charts.

---

## 2. Technical Integration Milestones (To Be Completed During Implementation Phase)

- [ ] **Prediction endpoint integration**: Wire `/api/v1/sensors/readings` and prediction handlers to the ML model inference pipeline.
- [ ] **Error handling**: Implement fallback logic and error status responses (`SUCCESS`, `ERROR`, `DEGRADED`) when sensor data is missing or malformed.
- [ ] **Timestamp handling**: Ensure strict UTC ISO 8601 parsing and serialization across all ingestion, feature engineering, and output steps.
- [ ] **Location handling**: Ensure correct spatial matching of zone IDs (`ZONE-003`) and WGS84 coordinates between GIS DEM models and telemetry records.
- [ ] **Model version handling**: Persist model artifact versions (`model_version`: `v1.0.0`) in prediction outputs for auditability and experiment tracking.
- [ ] **Final end-to-end test**: Execute full integration workflow from IoT/Simulation telemetry -> GIS enrichment -> ML inference -> Backend API -> Frontend Dashboard -> Alert trigger.
