# MineGuard AI — Phase 3 Real-Time Architecture & Early-Warning System

## 1. Executive Summary

This specification documents the production-style real-time architecture built in **MineGuard AI Phase 3**.

The architecture connects physical ESP32 edge telemetry and deterministic scenario simulations to a unified processing pipeline consisting of:
- Canonical Telemetry Ingestion & Validation (`iot/sensor_schema.py`)
- Device Health & Stale Sensor Detection (`iot/device_manager.py`)
- Rolling-Window Temporal Feature Engineering (`inference/rolling_window.py`)
- Real-Time ML Inference Engine (`inference/predictor.py` + `feature_adapter.py`)
- Risk Fusion Calculator & Escalation Evaluator (`risk_engine/risk_calculator.py`)
- Alert Escalation, Cooldown, & Deduplication Manager (`alerts/alert_manager.py`)
- FastAPI REST Services & WebSockets Broadcaster (`api/main.py`)

> [!IMPORTANT]
> **Safety Disclaimer**: MineGuard AI is a decision-support and early-warning prototype designed to estimate slope instability risks. It does not guarantee absolute rockfall prediction. Evacuation directives must comply with geotechnical engineering protocols.

---

## 2. End-to-End Real-Time Pipeline Data Flow

```
+--------------------------+       +-------------------------+
|  ESP32 / IoT Hardware    |       |  Deterministic Simulator|
|  (Physical Sensor Nodes) |       |  (Scenario Generator)   |
+--------------------------+       +-------------------------+
             |                                  |
             +----------------+-----------------+
                              |
                              v  (POST /api/v1/telemetry)
             +----------------------------------+
             | Canonical Schema & Validation    |  (Pydantic TelemetrySchema)
             +----------------------------------+
                              |
                              v
             +----------------------------------+
             | Device Health & Stale Checks     |  (DeviceManager)
             +----------------------------------+
                              |
                              v
             +----------------------------------+
             | Rolling-Window Temporal Features |  (RollingWindowBuffer)
             +----------------------------------+
                              |
                              +--------------------+
                              |                    |
                              v                    v
             +--------------------+   +-----------------------+
             | ML Feature Adapter |   | Sensor Anomaly &      |
             | & Baseline Model   |   | Physical Trend Check  |
             +--------------------+   +-----------------------+
                              |                    |
                              +---------+----------+
                                        |
                                        v
                       +----------------------------------+
                       | Risk Engine Fusion & Escalation |  (0-100 Risk Score)
                       +----------------------------------+
                                        |
                                        v
                       +----------------------------------+
                       | Alert Manager (Cooldown/Escalation)|
                       +----------------------------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   v                                         v
+------------------------------------+    +----------------------------------+
| Local Persistence Store            |    | Real-Time WebSocket Broadcaster |
| (alerts/alert_store.py)            |    | (ws_manager /ws)                 |
+------------------------------------+    +----------------------------------+
```

---

## 3. Canonical Telemetry Contract

All physical ESP32 edge units and simulator routines produce telemetry payloads matching the canonical `TelemetrySchema` (`iot/sensor_schema.py`):

```json
{
  "event_id": "EVT-8A2F91C0",
  "timestamp": "2026-08-16T12:00:00Z",
  "sensor_id": "SENSOR-003",
  "zone_id": "ZONE-003",
  "latitude": 23.7954,
  "longitude": 86.4304,
  "vibration_g": 3.5,
  "strain": 4.2,
  "displacement_mm": 75.0,
  "slope_velocity_mm_s": 1.2,
  "temperature_c": 22.5,
  "rainfall_mm": 45.0,
  "rainfall_1h": 25.0,
  "rainfall_6h": 65.0,
  "battery_pct": 98.5,
  "human_report_count": 0
}
```

### Validation Rules
- `latitude` / `longitude`: Valid WGS84 range limits (\(-90 \le \text{lat} \le 90\), \(-180 \le \text{lon} \le 180\)).
- `timestamp`: Strict UTC ISO 8601 strings.
- Non-negative constraints: `vibration_g`, `strain`, `displacement_mm`, `slope_velocity_mm_s`, `rainfall_mm` must be \(\ge 0.0\).
- Malformed payloads return HTTP 400 without crashing API server services.

---

## 4. ML Model Integration & Feature Adapter

The inference engine (`inference/predictor.py`) loads the Phase 2 Random Forest model (`models/baseline/model.joblib`) and preprocessor (`models/baseline/preprocessor.joblib`).

Because real-time IoT telemetry contains high-frequency features not present in historical catalogs, `inference/feature_adapter.py` maps canonical telemetry into the 16 engineered features expected by the Phase 2 ML model:
- `rainfall_mm`, `rainfall_3h_sum`, `rainfall_24h_sum`: Derived from precipitative telemetry fields.
- `displacement_velocity`: Derived from `slope_velocity_mm_s` (converted to mm/h).
- `landslide_trigger`: Categorized automatically (`downpour`, `rain`, `mining`, `unknown`).

