"""
MineGuard AI — Simulation Engine & Terminal Demo
Coordinates configuration, sensor physics generation, time advancement, and validation.
Produces payload structures strictly matching API_CONTRACT.md.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import sys
from typing import Any, Dict, Iterator, List, Optional

# Ensure repository root is on sys.path when executed directly
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Ensure stdout supports UTF-8 on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from simulation.config import SimulationConfig
from simulation.scenarios import ScenarioType
from simulation.sensor_generator import SensorGenerator
from simulation.validation import validate_reading


def format_utc_timestamp(dt: datetime) -> str:
    """Formats a datetime object as standard ISO 8601 UTC string ending in 'Z'."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class MineGuardSimulator:
    """
    Simulation Engine for generating realistic mine sensor readings.
    Reusable by Backend APIs, IoT layer, replay mechanisms, and automated testing.
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        """
        Initialize simulator with a given configuration.
        """
        self.config = config or SimulationConfig()
        self.generator = SensorGenerator(
            seed=self.config.random_seed,
            initial_values=self.config.initial_values,
            scenario=self.config.scenario,
        )
        self.current_time: datetime = self.config.start_time
        self.reading_count: int = 0

    def step(self) -> Dict[str, Any]:
        """
        Advances the simulation clock by config.interval_seconds and returns a valid reading.
        """
        # Advance simulation time
        self.current_time += timedelta(seconds=self.config.interval_seconds)
        self.reading_count += 1

        # Generate sensor values
        sensor_values = self.generator.generate_next_values(
            delta_time_seconds=self.config.interval_seconds
        )

        reading = {
            "mine_id": self.config.mine_id,
            "zone_id": self.config.zone_id,
            "sensor_id": self.config.sensor_id,
            "timestamp": format_utc_timestamp(self.current_time),
            "sensors": sensor_values,
        }

        # Validate strictly against API contract
        validate_reading(reading)

        return reading

    def generate_reading(self) -> Dict[str, Any]:
        """Alias for step(). Generates one reading."""
        return self.step()

    def generate_readings(self, n: int) -> List[Dict[str, Any]]:
        """Generates n consecutive simulation readings."""
        if n <= 0:
            return []
        return [self.step() for _ in range(n)]

    def stream(self, count: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """
        Generator yielding readings continuously or up to count readings.
        """
        produced = 0
        while count is None or produced < count:
            yield self.step()
            produced += 1

    @staticmethod
    def to_json(reading: Dict[str, Any], indent: Optional[int] = 2) -> str:
        """Converts a reading dictionary to a formatted JSON string."""
        return json.dumps(reading, indent=indent)


def format_step_display(step_num: int, reading: Dict[str, Any]) -> str:
    """
    Formats a single step sensor reading for terminal display.
    """
    sensors = reading["sensors"]
    lines = [
        f"STEP {step_num}",
        f"Displacement: {sensors['displacement_mm']:.1f} mm",
        f"Strain: {sensors['strain']:.2f}",
        f"Pore Pressure: {sensors['pore_pressure_kpa']:.1f} kPa",
        f"Rainfall: {sensors['rainfall_mm']:.1f} mm",
        f"Temperature: {sensors['temperature_c']:.1f} °C",
        f"Vibration: {sensors['vibration_g']:.2f} g",
        f"Timestamp: {reading['timestamp']}",
    ]
    return "\n".join(lines)


def run_cli():
    """CLI runner for terminal demo across all scenarios."""
    parser = argparse.ArgumentParser(
        description="MineGuard AI — Sensor Simulation Core (Terminal Demo)"
    )
    parser.add_argument("--mine", default="MINE-001", help="Mine identifier (e.g. MINE-001)")
    parser.add_argument("--zone", default="ZONE-003", help="Zone identifier (e.g. ZONE-003)")
    parser.add_argument("--sensor", default="SENSOR-003", help="Sensor identifier (e.g. SENSOR-003)")
    parser.add_argument(
        "--scenario",
        default="NORMAL",
        choices=[s.value for s in ScenarioType],
        help="Simulation scenario (NORMAL, HEAVY_RAIN, PROGRESSIVE_INSTABILITY, RAPID_DISPLACEMENT, HIGH_VIBRATION, CRITICAL_COMBINED, SENSOR_FAILURE, RECOVERY)",
    )
    parser.add_argument("--interval", type=float, default=1.0, help="Simulation step interval in seconds")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for deterministic generation")
    parser.add_argument("--steps", type=int, default=1, help="Number of reading steps to generate")
    parser.add_argument("--json", action="store_true", help="Output raw JSON payload instead of formatted text")

    args = parser.parse_args()

    config = SimulationConfig(
        mine_id=args.mine,
        zone_id=args.zone,
        sensor_id=args.sensor,
        interval_seconds=args.interval,
        random_seed=args.seed,
        scenario=args.scenario,
    )

    simulator = MineGuardSimulator(config)

    if not args.json:
        print(f"Mine: {config.mine_id}")
        print(f"Zone: {config.zone_id}")
        print(f"Sensor: {config.sensor_id}")
        print(f"Scenario: {args.scenario}")
        print()

    for i in range(args.steps):
        reading = simulator.step()
        if args.json:
            print(MineGuardSimulator.to_json(reading))
        else:
            if i > 0:
                print()
            print(format_step_display(i + 1, reading))

    if not args.json:
        print()
        print("Scenario completed successfully.")


if __name__ == "__main__":
    run_cli()
