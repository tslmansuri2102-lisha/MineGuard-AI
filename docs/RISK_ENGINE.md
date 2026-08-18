# MineGuard AI — AI Risk Prediction Engine & Early Warning Documentation

> [!CAUTION]
> **Safety Disclaimer**: The current implementation is a deterministic baseline risk model intended for simulation and prototype demonstration. It is not a certified mine-safety prediction system.

---

## 1. System Architecture

The MineGuard AI Risk Assessment Engine converts raw physics-based sensor telemetry streams into actionable geotechnical hazard intelligence in real time.

```
       SENSOR TELEMETRY (API_CONTRACT.md)
                      │
                      ▼
             FEATURE EXTRACTION
    (Displacement velocity, accel, pore rates, severity indices)
                      │
                      ▼
               AI RISK MODEL
      (Multi-criteria geotechnical model / future ML)
                      │
                      ▼
            RISK SCORE (0 – 100)
                      │
                      ▼
            RISK LEVEL (LOW / MODERATE / HIGH / CRITICAL)
                      │
                      ▼
         EXPLAINABILITY & FACTOR ATTRIBUTION
                      │
                      ▼
          RECOMMENDED SAFETY MITIGATION
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  REST & WEBSOCKET APIs       ALERT DISPATCH ENGINE
 (Frontend Dashboard)        (SMS / Email / Webhooks)
```

---

## 2. Feature Engineering

Incoming raw sensor values are buffered in a stateful sliding window to compute critical kinematic derivatives and geotechnical indices:

| Feature Name | Type | Physical Meaning |
| :--- | :--- | :--- |
| `displacement_mm` | Direct | Absolute surface displacement from baseline (mm) |
| `displacement_rate` | Derivative | Velocity of slope movement ($\Delta \text{disp} / \Delta t$ in mm/s) |
| `displacement_accel` | Derivative | Acceleration of creep ($\Delta \text{velocity} / \Delta t$ in $\text{mm/s}^2$) |
| `strain` | Direct | Dimensionless shear strain in rock mass |
| `strain_severity` | Index | Normalized strain index relative to baseline |
| `pore_pressure_kpa` | Direct | Ground pore water pressure (kPa) |
| `pore_pressure_rate` | Derivative | Infiltration rate ($\Delta \text{pore} / \Delta t$ in kPa/s) |
| `rainfall_mm` | Direct | Surface precipitation accumulation (mm) |
| `rainfall_intensity`| Direct | Rainfall intensity |
| `vibration_g` | Direct | Peak dynamic vibration amplitude (g) |
| `vibration_severity`| Index | Ratio of dynamic vibration relative to ambient background |
| `combined_instability_index` | Composite | Joint weighted stability indicator |

All numerical calculations enforce zero-division guards and guarantee finite values (no `NaN` or `Infinity`).

---

## 3. Geotechnical Risk Modeling

The baseline risk engine aggregates multiple geotechnical hazard sub-scores:

1. **Displacement & Kinematics (35% Weight)**: Combines displacement magnitude, velocity, and creep acceleration. Tertiary accelerating creep triggers severe risk penalties.
2. **Groundwater Pore Pressure (25% Weight)**: Evaluates hydraulic head and pore water pressure excess. Elevated pore pressure reduces effective normal stress along rock joints.
3. **Precipitation Infiltration (15% Weight)**: Measures storm rainfall volume.
4. **Dynamic Seismic / Blasting Load (15% Weight)**: Measures dynamic peak ground acceleration (PGA).
5. **Rock Mass Shear Strain (10% Weight)**: Quantifies accumulated shear distortion.
6. **Non-Linear Compound Coupling**: In compound disaster scenarios (e.g. heavy storm concurrent with high blasting or rapid displacement), synergistic coupling multipliers elevate the total score to reflect impending collapse.

### Risk Level Boundaries
- **`LOW`** (`0.0 – 29.9`): Safe operating conditions, baseline micro-creep.
- **`MODERATE`** (`30.0 – 59.9`): Early warning signs, elevated rainfall or moderate creep.
- **`HIGH`** (`60.0 – 79.9`): Significant instability, rapid displacement or severe pore pressure.
- **`CRITICAL`** (`80.0 – 100.0`): Imminent slope failure or combined multi-hazard state.

