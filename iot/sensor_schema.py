"""
MineGuard AI — IoT Sensor Telemetry Schema

Defines the standard telemetry format used by mine sensors
and validates incoming sensor readings before they enter
the MineGuard AI pipeline.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict


@dataclass
class SensorReading:
    """
    Standardized reading from a mine monitoring sensor.

    All physical sensors and the simulation layer should
    ultimately produce data in this format.
    """

    mine_id: str
    zone_id: str
    timestamp: str

    slope_angle: float
    displacement: float
    displacement_velocity: float
    displacement_acceleration: float
    strain: float
    pore_pressure: float
    rainfall: float
    temperature: float
    vibration: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert sensor reading to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SensorReading":
        """
        Create a SensorReading from a dictionary.

        Raises:
            ValueError: If required fields are missing or invalid.
        """

        required_fields = [
            "mine_id",
            "zone_id",
            "timestamp",
            "slope_angle",
            "displacement",
            "displacement_velocity",
            "displacement_acceleration",
            "strain",
            "pore_pressure",
            "rainfall",
            "temperature",
            "vibration",
        ]

        missing = [
            field for field in required_fields
            if field not in data
        ]

        if missing:
            raise ValueError(
                f"Missing required sensor fields: {missing}"
            )

        reading = cls(
            mine_id=str(data["mine_id"]),
            zone_id=str(data["zone_id"]),
            timestamp=str(data["timestamp"]),

            slope_angle=float(data["slope_angle"]),
            displacement=float(data["displacement"]),
            displacement_velocity=float(
                data["displacement_velocity"]
            ),
            displacement_acceleration=float(
                data["displacement_acceleration"]
            ),
            strain=float(data["strain"]),
            pore_pressure=float(data["pore_pressure"]),
            rainfall=float(data["rainfall"]),
            temperature=float(data["temperature"]),
            vibration=float(data["vibration"]),
        )

        reading.validate()

        return reading

    def validate(self) -> bool:
        """
        Validate sensor values against physically reasonable
        MineGuard operating ranges.
        """

        if not self.mine_id:
            raise ValueError("mine_id cannot be empty")

        if not self.zone_id:
            raise ValueError("zone_id cannot be empty")

        # Validate timestamp
        try:
            datetime.fromisoformat(
                self.timestamp.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(
                f"Invalid timestamp: {self.timestamp}"
            ) from exc

        # Physical/range validation
        ranges = {
            "slope_angle": (0.0, 90.0),
            "displacement": (0.0, 10000.0),
            "displacement_velocity": (0.0, 1000.0),
            "displacement_acceleration": (0.0, 1000.0),
            "strain": (0.0, 1000.0),
            "pore_pressure": (0.0, 10000.0),
            "rainfall": (0.0, 2000.0),
            "temperature": (-80.0, 80.0),
            "vibration": (0.0, 100.0),
        }

        for field, (minimum, maximum) in ranges.items():
            value = getattr(self, field)

            if value < minimum or value > maximum:
                raise ValueError(
                    f"{field}={value} is outside valid range "
                    f"[{minimum}, {maximum}]"
                )

        return True