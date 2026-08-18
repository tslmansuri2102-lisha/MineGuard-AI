"""
MineGuard AI — Simulation Scenarios Definition
Defines scenario types and physics profiles for all sensor simulation modes.
Strictly conforms to API_CONTRACT.md identifiers and rules.
"""

from enum import Enum
from typing import Dict, Any, Optional


class ScenarioType(str, Enum):
    """
    Recognized simulation scenarios with realistic time-dependent physics.
    """
    NORMAL = "NORMAL"
    HEAVY_RAIN = "HEAVY_RAIN"
    PROGRESSIVE_INSTABILITY = "PROGRESSIVE_INSTABILITY"
    RAPID_DISPLACEMENT = "RAPID_DISPLACEMENT"
    HIGH_VIBRATION = "HIGH_VIBRATION"
    CRITICAL_COMBINED = "CRITICAL_COMBINED"
    SENSOR_FAILURE = "SENSOR_FAILURE"
    RECOVERY = "RECOVERY"

    @classmethod
    def from_string(cls, name: str) -> "ScenarioType":
        """
        Parses a scenario name string into a ScenarioType enum, case-insensitively.
        Raises ValueError if unrecognized.
        """
        if not isinstance(name, str):
            raise ValueError(f"Scenario name must be a string, got {type(name).__name__}")
        
        normalized = name.strip().upper()
        for member in cls:
            if member.value == normalized:
                return member
        
        valid_names = [m.value for m in cls]
        raise ValueError(
            f"Unrecognized scenario '{name}'. Valid scenarios are: {', '.join(valid_names)}"
        )


class ScenarioProfile:
    """
    Scenario profile describing behavior, implementation status, and metadata.
    """
    def __init__(
        self,
        name: ScenarioType,
        description: str,
        is_implemented: bool = True,
        drift_rates: Optional[Dict[str, float]] = None,
        noise_scales: Optional[Dict[str, float]] = None,
    ):
        self.name = name
        self.description = description
        self.is_implemented = is_implemented
        self.drift_rates = drift_rates or {}
        self.noise_scales = noise_scales or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name.value,
            "description": self.description,
            "is_implemented": self.is_implemented,
        }


# Registry of all 8 scenario profiles — all fully implemented in Phase 2
SCENARIO_REGISTRY: Dict[ScenarioType, ScenarioProfile] = {
    ScenarioType.NORMAL: ScenarioProfile(
        name=ScenarioType.NORMAL,
        description="Normal mine operating conditions with gradual baseline creep and diurnal variations.",
        is_implemented=True,
    ),
    ScenarioType.HEAVY_RAIN: ScenarioProfile(
        name=ScenarioType.HEAVY_RAIN,
        description="Severe precipitation event causing elevated pore water pressure and surface saturation.",
        is_implemented=True,
    ),
    ScenarioType.PROGRESSIVE_INSTABILITY: ScenarioProfile(
        name=ScenarioType.PROGRESSIVE_INSTABILITY,
        description="Accelerating slope movement, increasing shear strain and warning signs.",
        is_implemented=True,
    ),
    ScenarioType.RAPID_DISPLACEMENT: ScenarioProfile(
        name=ScenarioType.RAPID_DISPLACEMENT,
        description="Sudden tertiary creep and high-velocity displacement indicating imminent failure.",
        is_implemented=True,
    ),
    ScenarioType.HIGH_VIBRATION: ScenarioProfile(
        name=ScenarioType.HIGH_VIBRATION,
        description="Intense seismic activity or nearby production blasting inducing high dynamic loads.",
        is_implemented=True,
    ),
    ScenarioType.CRITICAL_COMBINED: ScenarioProfile(
        name=ScenarioType.CRITICAL_COMBINED,
        description="Compound hazard combining extreme rainfall, high pore pressure, and accelerated displacement.",
        is_implemented=True,
    ),
    ScenarioType.SENSOR_FAILURE: ScenarioProfile(
        name=ScenarioType.SENSOR_FAILURE,
        description="Hardware anomaly, intermittent signal dropout, or flatlining sensor readings.",
        is_implemented=True,
    ),
    ScenarioType.RECOVERY: ScenarioProfile(
        name=ScenarioType.RECOVERY,
        description="Post-stabilization or engineered bench stabilization returning smoothly to equilibrium.",
        is_implemented=True,
    ),
}