---

## 4. Confidence & Data Quality

Every prediction reports a confidence value (`0.0 – 1.0`) and data quality status:
- **`NORMAL`** (Confidence $\ge 0.90$): Full sensor telemetry stream with valid sliding history.
- **`INSUFFICIENT_DATA`** (Confidence $\approx 0.75 – 0.80$): Initial single reading without prior derivative history.
- **`DEGRADED`** (Confidence $\approx 0.20$): Triggered on sensor malfunction/dropout (`SENSOR_FAILURE` flatline). Alerts operators to inspect sensor hardware rather than trusting automated predictions.

---

## 5. Explainability & Contributing Factors

For transparency and root-cause analysis, every assessment generates prioritized contributing factors:

```json
"factors": [
  { "feature": "displacement_rate", "impact": "HIGH" },
  { "feature": "pore_pressure_kpa", "impact": "HIGH" },
  { "feature": "rainfall_mm", "impact": "MEDIUM" }
]
```

---

## 6. Recommended Safety Mitigations

Automated prototype mitigation actions are mapped directly from risk level:
- **LOW**: *"Continue normal monitoring."*
- **MODERATE**: *"Increase monitoring frequency and inspect the affected zone."*
- **HIGH**: *"Restrict access to the affected zone and perform immediate inspection."*
- **CRITICAL**: *"Evacuate personnel from the affected zone and initiate emergency geotechnical assessment."*
- **DEGRADED**: *"Sensor data quality compromised. Verify sensor health before relying on automated risk assessment."*

---

## 7. API Endpoints & WebSocket Integration

### REST Endpoints
- `GET /api/v1/risk/latest` — Retrieve latest AI risk prediction.
- `GET /api/v1/risk/{mine_id}/{zone_id}/{sensor_id}` — Query risk prediction for a specific sensor.
- `POST /api/v1/risk/predict` — Evaluate risk for an externally supplied sensor telemetry payload.
- `GET /api/v1/risk/history?limit=50` — Retrieve historical risk assessments.
- `GET /api/v1/alerts/history?limit=50` — Retrieve historical safety alerts.

### Real-Time WebSocket (`/ws/sensors`)
Streams unified telemetry and risk assessment payloads:

```json
{
  "mine_id": "MINE-001",
  "zone_id": "ZONE-003",
  "sensor_id": "SENSOR-003",
  "timestamp": "2026-08-16T12:00:00Z",
  "sensors": {
    "displacement_mm": 24.2,
    "strain": 0.81,
    "pore_pressure_kpa": 62.0,
    "rainfall_mm": 74.0,
    "temperature_c": 32.0,
    "vibration_g": 1.2
  },
  "telemetry": { ... },
  "risk": {
    "score": 84.2,
    "level": "CRITICAL",
    "confidence": 0.93,
    "status": "NORMAL",
    "factors": [
      { "feature": "displacement_rate", "impact": "HIGH" },
      { "feature": "pore_pressure_kpa", "impact": "HIGH" }
    ],
    "recommended_action": "Evacuate personnel from the affected zone and initiate emergency geotechnical assessment."
  }
}
```

---

## 8. Alerting & Multi-Channel Subscriber Architecture

The `AlertService` ([`backend/alerts.py`](file:///C:/Users/saniy/MineGuard-AI/backend/alerts.py)) automatically triggers on `HIGH` or `CRITICAL` risk predictions and dispatches `AlertEvent` objects to registered subscriber callbacks (e.g. SMS via Twilio, Email via SendGrid, Push Notifications, WhatsApp Webhooks).

---

## 9. Future Machine Learning Integration

The `BaseRiskModel` interface allows seamless replacement of the rule-based model with trained production ML models (such as Random Forest, XGBoost, or temporal LSTM/Transformer architectures) without modifying the downstream REST API, WebSocket streams, or dashboard contracts.
