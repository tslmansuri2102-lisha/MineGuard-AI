"""
MineGuard AI — Simulation Configuration
Handles simulation parameters, defaults, and input validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Dict, Optional, Union, Any

from simulation.scenarios import ScenarioType


# Standard realistic baseline values for open-pit mine sensors under NORMAL conditions
DEFAULT_BASELINE_VALUES: Dict[str, float] = {
    "displacement_mm": 4.2,
    "strain": 0.21,
    "pore_pressure_kpa": 31.5,
    "rainfall_mm": 3.2,
    "temperature_c": 28.4,
    "vibration_g": 0.18,
}

REQUIRED_SENSOR_KEYS = (
    "displacement_mm",
    "strain",
    "pore_pressure_kpa",
    "rainfall_mm",
    "temperature_c",
    "vibration_g",
)


@dataclass
class SimulationConfig:
    """
    Configuration parameters for the MineGuard AI sensor simulator.
    """
    mine_id: str = "MINE-001"
    zone_id: str = "ZONE-003"
    sensor_id: str = "SENSOR-003"
    interval_seconds: float = 1.0
    random_seed: Optional[int] = None
    scenario: Union[ScenarioType, str] = ScenarioType.NORMAL
    initial_values: Optional[Dict[str, float]] = None
    num_readings: Optional[int] = None
    start_time: Optional[datetime] = None

    def __post_init__(self):
        # Normalize scenario if passed as string
        if isinstance(self.scenario, str):
            self.scenario = ScenarioType.from_string(self.scenario)
        elif not isinstance(self.scenario, ScenarioType):
            raise ValueError(
                f"Invalid scenario type: expected ScenarioType or str, got {type(self.scenario).__name__}"
            )
        
        # Set start_time default to UTC now if not provided
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)
        elif self.start_time.tzinfo is None:
            # Assume UTC if naive datetime was provided
            self.start_time = self.start_time.replace(tzinfo=timezone.utc)

        # Merge custom initial values over baseline if provided
        if self.initial_values is not None:
            merged = dict(DEFAULT_BASELINE_VALUES)
            merged.update(self.initial_values)
            self.initial_values = merged

        self.validate()

    def validate(self) -> None:
        """
        Validates configuration settings. Raises ValueError on any invalid setting.
        """
        # Identifiers validation
        if not isinstance(self.mine_id, str) or not self.mine_id.strip():
            raise ValueError("mine_id must be a non-empty string")
        if not isinstance(self.zone_id, str) or not self.zone_id.strip():
            raise ValueError("zone_id must be a non-empty string")
        if not isinstance(self.sensor_id, str) or not self.sensor_id.strip():
            raise ValueError("sensor_id must be a non-empty string")

        # Interval validation
        if not isinstance(self.interval_seconds, (int, float)) or isinstance(self.interval_seconds, bool):
            raise ValueError("interval_seconds must be a number")
        if not math.isfinite(self.interval_seconds) or self.interval_seconds <= 0:
            raise ValueError("interval_seconds must be a positive, finite number")

        # Random seed validation
        if self.random_seed is not None and not isinstance(self.random_seed, int):
            raise ValueError("random_seed must be an integer or None")

        # Num readings validation
        if self.num_readings is not None:
            if not isinstance(self.num_readings, int) or self.num_readings <= 0:
                raise ValueError("num_readings must be a positive integer or None")

        # Initial values validation (if explicitly provided)
        if self.initial_values is not None:
            if not isinstance(self.initial_values, dict):
                raise ValueError("initial_values must be a dictionary")

            for key in REQUIRED_SENSOR_KEYS:
                if key not in self.initial_values:
                    raise ValueError(f"initial_values is missing required sensor field '{key}'")
                val = self.initial_values[key]
                if not isinstance(val, (int, float)) or isinstance(val, bool):
                    raise ValueError(f"Initial value for '{key}' must be numeric, got {type(val).__name__}")
                if not math.isfinite(val):
                    raise ValueError(f"Initial value for '{key}' must be a finite number (got {val})")
                if key != "temperature_c" and val < 0:
                    raise ValueError(f"Initial value for '{key}' cannot be negative (got {val})")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        """
        Factory method to create SimulationConfig from a dictionary.
        """
        return cls(
            mine_id=data.get("mine_id", "MINE-001"),
            zone_id=data.get("zone_id", "ZONE-003"),
            sensor_id=data.get("sensor_id", "SENSOR-003"),
            interval_seconds=data.get("interval_seconds", 1.0),
            random_seed=data.get("random_seed"),
            scenario=data.get("scenario", ScenarioType.NORMAL),
            initial_values=data.get("initial_values"),
            num_readings=data.get("num_readings"),
            start_time=data.get("start_time"),
        )
