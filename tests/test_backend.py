"""
MineGuard AI — Backend API & WebSocket Test Suite
Tests REST endpoints, simulation control, and WebSocket streaming conforming to API_CONTRACT.md.
"""

from datetime import datetime, timezone
import json
import unittest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import simulation_service
from simulation.scenarios import ScenarioType
from simulation.validation import validate_reading, is_valid_reading


class TestBackendAPI(unittest.TestCase):
    """
    Test suite for FastAPI REST and WebSocket endpoints.
    """

    def setUp(self):
        """Reset simulation service state before each test."""
        self.client = TestClient(app)
        simulation_service.start_simulation(
            mine_id="MINE-001",
            zone_id="ZONE-003",
            sensor_id="SENSOR-003",
            scenario="NORMAL",
            interval=1.0,
            seed=42,
        )

    # 1. GET /health returns 200
    def test_01_health_endpoint_status_200(self):
        """Test GET /health returns HTTP 200."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    # 2. Health response contains status
    def test_02_health_response_content(self):
        """Test GET /health returns expected status message."""
        response = self.client.get("/health")
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "MineGuard AI backend")

    # 3. Latest sensor endpoint returns valid contract payload
    def test_03_latest_sensor_reading_contract_payload(self):
        """Test GET /api/v1/sensors/latest returns valid API contract payload."""
        response = self.client.get("/api/v1/sensors/latest")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Validate against schema
        self.assertTrue(is_valid_reading(data))
        validate_reading(data)

        self.assertEqual(data["mine_id"], "MINE-001")
        self.assertEqual(data["zone_id"], "ZONE-003")
        self.assertEqual(data["sensor_id"], "SENSOR-003")
        self.assertIn("timestamp", data)
        self.assertIn("sensors", data)

        sensors = data["sensors"]
        for key in (
            "displacement_mm",
            "strain",
            "pore_pressure_kpa",
            "rainfall_mm",
            "temperature_c",
            "vibration_g",
        ):
            self.assertIn(key, sensors)
            self.assertIsInstance(sensors[key], (int, float))

    # 4. Sensor lookup endpoint works
    def test_04_sensor_lookup_endpoint(self):
        """Test GET /api/v1/sensors/{mine_id}/{zone_id}/{sensor_id} returns reading."""
        response = self.client.get("/api/v1/sensors/MINE-001/ZONE-003/SENSOR-003")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mine_id"], "MINE-001")
        self.assertEqual(data["zone_id"], "ZONE-003")
        self.assertEqual(data["sensor_id"], "SENSOR-003")
        validate_reading(data)

    # 5. Invalid sensor returns appropriate error (404)
    def test_05_invalid_sensor_lookup_returns_404(self):
        """Test querying non-existent sensor returns HTTP 404."""
        response = self.client.get("/api/v1/sensors/MINE-999/ZONE-999/SENSOR-999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)

    # 6. Invalid scenario is rejected with 400 Bad Request
    def test_06_invalid_scenario_rejected(self):
        """Test starting simulation with invalid scenario returns HTTP 400."""
        payload = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "scenario": "TOTALLY_INVALID_SCENARIO",
            "interval": 1.0,
        }
        response = self.client.post("/api/v1/simulation/start", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)

    # 7. Simulation start endpoint works
    def test_07_simulation_start_endpoint_works(self):
        """Test POST /api/v1/simulation/start successfully starts simulation."""
        payload = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "scenario": "HEAVY_RAIN",
            "interval": 0.5,
            "seed": 100,
        }
        response = self.client.post("/api/v1/simulation/start", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["scenario"], "HEAVY_RAIN")
        self.assertTrue(data["is_running"])
        self.assertIn("latest_reading", data)
        validate_reading(data["latest_reading"])

    # 8. Simulation configuration is accepted
    def test_08_simulation_configuration_accepted(self):
        """Test that custom mine_id and interval are properly applied."""
        payload = {
            "mine_id": "MINE-002",
            "zone_id": "ZONE-004",
            "sensor_id": "SENSOR-005",
            "scenario": "PROGRESSIVE_INSTABILITY",
            "interval": 2.5,
            "seed": 42,
        }
        response = self.client.post("/api/v1/simulation/start", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mine_id"], "MINE-002")
        self.assertEqual(data["zone_id"], "ZONE-004")
        self.assertEqual(data["sensor_id"], "SENSOR-005")
        self.assertEqual(data["interval_seconds"], 2.5)

    # 9. Generated backend payload passes existing validation
    def test_09_backend_payload_passes_strict_validation(self):
        """Test generated sensor payload from service passes strict validation."""
        reading = simulation_service.generate_next_reading()
        self.assertTrue(is_valid_reading(reading))
        validate_reading(reading)

    # 10. WebSocket connection succeeds
    def test_10_websocket_connection_succeeds(self):
        """Test WebSocket client connects successfully to /ws/sensors."""
        simulation_service.start_simulation(interval=0.01)
        with self.client.websocket_connect("/ws/sensors") as websocket:
            data = websocket.receive_json()
            self.assertIsInstance(data, dict)

    # 11. WebSocket receives sensor telemetry
    def test_11_websocket_receives_telemetry(self):
        """Test WebSocket receives sensor telemetry payload."""
        simulation_service.start_simulation(interval=0.01)
        with self.client.websocket_connect("/ws/sensors") as websocket:
            data = websocket.receive_json()
            self.assertIn("mine_id", data)
            self.assertIn("zone_id", data)
            self.assertIn("sensor_id", data)
            self.assertIn("timestamp", data)
            self.assertIn("sensors", data)

    # 12. WebSocket telemetry matches API contract
    def test_12_websocket_telemetry_matches_api_contract(self):
        """Test WebSocket telemetry payload strictly adheres to API_CONTRACT.md."""
        simulation_service.start_simulation(interval=0.01)
        with self.client.websocket_connect("/ws/sensors") as websocket:
            data = websocket.receive_json()
            validate_reading(data)

    # 13. Multiple WebSocket messages can be received
    def test_13_multiple_websocket_messages_received(self):
        """Test streaming multiple consecutive messages over WebSocket."""
        # Use interval=1.0 so each step advances 1 second
        simulation_service.start_simulation(interval=0.05)
        with self.client.websocket_connect("/ws/sensors") as websocket:
            readings = []
            for _ in range(3):
                msg = websocket.receive_json()
                validate_reading(msg)
                readings.append(msg)
            
            self.assertEqual(len(readings), 3)
            # Verify each message has valid sensors and IDs
            for r in readings:
                self.assertEqual(r["mine_id"], "MINE-001")
                self.assertEqual(r["zone_id"], "ZONE-003")

    # 14. Same seed produces deterministic simulation behavior
    def test_14_deterministic_seed_via_api(self):
        """Test deterministic behavior via simulation start endpoint."""
        payload1 = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "scenario": "CRITICAL_COMBINED",
            "interval": 1.0,
            "seed": 999,
        }
        self.client.post("/api/v1/simulation/start", json=payload1)
        r1_a = simulation_service.generate_next_reading()
        r2_a = simulation_service.generate_next_reading()

        # Restart with identical seed
        self.client.post("/api/v1/simulation/start", json=payload1)
        r1_b = simulation_service.generate_next_reading()
        r2_b = simulation_service.generate_next_reading()

        self.assertEqual(r1_a["sensors"], r1_b["sensors"])
        self.assertEqual(r2_a["sensors"], r2_b["sensors"])


if __name__ == "__main__":
    unittest.main()
