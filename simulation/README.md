# MineGuard AI — Sensor Simulator Package (`simulation/`)

## Overview

The `simulation/` package provides a deterministic, scenario-based physics simulator that generates real-time telemetry matching the canonical `TelemetrySchema`.

It allows testing the end-to-end pipeline (`Telemetry -> Ingestion -> Rolling Features -> ML Inference -> Risk Engine -> Alerts -> WebSockets`) under 4 realistic mine bench stability scenarios:
1. `NORMAL`: Baseline stable vibration (0.1g), low strain, low displacement.
2. `DEVELOPING_INSTABILITY`: Linear rise in vibration, strain, displacement, and rainfall.
3. `HIGH_RISK`: Accelerating vibration (3.0g+), high strain (4.5µε), heavy rainfall.
4. `CRITICAL_ROCKFALL`: Exponential tertiary creep acceleration (vibration 10g+, displacement > 200mm, velocity > 10mm/s).

---

## Usage Commands

```bash
# Run NORMAL scenario
python -m simulation.sensor_simulator --scenario NORMAL --duration 10 --interval 1.0

# Run CRITICAL scenario and post to local API
python -m simulation.sensor_simulator --scenario CRITICAL_ROCKFALL --duration 10 --interval 0.5 --api-url http://localhost:8000/api/v1/telemetry
```