If model artifacts are missing, the predictor operates in a fail-safe `DEGRADED` mode using heuristic estimates.

---

## 5. Risk Engine Fusion & Escalation Logic

The Risk Engine (`risk_engine/risk_calculator.py`) calculates a unified **0 – 100 Risk Score**:

$$\text{RiskScore} = \sum_{i} w_i \cdot S_i$$

### Sub-Score Weighting Matrix

| Feature Input | Sub-Score Scaling | Configured Weight ($w_i$) |
| :--- | :--- | :--- |
| **ML Failure Probability** | $P_{\text{ML}} \times 100$ | **0.35** |
| **Ground Vibration ($g$)** | $(g / 5.0) \times 100$ | **0.15** |
| **Displacement ($mm$)** | $(D / 100.0) \times 100$ | **0.15** |
| **Slope Velocity ($mm/s$)** | $(v / 2.0) \times 100$ | **0.12** |
| **Microstrain ($\mu\varepsilon$)** | $(\varepsilon / 5.0) \times 100$ | **0.10** |
| **Sensor Anomaly Score** | $Z_{\text{Score}} \times 100$ | **0.08** |
| **Rainfall ($mm$)** | $(R / 80.0) \times 100$ | **0.03** |
| **Human Reports** | $\text{Count} \times 25.0$ | **0.02** |

> [!NOTE]
> **Human Reports Rule**: Auxiliary signal only (weight 0.02). Zones with 0 human reports generate `HIGH` or `CRITICAL` alerts based purely on physical telemetry.

### Risk Level Categorization

| Score Range | Risk Level | Recommended Action |
| :--- | :--- | :--- |
| **0 – 25** | `LOW` | Routine slope stability monitoring. Operations normal. |
| **26 – 50** | `MODERATE` | Heightened vigilance. Increase sensor sampling frequency. |
| **51 – 75** | `HIGH` | WARNING: Restrict heavy machinery on bench. Alert safety engineer. |
| **76 – 100** | `CRITICAL` | **EMERGENCY: EVACUATE BENCH WORKERS IMMEDIATELY! TRIGGER ALARM!** |

### Confidence & Stale Sensor Handling
- If a sensor has not transmitted data for > 60 seconds, `DeviceManager` marks it `STALE`, reducing confidence by 0.35.
- Multiple sensors agreeing in the same zone increases confidence (+0.10).

---

## 6. Alert Management & Escalation

The Alert Manager (`alerts/alert_manager.py`) manages notification creation, cooldown, deduplication, and escalation:
- **Cooldown Rule**: Suppresses duplicate alerts for the same zone within a 60-second window.
- **Escalation Bypass**: If a zone escalates from `HIGH` to `CRITICAL`, cooldown is bypassed immediately to fire an emergency alert.
- **Deduplication**: Suppresses alerts if risk level is unchanged and score delta < 5.0.

---

## 7. Deterministic Sensor Simulation

The simulator (`simulation/sensor_simulator.py`) generates physical temporal trends across 4 scenarios:
- `NORMAL`: Stable vibration (0.1g), displacement < 3mm.
- `DEVELOPING_INSTABILITY`: Linear rise in vibration, strain, displacement, and rainfall.
- `HIGH_RISK`: Accelerating vibration (3.0g+), high strain (4.5µε), heavy rainfall.
- `CRITICAL_ROCKFALL`: Exponential tertiary creep acceleration (vibration > 10g, displacement > 200mm, velocity > 10mm/s).

---

## 8. API & WebSocket Reference

### REST Endpoints
- `GET /api/v1/health`: System health and artifact status.
- `POST /api/v1/telemetry`: Canonical telemetry ingestion endpoint.
- `GET /api/v1/risk/{zone_id}`: Retrieve latest risk score for mine zone.
- `GET /api/v1/alerts`: List safety alerts (`zone_id` filter available).
- `POST /api/v1/alerts/{alert_id}/acknowledge`: Mark alert acknowledged.
- `POST /api/v1/alerts/{alert_id}/resolve`: Mark alert resolved.
- `GET /api/v1/zones`: List mine bench zones and live risk levels.
- `GET /api/v1/sensors`: List registered sensor units and `ONLINE`/`STALE` status.

### Real-Time WebSocket
- `WS /ws`: Broadcasts `TELEMETRY_INGESTED` and `ALERT_TRIGGERED` JSON events to subscribers.

---

## 9. Next Steps for Physical ESP32 Hardware Integration

1. Flash ESP32 units with HTTP Client firmware targeting `POST http://<server-ip>:8000/api/v1/telemetry`.
2. Format payload to match `TelemetrySchema` JSON.
3. Configure Wi-Fi / LoRaWAN gateway routing to relay payloads.
