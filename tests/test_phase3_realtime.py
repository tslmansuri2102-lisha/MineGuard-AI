"""
MineGuard AI — Phase 3 Real-Time Architecture Unit Tests
"""

import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from iot.sensor_schema import TelemetrySchema, validate_raw_telemetry_dict
from iot.device_manager import DeviceManager
from simulation.scenarios import ScenarioGenerator
from simulation.telemetry import create_simulated_telemetry
from inference.rolling_window import RollingWindowBuffer
from inference.feature_adapter import FeatureAdapter
from inference.predictor import RealTimePredictor
from risk_engine.risk_calculator import RiskCalculator
from risk_engine.escalation import EscalationEvaluator
from alerts.alert_store import AlertStore
from alerts.alert_manager import AlertManager
from api.main import app


class TestPhase3RealTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_telemetry_schema_validation(self):
        """Test canonical telemetry schema validation and malformed payload rejection."""
        valid_payload = {
            "event_id": "EVT-001",
            "timestamp": "2026-08-16T10:00:00Z",
            "sensor_id": "SENSOR-001",
            "zone_id": "ZONE-001",
            "latitude": 23.7954,
            "longitude": 86.4304,
            "vibration_g": 0.15,
            "strain": 0.20,
            "displacement_mm": 2.5,
            "slope_velocity_mm_s": 0.002,
            "temperature_c": 25.0,
            "rainfall_mm": 0.0,
            "rainfall_1h": 0.0,
            "rainfall_6h": 0.0,
            "battery_pct": 99.0,
            "human_report_count": 0
        }
        is_valid, schema_obj, err = validate_raw_telemetry_dict(valid_payload)
        self.assertTrue(is_valid)
        self.assertIsNotNone(schema_obj)
        self.assertIsNone(err)

        # Test Malformed Latitude (> 90.0)
        invalid_payload = valid_payload.copy()
        invalid_payload["latitude"] = 120.0
        is_valid_inv, schema_inv, err_inv = validate_raw_telemetry_dict(invalid_payload)
        self.assertFalse(is_valid_inv)
        self.assertIsNotNone(err_inv)

    def test_02_simulator_determinism(self):
        """Test deterministic scenario generation with fixed random seed."""
        gen1 = ScenarioGenerator(scenario="CRITICAL_ROCKFALL", seed=123)
        m1 = gen1.generate_step(step_idx=5, total_steps=10)

        gen2 = ScenarioGenerator(scenario="CRITICAL_ROCKFALL", seed=123)
        m2 = gen2.generate_step(step_idx=5, total_steps=10)

        self.assertEqual(m1["vibration_g"], m2["vibration_g"])
        self.assertEqual(m1["displacement_mm"], m2["displacement_mm"])

    def test_03_simulator_scenarios(self):
        """Test physical telemetry metric progression across scenarios."""
        normal_gen = ScenarioGenerator(scenario="NORMAL", seed=42)
        m_norm = normal_gen.generate_step(step_idx=0, total_steps=10)
        self.assertLess(m_norm["vibration_g"], 1.0)
        self.assertLess(m_norm["displacement_mm"], 10.0)

        crit_gen = ScenarioGenerator(scenario="CRITICAL_ROCKFALL", seed=42)
        m_crit = crit_gen.generate_step(step_idx=9, total_steps=10)
        self.assertGreater(m_crit["vibration_g"], 5.0)
        self.assertGreater(m_crit["displacement_mm"], 100.0)

    def test_04_rolling_window_features(self):
        """Test temporal rolling window feature calculation."""
        buffer = RollingWindowBuffer(window_size=10)
        for i in range(5):
            t_payload = {
                "sensor_id": "SENSOR-TEST",
                "vibration_g": 0.1 * i,
                "strain": 0.2 * i,
                "displacement_mm": 1.0 * i,
                "slope_velocity_mm_s": 0.01 * i,
                "rainfall_mm": 5.0,
                "rainfall_1h": 5.0,
                "rainfall_6h": 10.0
            }
            res = buffer.add_telemetry(t_payload)
            
        self.assertIn("vibration_mean_1m", res)
        self.assertIn("vibration_change_rate", res)
        self.assertIn("sensor_anomaly_score", res)
        self.assertAlmostEqual(res["vibration_current"], 0.4)

    def test_05_feature_adapter_and_model_inference(self):
        """Test adapting real-time telemetry and running ML model predictor."""
        telemetry = {
            "event_id": "EVT-TEST",
            "timestamp": "2026-08-16T12:00:00Z",
            "sensor_id": "SENSOR-001",
            "zone_id": "ZONE-001",
            "latitude": 23.7954,
            "longitude": 86.4304,
            "vibration_g": 3.5,
            "strain": 4.0,
            "displacement_mm": 75.0,
            "slope_velocity_mm_s": 1.2,
            "temperature_c": 22.0,
            "rainfall_mm": 85.0,
            "rainfall_1h": 50.0,
            "rainfall_6h": 120.0
        }
        adapter = FeatureAdapter()
        df_feat = adapter.adapt_telemetry_to_ml_features(telemetry)
        self.assertEqual(len(df_feat), 1)
        self.assertIn("latitude", df_feat.columns)
        self.assertIn("rainfall_mm", df_feat.columns)

        predictor = RealTimePredictor()
        ml_res = predictor.predict(telemetry)
        self.assertIn("ml_probability", ml_res)
        self.assertIn("ml_class", ml_res)
        self.assertTrue(0.0 <= ml_res["ml_probability"] <= 1.0)

    def test_06_risk_calculator_fusion(self):
        """Test risk calculator fusion under NORMAL vs CRITICAL metrics."""
        calc = RiskCalculator()
        telemetry_norm = {
            "zone_id": "ZONE-001",
            "vibration_g": 0.1,
            "displacement_mm": 1.0,
            "slope_velocity_mm_s": 0.001,
            "strain": 0.1,
            "rainfall_mm": 0.0,
            "human_report_count": 0
        }
        ml_norm = {"ml_probability": 0.05}
        r_norm = calc.calculate_risk(telemetry_norm, ml_norm)
        self.assertEqual(r_norm["risk_level"], "LOW")
        self.assertLess(r_norm["risk_score"], 25.0)

        telemetry_crit = {
            "zone_id": "ZONE-001",
            "vibration_g": 8.0,
            "displacement_mm": 150.0,
            "slope_velocity_mm_s": 5.0,
            "strain": 10.0,
            "rainfall_mm": 120.0,
            "human_report_count": 0
        }
        ml_crit = {"ml_probability": 0.92}
        r_crit = calc.calculate_risk(telemetry_crit, ml_crit)
        self.assertIn(r_crit["risk_level"], ["HIGH", "CRITICAL"])
        self.assertGreater(r_crit["risk_score"], 60.0)

    def test_07_risk_escalation_and_confidence(self):
        """Test trend calculation and stale device confidence penalty."""
        trend = EscalationEvaluator.calculate_trend([10.0, 15.0, 35.0])
        self.assertEqual(trend, "RAPIDLY_INCREASING")

        conf_fresh = EscalationEvaluator.calculate_confidence(is_stale=False, sensor_count_in_zone=2, is_isolated_anomaly=False)
        conf_stale = EscalationEvaluator.calculate_confidence(is_stale=True, sensor_count_in_zone=1, is_isolated_anomaly=False)
        self.assertGreater(conf_fresh, conf_stale)

    def test_08_alert_manager_and_cooldown(self):
        """Test alert creation, cooldown suppression, escalation, and resolution."""
        store = AlertStore()
        mgr = AlertManager(alert_store=store, cooldown_seconds=60.0)

        t_data = {"zone_id": "ZONE-TEST", "sensor_id": "S1", "latitude": 23.7, "longitude": 86.4}
        r_high = {"risk_level": "HIGH", "risk_score": 65.0, "contributing_factors": [], "recommended_action": "Act"}

        a1 = mgr.evaluate_risk_and_trigger_alert(t_data, r_high)
        self.assertIsNotNone(a1)
        alert_id = a1["alert_id"]

        # Duplicate alert within cooldown window should be suppressed (None)
        a2 = mgr.evaluate_risk_and_trigger_alert(t_data, r_high)
        self.assertIsNone(a2)

        # Escalation to CRITICAL should bypass cooldown
        r_crit = {"risk_level": "CRITICAL", "risk_score": 90.0, "contributing_factors": [], "recommended_action": "Evacuate"}
        a3 = mgr.evaluate_risk_and_trigger_alert(t_data, r_crit)
        self.assertIsNotNone(a3)

        # Test Acknowledge & Resolve
        ack = store.acknowledge_alert(alert_id)
        self.assertEqual(ack["status"], "ACKNOWLEDGED")
        res = store.resolve_alert(alert_id)
        self.assertEqual(res["status"], "RESOLVED")

    def test_09_fastapi_endpoints_health_and_telemetry(self):
        """Test REST endpoints via FastAPI TestClient."""
        res_health = self.client.get("/api/v1/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "HEALTHY")

        telemetry_payload = {
            "event_id": "EVT-CLIENT-01",
            "timestamp": "2026-08-16T12:00:00Z",
            "sensor_id": "SENSOR-003",
            "zone_id": "ZONE-003",
            "latitude": 23.7954,
            "longitude": 86.4304,
            "vibration_g": 0.12,
            "strain": 0.2,
            "displacement_mm": 2.4,
            "slope_velocity_mm_s": 0.003,
            "temperature_c": 25.0,
            "rainfall_mm": 0.0,
            "rainfall_1h": 0.0,
            "rainfall_6h": 0.0,
            "battery_pct": 98.0,
            "human_report_count": 0
        }
        res_post = self.client.post("/api/v1/telemetry", json=telemetry_payload)
        self.assertEqual(res_post.status_code, 200)
        body = res_post.json()
        self.assertEqual(body["status"], "ACCEPTED")

        res_risk = self.client.get("/api/v1/risk/ZONE-003")
        self.assertEqual(res_risk.status_code, 200)
        self.assertEqual(res_risk.json()["zone_id"], "ZONE-003")

        res_alerts = self.client.get("/api/v1/alerts")
        self.assertEqual(res_alerts.status_code, 200)

        res_zones = self.client.get("/api/v1/zones")
        self.assertEqual(res_zones.status_code, 200)

        res_sensors = self.client.get("/api/v1/sensors")
        self.assertEqual(res_sensors.status_code, 200)

    def test_10_fastapi_malformed_telemetry_handling(self):
        """Test API safely handles malformed telemetry without crashing."""
        malformed_payload = {
            "event_id": "EVT-BAD",
            "timestamp": "invalid-timestamp",
            "latitude": 500.0  # Invalid latitude
        }
        res = self.client.post("/api/v1/telemetry", json=malformed_payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("detail", res.json())


if __name__ == "__main__":
    unittest.main()
