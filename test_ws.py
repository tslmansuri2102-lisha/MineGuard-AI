import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:8000/ws/sensors"

    async with websockets.connect(uri) as ws:
        print("WEBSOCKET CONNECTED")

        for i in range(5):
            msg = json.loads(await ws.recv())

            print(f"\nMESSAGE {i+1}")
            print("Scenario:", msg.get("scenario"))
            print("Risk:", msg.get("risk"))
            print("Displacement:", msg.get("telemetry", {}).get("sensors", {}).get("displacement_mm"))

asyncio.run(main())
