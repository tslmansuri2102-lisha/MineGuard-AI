"""
MineGuard AI — Risk REST & WebSocket API Integration Tests
Validates risk endpoints, alert dispatch, history store, and real-time streaming payloads.
"""

import json
import unittest
from fastapi.testclient import TestClient

from backend.alerts import alert_service
from backend.main import app
from backend.services import simulation_service
from simulation.scenarios import ScenarioType


class TestRiskAPI(unittest.TestCase):
    """Integration test suite for Risk REST endpoints and alerts."""

    def setUp(self):
        self.client = TestClient(app)
        alert_service.clear()
        simulation_service.start_simulation(
            mine_id="MINE-001",
            zone_id="ZONE-003",
            sensor_id="SENSOR-003",
            scenario="NORMAL",
            interval=0.1,
            seed=42,
        )

    # 1. GET /api/v1/risk/latest
    def test_01_get_latest_risk_endpoint(self):
        """Test GET /api/v1/risk/latest returns valid risk payload."""
        response = self.client.get("/api/v1/risk/latest")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["mine_id"], "MINE-001")
        self.assertEqual(data["zone_id"], "ZONE-003")
        self.assertEqual(data["sensor_id"], "SENSOR-003")
        self.assertIn("risk_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("confidence", data)
        self.assertIn("status", data)
        self.assertIn("factors", data)
        self.assertIn("recommended_action", data)

    # 2. GET /api/v1/risk/{mine_id}/{zone_id}/{sensor_id}
    def test_02_get_sensor_risk_by_id(self):
        """Test GET /api/v1/risk/MINE-001/ZONE-003/SENSOR-003."""
        response = self.client.get("/api/v1/risk/MINE-001/ZONE-003/SENSOR-003")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mine_id"], "MINE-001")
        self.assertIn(data["risk_level"], ("LOW", "MODERATE", "HIGH", "CRITICAL"))

    # 3. POST /api/v1/risk/predict
    def test_03_predict_risk_for_supplied_reading(self):
        """Test POST /api/v1/risk/predict with high danger readings."""
        payload = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "timestamp": "2026-08-16T12:00:00Z",
            "sensors": {
                "displacement_mm": 45.0,
                "strain": 0.85,
                "pore_pressure_kpa": 75.0,
                "rainfall_mm": 80.0,
                "temperature_c": 28.0,
                "vibration_g": 1.8,
            },
        }
        response = self.client.post("/api/v1/risk/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_level"], "CRITICAL")
        self.assertGreaterEqual(data["risk_score"], 80.0)

    # 4. GET /api/v1/risk/history
    def test_04_get_risk_history(self):
        """Test GET /api/v1/risk/history returns historical entries."""
        # Generate several readings
        simulation_service.generate_next_reading()
        simulation_service.generate_next_reading()

        response = self.client.get("/api/v1/risk/history?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    # 5. Alert triggering on HIGH/CRITICAL
    def test_05_alert_triggering_and_history(self):
        """Test that CRITICAL scenario triggers alert and records in alert history."""
        # Start CRITICAL_COMBINED simulation
        self.client.post(
            "/api/v1/simulation/start",
            json={
                "mine_id": "MINE-001",
                "zone_id": "ZONE-003",
                "sensor_id": "SENSOR-003",
                "scenario": "CRITICAL_COMBINED",
                "interval": 0.1,
                "seed": 42,
            },
        )
        # Advance simulation to trigger alert
        simulation_service.generate_next_reading()
        simulation_service.generate_next_reading()

        response = self.client.get("/api/v1/alerts/history")
        self.assertEqual(response.status_code, 200)
        alerts = response.json()
        self.assertGreaterEqual(len(alerts), 1)
        self.assertIn(alerts[0]["risk_level"], ("HIGH", "CRITICAL"))

    # 6. WebSocket streaming includes risk assessment
    def test_06_websocket_stream_includes_risk_payload(self):
        """Test WebSocket delivers unified telemetry and risk block."""
        simulation_service.start_simulation(interval=0.01)
        with self.client.websocket_connect("/ws/sensors") as websocket:
            data = websocket.receive_json()
            self.assertIn("telemetry", data)
            self.assertIn("risk", data)
            self.assertIn("score", data["risk"])
            self.assertIn("level", data["risk"])
            self.assertIn("factors", data["risk"])
            self.assertIn("recommended_action", data["risk"])


if __name__ == "__main__":
    unittest.main()
