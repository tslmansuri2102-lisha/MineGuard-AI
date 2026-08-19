import json
import random
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


API_URL = "http://localhost:8000/api/v1/sensors/readings"

MINE_ID = "MINE-001"
ZONE_ID = "ZONE-003"
SENSOR_ID = "SENSOR-003"

random.seed(42)


def generate_telemetry(step):
    if step < 10:
        displacement = 24.0 + random.uniform(-0.5, 0.5)
        strain = 0.30 + random.uniform(-0.02, 0.02)
        pore_pressure = 35.0 + random.uniform(-1.5, 1.5)
        rainfall = 5.0 + random.uniform(-1.0, 1.0)
        temperature = 28.0 + random.uniform(-1.0, 1.0)
        vibration = 0.20 + random.uniform(-0.03, 0.03)

    elif step < 20:
        progress = step - 10

        displacement = 24.0 + progress * 1.8 + random.uniform(-0.5, 0.5)
        strain = 0.30 + progress * 0.035 + random.uniform(-0.02, 0.02)
        pore_pressure = 35.0 + progress * 2.5 + random.uniform(-1.5, 1.5)
        rainfall = 10.0 + progress * 3.0 + random.uniform(-1.0, 1.0)
        temperature = 29.0 + random.uniform(-1.0, 1.0)
        vibration = 0.30 + progress * 0.08 + random.uniform(-0.03, 0.03)

    else:
        progress = step - 20

        displacement = 45.0 + progress * 1.5 + random.uniform(-0.8, 0.8)
        strain = 0.70 + progress * 0.025 + random.uniform(-0.02, 0.02)
        pore_pressure = 65.0 + progress * 2.0 + random.uniform(-2.0, 2.0)
        rainfall = 70.0 + progress * 2.5 + random.uniform(-2.0, 2.0)
        temperature = 31.0 + random.uniform(-1.0, 1.0)
        vibration = 1.20 + progress * 0.08 + random.uniform(-0.05, 0.05)

    return {
        "mine_id": MINE_ID,
        "zone_id": ZONE_ID,
        "sensor_id": SENSOR_ID,
        "timestamp": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "sensors": {
            "displacement_mm": round(max(0.0, displacement), 2),
            "strain": round(max(0.0, strain), 3),
            "pore_pressure_kpa": round(max(0.0, pore_pressure), 2),
            "rainfall_mm": round(max(0.0, rainfall), 2),
            "temperature_c": round(temperature, 2),
            "vibration_g": round(max(0.0, vibration), 3),
        },
    }


def send_telemetry(reading):
    payload = json.dumps(reading).encode("utf-8")

    request = Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

            print("\n==========================================")
            print("MineGuard IoT Telemetry")
            print("==========================================")
            print("HTTP Status:", response.status)
            print("Sensor:", reading["sensor_id"])
            print("Zone:", reading["zone_id"])
            print("Timestamp:", reading["timestamp"])
            print()
            print("Telemetry:")
            print(json.dumps(reading["sensors"], indent=2))
            print()
            print("Backend Response:")
            print(json.dumps(response_data, indent=2))
            print("==========================================")

    except HTTPError as error:
        print("\nBackend rejected telemetry.")
        print("HTTP Status:", error.code)

        try:
            print(error.read().decode("utf-8"))
        except Exception:
            pass

    except URLError as error:
        print("\nCould not connect to MineGuard backend.")
        print("Reason:", error.reason)

    except Exception as error:
        print("\nUnexpected error:", error)


def main():
    print("MineGuard AI — Dynamic IoT Telemetry Sender")
    print("-------------------------------------------")
    print("Target:", API_URL)
    print()
    print("Telemetry progression:")
    print("Steps  0-9  : Normal")
    print("Steps 10-19 : Increasing instability")
    print("Steps 20+   : High-risk conditions")
    print()

    step = 0

    while True:
        reading = generate_telemetry(step)

        print(f"\nSENDING TELEMETRY STEP {step + 1}")

        send_telemetry(reading)

        step += 1

        print("\nSending next reading in 5 seconds...")
        time.sleep(5)


if __name__ == "__main__":
    main()