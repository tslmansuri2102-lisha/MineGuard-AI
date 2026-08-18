"""
MineGuard AI — WebSocket Client Demonstration Script
Connects to ws://localhost:8000/ws/sensors and prints real-time telemetry stream.
"""

import argparse
import asyncio
import json
import os
import sys

# Ensure repository root is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import websockets
from simulation.validation import validate_reading


def format_client_reading(count: int, reading: dict) -> str:
    sensors = reading.get("sensors", {})
    return (
        f"\n[STREAM #{count}] {reading.get('mine_id')} / {reading.get('zone_id')} / {reading.get('sensor_id')}\n"
        f"  Timestamp:     {reading.get('timestamp')}\n"
        f"  Displacement:  {sensors.get('displacement_mm', 0):.2f} mm\n"
        f"  Strain:        {sensors.get('strain', 0):.2f}\n"
        f"  Pore Pressure: {sensors.get('pore_pressure_kpa', 0):.2f} kPa\n"
        f"  Rainfall:      {sensors.get('rainfall_mm', 0):.2f} mm\n"
        f"  Temperature:   {sensors.get('temperature_c', 0):.2f} °C\n"
        f"  Vibration:     {sensors.get('vibration_g', 0):.2f} g"
    )


async def listen_to_telemetry(uri: str, max_messages: int = 5, json_only: bool = False):
    print(f"Connecting to MineGuard AI WebSocket stream at: {uri} ...")
    try:
        async with websockets.connect(uri) as ws:
            print("Connected! Listening for live telemetry stream...\n")
            msg_count = 0
            while max_messages == 0 or msg_count < max_messages:
                raw_data = await ws.recv()
                msg_count += 1
                payload = json.loads(raw_data)

                # Validate against API contract
                validate_reading(payload)

                if json_only:
                    print(json.dumps(payload, indent=2))
                else:
                    print(format_client_reading(msg_count, payload))

            print(f"\nSuccessfully received and validated {msg_count} live telemetry payloads.")
    except ConnectionRefusedError:
        print(f"\n[ERROR] Connection refused at {uri}.")
        print("Please start the backend server first using:")
        print("  uvicorn backend.main:app --reload --port 8000")
    except Exception as e:
        print(f"\n[ERROR] WebSocket error: {e}")


def main():
    parser = argparse.ArgumentParser(description="MineGuard AI — Live WebSocket Telemetry Client")
    parser.add_argument("--url", default="ws://localhost:8000/ws/sensors", help="WebSocket URI")
    parser.add_argument("--max-messages", type=int, default=5, help="Number of messages to receive (0 for infinite)")
    parser.add_argument("--json", action="store_true", help="Print raw JSON format")

    args = parser.parse_args()
    asyncio.run(listen_to_telemetry(args.url, args.max_messages, args.json))


if __name__ == "__main__":
    main()
