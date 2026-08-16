"""
MineGuard AI — Simulation Core Automated Test Suite (Phase 1 & Phase 2)
Validates sensor simulation physics, scenario dynamic state transitions,
and strict adherence to API_CONTRACT.md.
"""

from datetime import datetime, timezone, timedelta
import json
import math
import unittest

from simulation.config import SimulationConfig, DEFAULT_BASELINE_VALUES
from simulation.scenarios import ScenarioType, SCENARIO_REGISTRY
from simulation.sensor_generator import SensorGenerator, DEFAULT_RECOVERY_INITIAL_VALUES
from simulation.simulator import MineGuardSimulator, format_utc_timestamp
from simulation.validation import (
    validate_reading,
    is_valid_reading,
    ValidationError,
    parse_iso8601_utc,
)


class TestSimulationCorePhase1And2(unittest.TestCase):
    """
    Comprehensive test suite for Phase 1 and Phase 2.
    """

    def setUp(self):
        """Set up standard configuration for tests."""
        self.default_config = SimulationConfig(
            mine_id="MINE-001",
            zone_id="ZONE-003",
            sensor_id="SENSOR-003",
            interval_seconds=1.0,
            random_seed=42,
            scenario=ScenarioType.NORMAL,
        )

    # -------------------------------------------------------------
    # PHASE 1 BASELINE TESTS
    # -------------------------------------------------------------

    def test_01_normal_sensor_reading_generation(self):
        """Test that NORMAL scenario generates realistic, valid readings."""
        sim = MineGuardSimulator(self.default_config)
        reading = sim.step()

        self.assertIsInstance(reading, dict)
        self.assertEqual(reading["mine_id"], "MINE-001")
        self.assertEqual(reading["zone_id"], "ZONE-003")
        self.assertEqual(reading["sensor_id"], "SENSOR-003")
        
        # Verify JSON serializability
        json_str = sim.to_json(reading)
        reloaded = json.loads(json_str)
        self.assertEqual(reloaded["mine_id"], "MINE-001")
        self.assertIn("sensors", reloaded)

    def test_02_required_fields_present(self):
        """Test that top-level required fields are present in every generated reading."""
        sim = MineGuardSimulator(self.default_config)
        reading = sim.step()

        required_keys = {"mine_id", "zone_id", "sensor_id", "timestamp", "sensors"}
        self.assertTrue(required_keys.issubset(reading.keys()))

    def test_03_exact_api_contract_sensor_field_names(self):
        """Verify that sensor field names match API_CONTRACT.md exactly."""
        sim = MineGuardSimulator(self.default_config)
        reading = sim.step()
        sensors = reading["sensors"]

        expected_sensor_keys = {
            "displacement_mm",
            "strain",
            "pore_pressure_kpa",
            "rainfall_mm",
            "temperature_c",
            "vibration_g",
        }
        self.assertEqual(set(sensors.keys()), expected_sensor_keys)

    def test_04_correct_data_types(self):
        """Test that identifiers are strings, timestamps are strings, and all sensor readings are numbers."""
        sim = MineGuardSimulator(self.default_config)
        reading = sim.step()

        self.assertIsInstance(reading["mine_id"], str)
        self.assertIsInstance(reading["zone_id"], str)
        self.assertIsInstance(reading["sensor_id"], str)
        self.assertIsInstance(reading["timestamp"], str)
        self.assertIsInstance(reading["sensors"], dict)

        for key, val in reading["sensors"].items():
            self.assertIsInstance(val, (int, float), f"Sensor {key} must be numeric, got {type(val)}")
            self.assertNotIsInstance(val, bool, f"Sensor {key} cannot be a boolean")

    def test_05_valid_utc_iso_timestamp(self):
        """Test that timestamps are valid ISO 8601 UTC format with proper progression."""
        start_time = datetime(2026, 8, 14, 10, 30, 0, tzinfo=timezone.utc)
        config = SimulationConfig(
            mine_id="MINE-001",
            zone_id="ZONE-003",
            sensor_id="SENSOR-003",
            interval_seconds=5.0,
            start_time=start_time,
        )
        sim = MineGuardSimulator(config)

        # Step 1
        r1 = sim.step()
        self.assertEqual(r1["timestamp"], "2026-08-14T10:30:05Z")
        dt1 = parse_iso8601_utc(r1["timestamp"])
        self.assertEqual(dt1.year, 2026)
        self.assertEqual(dt1.utcoffset(), timedelta(0))

        # Step 2
        r2 = sim.step()
        self.assertEqual(r2["timestamp"], "2026-08-14T10:30:10Z")

    def test_06_deterministic_generation_with_seed(self):
        """Test that identical seeds generate identical sensor reading sequences."""
        sim1 = MineGuardSimulator(SimulationConfig(random_seed=12345, scenario=ScenarioType.CRITICAL_COMBINED))
        sim2 = MineGuardSimulator(SimulationConfig(random_seed=12345, scenario=ScenarioType.CRITICAL_COMBINED))

        readings1 = sim1.generate_readings(10)
        readings2 = sim2.generate_readings(10)

        for idx, (rd1, rd2) in enumerate(zip(readings1, readings2)):
            self.assertEqual(
                rd1["sensors"],
                rd2["sensors"],
                f"Mismatch at step {idx} between identical seed runs",
            )

    def test_07_scenario_name_recognition_all_8(self):
        """Test that all 8 required scenario names are recognized and valid."""
        required_scenarios = [
            "NORMAL",
            "HEAVY_RAIN",
            "PROGRESSIVE_INSTABILITY",
            "RAPID_DISPLACEMENT",
            "HIGH_VIBRATION",
            "CRITICAL_COMBINED",
            "SENSOR_FAILURE",
            "RECOVERY",
        ]

        for sc_name in required_scenarios:
            enum_val = ScenarioType.from_string(sc_name)
            self.assertEqual(enum_val.value, sc_name)
            self.assertIn(enum_val, SCENARIO_REGISTRY)
            self.assertTrue(SCENARIO_REGISTRY[enum_val].is_implemented)

        # Verify case insensitivity
        self.assertEqual(ScenarioType.from_string("normal"), ScenarioType.NORMAL)
        self.assertEqual(ScenarioType.from_string(" heavy_rain "), ScenarioType.HEAVY_RAIN)

        # Verify unrecognized scenario raises ValueError
        with self.assertRaises(ValueError):
            ScenarioType.from_string("INVALID_SCENARIO")

    def test_08_invalid_configuration_handling(self):
        """Test that invalid configuration parameters raise clear ValueErrors."""
        with self.assertRaises(ValueError):
            SimulationConfig(interval_seconds=0)

        with self.assertRaises(ValueError):
            SimulationConfig(interval_seconds=-5.0)

        with self.assertRaises(ValueError):
            SimulationConfig(mine_id="")

        with self.assertRaises(ValueError):
            SimulationConfig(zone_id="   ")

        with self.assertRaises(ValueError):
            SimulationConfig(sensor_id="")

        with self.assertRaises(ValueError):
            SimulationConfig(scenario="UNKNOWN_SCENARIO")

        with self.assertRaises(ValueError):
            SimulationConfig(random_seed="not_an_int")

        with self.assertRaises(ValueError):
            SimulationConfig(initial_values={"rainfall_mm": -10.0})

    def test_09_no_nan_or_infinity_all_scenarios(self):
        """Test that 50 steps across EVERY scenario never produces NaN or infinite values."""
        for sc in ScenarioType:
            sim = MineGuardSimulator(SimulationConfig(interval_seconds=1.0, random_seed=777, scenario=sc))
            readings = sim.generate_readings(50)
            for i, rd in enumerate(readings):
                for sensor_name, val in rd["sensors"].items():
                    self.assertFalse(math.isnan(val), f"NaN in {sc.value}:{sensor_name} at step {i}")
                    self.assertFalse(math.isinf(val), f"Infinity in {sc.value}:{sensor_name} at step {i}")
                    self.assertTrue(math.isfinite(val), f"Non-finite value in {sc.value}:{sensor_name} at step {i}")

    def test_10_reading_validation_enforcement(self):
        """Test strict validation catches corruptions."""
        sim = MineGuardSimulator(self.default_config)
        valid_reading = sim.step()

        self.assertTrue(is_valid_reading(valid_reading))
        validate_reading(valid_reading)

        # Missing key
        bad1 = dict(valid_reading)
        del bad1["mine_id"]
        self.assertFalse(is_valid_reading(bad1))

        # Negative displacement
        bad2 = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "timestamp": "2026-08-14T10:30:00Z",
            "sensors": {
                "displacement_mm": -5.0,
                "strain": 0.81,
                "pore_pressure_kpa": 62.0,
                "rainfall_mm": 74.0,
                "temperature_c": 32.0,
                "vibration_g": 1.2,
            },
        }
        self.assertFalse(is_valid_reading(bad2))

        # NaN
        bad3 = {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "timestamp": "2026-08-14T10:30:00Z",
            "sensors": {
                "displacement_mm": float("nan"),
                "strain": 0.81,
                "pore_pressure_kpa": 62.0,
                "rainfall_mm": 74.0,
                "temperature_c": 32.0,
                "vibration_g": 1.2,
            },
        }
        self.assertFalse(is_valid_reading(bad3))

    # -------------------------------------------------------------
    # PHASE 2 SCENARIO DYNAMICS TESTS
    # -------------------------------------------------------------

    def test_11_multiple_simulation_steps_produce_changing_values(self):
        """Verify that dynamic simulation steps produce evolving values over time."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.HEAVY_RAIN, random_seed=100))
        readings = sim.generate_readings(5)
        
        # Check that rainfall changes across steps
        rainfall_values = [r["sensors"]["rainfall_mm"] for r in readings]
        self.assertEqual(len(rainfall_values), 5)
        # Should not be all identical
        self.assertGreater(len(set(rainfall_values)), 1)

    def test_12_heavy_rain_dynamics(self):
        """Test that HEAVY_RAIN increases rainfall and elevates pore water pressure."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.HEAVY_RAIN, random_seed=42))
        readings = sim.generate_readings(10)

        initial_rain = readings[0]["sensors"]["rainfall_mm"]
        final_rain = readings[-1]["sensors"]["rainfall_mm"]
        self.assertGreater(final_rain, initial_rain, "Rainfall must increase in HEAVY_RAIN")
        self.assertGreater(final_rain, 30.0, "Rainfall should reach significant levels over 10 steps")

        initial_pore = readings[0]["sensors"]["pore_pressure_kpa"]
        final_pore = readings[-1]["sensors"]["pore_pressure_kpa"]
        self.assertGreater(final_pore, initial_pore, "Pore pressure must increase in response to rain")

    def test_13_progressive_instability_dynamics(self):
        """Test that PROGRESSIVE_INSTABILITY increases displacement and strain progressively."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.PROGRESSIVE_INSTABILITY, random_seed=42))
        readings = sim.generate_readings(10)

        displacements = [r["sensors"]["displacement_mm"] for r in readings]
        strains = [r["sensors"]["strain"] for r in readings]

        # Monotonically or progressively increasing displacement
        self.assertGreater(displacements[-1], displacements[0] + 5.0)
        self.assertGreater(strains[-1], strains[0])

    def test_14_rapid_displacement_faster_than_progressive(self):
        """Test that RAPID_DISPLACEMENT increases displacement faster than PROGRESSIVE_INSTABILITY."""
        sim_prog = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.PROGRESSIVE_INSTABILITY, random_seed=42))
        sim_rapid = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.RAPID_DISPLACEMENT, random_seed=42))

        readings_prog = sim_prog.generate_readings(5)
        readings_rapid = sim_rapid.generate_readings(5)

        delta_disp_prog = readings_prog[-1]["sensors"]["displacement_mm"] - readings_prog[0]["sensors"]["displacement_mm"]
        delta_disp_rapid = readings_rapid[-1]["sensors"]["displacement_mm"] - readings_rapid[0]["sensors"]["displacement_mm"]

        self.assertGreater(
            delta_disp_rapid,
            delta_disp_prog * 2.0,
            f"Rapid displacement ({delta_disp_rapid}) must be significantly faster than progressive ({delta_disp_prog})",
        )

    def test_15_high_vibration_dynamics(self):
        """Test that HIGH_VIBRATION produces significantly higher vibration readings."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.HIGH_VIBRATION, random_seed=42))
        readings = sim.generate_readings(5)

        vibrations = [r["sensors"]["vibration_g"] for r in readings]
        for v in vibrations:
            self.assertGreaterEqual(v, 1.2, "Vibration in HIGH_VIBRATION must be significantly elevated (> 1.2 g)")

    def test_16_critical_combined_dynamics(self):
        """Test that CRITICAL_COMBINED exhibits multiple simultaneously elevated risk indicators."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.CRITICAL_COMBINED, random_seed=42))
        readings = sim.generate_readings(10)
        final_reading = readings[-1]["sensors"]

        # All key risk parameters should be elevated
        self.assertGreater(final_reading["displacement_mm"], 25.0, "Displacement must be elevated")
        self.assertGreater(final_reading["strain"], 0.6, "Strain must be elevated")
        self.assertGreater(final_reading["pore_pressure_kpa"], 50.0, "Pore pressure must be elevated")
        self.assertGreater(final_reading["rainfall_mm"], 35.0, "Rainfall must be elevated")
        self.assertGreater(final_reading["vibration_g"], 1.0, "Vibration must be elevated")

    def test_17_sensor_failure_contract_compliance(self):
        """Test that SENSOR_FAILURE flatlines cleanly while strictly conforming to API_CONTRACT.md."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.SENSOR_FAILURE, random_seed=42))
        readings = sim.generate_readings(5)

        for r in readings:
            # Must pass contract validation
            self.assertTrue(is_valid_reading(r))
            validate_reading(r)
            # All sensor readings are flatlined at 0.0
            for sensor_name, val in r["sensors"].items():
                self.assertEqual(val, 0.0, f"Sensor {sensor_name} should be flatlined at 0.0")

    def test_18_recovery_dynamics(self):
        """Test that RECOVERY smoothly decays elevated values back toward normal baselines."""
        sim = MineGuardSimulator(SimulationConfig(scenario=ScenarioType.RECOVERY, random_seed=42))
        readings = sim.generate_readings(15)

        initial = readings[0]["sensors"]
        final = readings[-1]["sensors"]

        # Pore pressure should decrease toward normal baseline (~31.5)
        self.assertLess(final["pore_pressure_kpa"], initial["pore_pressure_kpa"])
        # Rainfall should decrease toward normal baseline (~3.2)
        self.assertLess(final["rainfall_mm"], initial["rainfall_mm"])
        # Vibration should decrease toward normal baseline (~0.18)
        self.assertLess(final["vibration_g"], initial["vibration_g"])
        # Strain should decrease toward normal baseline (~0.21)
        self.assertLess(final["strain"], initial["strain"])

        # Final values should be close to normal baselines
        self.assertAlmostEqual(final["pore_pressure_kpa"], DEFAULT_BASELINE_VALUES["pore_pressure_kpa"], delta=15.0)
        self.assertAlmostEqual(final["rainfall_mm"], DEFAULT_BASELINE_VALUES["rainfall_mm"], delta=15.0)


if __name__ == "__main__":
    unittest.main()
