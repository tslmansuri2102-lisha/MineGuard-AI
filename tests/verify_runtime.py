"""
MineGuard AI — Full Runtime & Live WebSocket Stream Verifier
Tests backend endpoints, frontend HTTP status, and live WebSocket streaming during scenario transitions.
"""

import asyncio
import json
import urllib.request
import websockets

def test_rest_endpoints():
    print("==================================================")
    print("1. VERIFYING REST ENDPOINTS")
    print("==================================================")

    # 1. Health
    with urllib.request.urlopen("http://localhost:8000/health") as r:
        health = json.loads(r.read())
        assert health["status"] == "ok"
        print("  [OK] GET /health:", health)

    # 2. Frontend HTML
    with urllib.request.urlopen("http://localhost:5173/") as r:
        html = r.read().decode("utf-8")
        assert "<title>MineGuard AI" in html
        print(f"  [OK] GET http://localhost:5173/ (HTTP {r.status}, HTML length: {len(html)} bytes)")

    # 3. Latest Sensor
    with urllib.request.urlopen("http://localhost:8000/api/v1/sensors/latest") as r:
        sensor = json.loads(r.read())
        assert "sensors" in sensor
        print("  [OK] GET /api/v1/sensors/latest:", sensor["mine_id"], sensor["zone_id"], sensor["sensor_id"])

    # 4. Simulation Status
    with urllib.request.urlopen("http://localhost:8000/api/v1/simulation/status") as r:
        sim = json.loads(r.read())
        assert sim["is_running"] is True
        print("  [OK] GET /api/v1/simulation/status: Scenario =", sim["scenario"])

    # 5. Latest Risk
    with urllib.request.urlopen("http://localhost:8000/api/v1/risk/latest") as r:
        risk = json.loads(r.read())
        assert "risk_score" in risk
        print(f"  [OK] GET /api/v1/risk/latest: Level={risk['risk_level']} Score={risk['risk_score']} Confidence={risk['confidence']}")

    # 6. Alert History
    with urllib.request.urlopen("http://localhost:8000/api/v1/alerts/history") as r:
        alerts = json.loads(r.read())
        print(f"  [OK] GET /api/v1/alerts/history: Count={len(alerts)}")


async def test_websocket_and_scenarios():
    print("\n==================================================")
    print("2. VERIFYING LIVE WEBSOCKET & SCENARIO TRANSITIONS")
    print("==================================================")

    uri = "ws://localhost:8000/ws/sensors"
    async with websockets.connect(uri) as ws:
        print("  [OK] WebSocket connected to", uri)

        scenarios = ["NORMAL", "HEAVY_RAIN", "CRITICAL_COMBINED", "SENSOR_FAILURE", "RECOVERY"]
        for sc in scenarios:
            # Trigger scenario change via REST API
            req = urllib.request.Request(
                "http://localhost:8000/api/v1/simulation/start",
                data=json.dumps({"scenario": sc, "interval": 0.2, "seed": 42}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read())
                print(f"\n  ▶ Switched Scenario to: {sc} (status={res['status']})")

            # Receive 2 live WebSocket messages
            for step in range(2):
                msg_raw = await ws.recv()
                msg = json.loads(msg_raw)
                sensors = msg.get("sensors", {})
                risk = msg.get("risk", {})
                print(f"    Step {step+1}: Disp={sensors.get('displacement_mm')}mm | Pore={sensors.get('pore_pressure_kpa')}kPa | Rain={sensors.get('rainfall_mm')}mm | Vib={sensors.get('vibration_g')}g")
                print(f"            Risk: Level={risk.get('level')} Score={risk.get('score')} Status={risk.get('status')} Action=\"{risk.get('recommended_action')[:45]}...\"")

    print("\n==================================================")
    print("✅ ALL RUNTIME CHECKS & WEBSOCKET DEMOS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    test_rest_endpoints()
    asyncio.run(test_websocket_and_scenarios())
