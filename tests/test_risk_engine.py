"""
MineGuard AI — Risk Engine Unit Test Suite
Tests feature engineering, multi-criteria risk modeling, explainability, and scenario responses.
"""

import math
import unittest

from ai.config import PredictionStatus, RiskLevel, score_to_risk_level
from ai.features import FeatureExtractor
from ai.model import RuleBasedRiskModel
from ai.risk_engine import RiskEngine
from simulation.config import SimulationConfig
from simulation.scenarios import ScenarioType
from simulation.simulator import MineGuardSimulator


class TestRiskEngine(unittest.TestCase):
    """Unit tests for the AI risk prediction engine."""

    def setUp(self):
        self.engine = RiskEngine()

    def test_01_normal_scenario_produces_low_risk(self):
        """Test that NORMAL scenario telemetry evaluates to LOW risk."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.NORMAL, random_seed=42))
        readings = sim.generate_readings(5)
        for r in readings:
            pred = self.engine.evaluate_reading(r)
            self.assertEqual(pred["risk_level"], "LOW")
            self.assertLess(pred["risk_score"], 30.0)
            self.assertGreaterEqual(pred["confidence"], 0.75)

    def test_02_heavy_rain_increases_risk(self):
        """Test that HEAVY_RAIN increases risk score as rain and pore pressure build."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.HEAVY_RAIN, random_seed=42))
        readings = sim.generate_readings(10)
        self.engine.reset()

        preds = [self.engine.evaluate_reading(r) for r in readings]
        initial_score = preds[0]["risk_score"]
        final_score = preds[-1]["risk_score"]

        self.assertGreater(final_score, initial_score)
        self.assertGreaterEqual(final_score, 30.0, "Heavy rain should reach at least MODERATE/HIGH risk")

    def test_03_progressive_instability_increases_risk(self):
        """Test that PROGRESSIVE_INSTABILITY progressively elevates risk."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.PROGRESSIVE_INSTABILITY, random_seed=42))
        readings = sim.generate_readings(10)
        self.engine.reset()

        preds = [self.engine.evaluate_reading(r) for r in readings]
        self.assertGreater(preds[-1]["risk_score"], preds[0]["risk_score"])
        self.assertIn(preds[-1]["risk_level"], ("HIGH", "CRITICAL"))

    def test_04_rapid_displacement_produates_high_or_critical_risk(self):
        """Test that RAPID_DISPLACEMENT rapidly triggers HIGH or CRITICAL risk."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.RAPID_DISPLACEMENT, random_seed=42))
        readings = sim.generate_readings(5)
        self.engine.reset()

        preds = [self.engine.evaluate_reading(r) for r in readings]
        final_pred = preds[-1]
        self.assertIn(final_pred["risk_level"], ("HIGH", "CRITICAL"))
        self.assertGreaterEqual(final_pred["risk_score"], 60.0)

    def test_05_high_vibration_increases_risk(self):
        """Test that HIGH_VIBRATION elevates risk score due to dynamic shock load."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.HIGH_VIBRATION, random_seed=42))
        readings = sim.generate_readings(5)
        self.engine.reset()

        preds = [self.engine.evaluate_reading(r) for r in readings]
        for p in preds:
            self.assertGreater(p["risk_score"], 25.0)

    def test_06_critical_combined_produces_critical_risk(self):
        """Test that CRITICAL_COMBINED triggers CRITICAL risk level."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.CRITICAL_COMBINED, random_seed=42))
        readings = sim.generate_readings(5)
        self.engine.reset()

        preds = [self.engine.evaluate_reading(r) for r in readings]
        final_pred = preds[-1]
        self.assertEqual(final_pred["risk_level"], "CRITICAL")
        self.assertGreaterEqual(final_pred["risk_score"], 80.0)

    def test_07_sensor_failure_reduces_confidence(self):
        """Test that SENSOR_FAILURE drops confidence and flags DEGRADED status."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.SENSOR_FAILURE, random_seed=42))
        readings = sim.generate_readings(3)
        self.engine.reset()

        for r in readings:
            pred = self.engine.evaluate_reading(r)
            self.assertEqual(pred["status"], "DEGRADED")
            self.assertLessEqual(pred["confidence"], 0.30)
            self.assertIn("compromised", pred["recommended_action"].lower())

    def test_08_recovery_decreases_risk_progressively(self):
        """Test that RECOVERY decreases risk score smoothly toward LOW."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.RECOVERY, random_seed=42))
        readings = sim.generate_readings(15)
        self.engine.reset()

        preds = [self.engine.evaluate_reading(r) for r in readings]
        initial_score = preds[0]["risk_score"]
        final_score = preds[-1]["risk_score"]

        self.assertLess(final_score, initial_score)
        self.assertLessEqual(final_score, 35.0)

    def test_09_risk_score_always_bounded(self):
        """Verify risk score is strictly in [0.0, 100.0] and confidence in [0.0, 1.0]."""
        for sc in ScenarioType:
            sim = MineGuardSimulator(SimulationConfig(scenario=sc, random_seed=99))
            readings = sim.generate_readings(10)
            self.engine.reset()
            for r in readings:
                pred = self.engine.evaluate_reading(r)
                self.assertGreaterEqual(pred["risk_score"], 0.0)
                self.assertLessEqual(pred["risk_score"], 100.0)
                self.assertGreaterEqual(pred["confidence"], 0.0)
                self.assertLessEqual(pred["confidence"], 1.0)
                self.assertFalse(math.isnan(pred["risk_score"]))
                self.assertFalse(math.isinf(pred["risk_score"]))

    def test_10_explainability_factors_present(self):
        """Verify that risk assessment includes factors attribution."""
        reading = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "timestamp": "2026-08-16T10:30:00Z",
            "sensors": {
                "displacement_mm": 35.0,
                "strain": 0.75,
                "pore_pressure_kpa": 65.0,
                "rainfall_mm": 50.0,
                "temperature_c": 28.0,
                "vibration_g": 1.5,
            },
        }
        pred = self.engine.evaluate_reading(reading)
        self.assertIsInstance(pred["factors"], list)
        self.assertGreater(len(pred["factors"]), 0)
        for f in pred["factors"]:
            self.assertIn("feature", f)
            self.assertIn("impact", f)
            self.assertIn(f["impact"], ("HIGH", "MEDIUM", "LOW"))


if __name__ == "__main__":
    unittest.main()
