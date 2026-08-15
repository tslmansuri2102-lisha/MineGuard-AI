# MineGuard AI — API Contract

## 1. Project Information

Project: MineGuard AI  
API Version: v1  
Contract Version: 1.0.0  
Status: Active Development

---

## 2. Base URL

Development:

http://localhost:8000

API Base Path:

/api/v1

Full Base URL:

http://localhost:8000/api/v1

---

## 3. General Rules

All requests and responses use JSON unless otherwise specified.

Content-Type:

application/json

All timestamps use UTC ISO 8601 format.

Example:

2026-08-14T10:30:00Z

Probability values range from 0 to 1.

Example:

0.84 = 84%

Allowed risk levels:

- LOW
- MODERATE
- HIGH
- CRITICAL

---

## 4. Identifier Format

Mine:

MINE-001

Zone:

ZONE-001

Sensor:

SENSOR-001

Reading:

READ-000001

Prediction:

PRED-000001

Alert:

ALERT-000001

Simulation:

SIM-000001

Drone Analysis:

DRONE-000001

---

# 5. Sensor Data

## POST /api/v1/sensors/readings

Purpose:

Receive readings from sensor simulators, IoT devices, ESP32
hardware and future real mine sensors.

### Request

```json
{
  "mine_id": "MINE-001",
  "zone_id": "ZONE-003",
  "sensor_id": "SENSOR-003",
  "timestamp": "2026-08-14T10:30:00Z",
  "sensors": {
    "displacement_mm": 24.2,
    "strain": 0.81,
    "pore_pressure_kpa": 62.0,
    "rainfall_mm": 74.0,
    "temperature_c": 32.0,
    "vibration_g": 1.2
  }
}
