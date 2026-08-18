"""
MineGuard AI — Simulation Package
Core simulation modules for realistic sensor data generation and validation.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.config import SimulationConfig, DEFAULT_BASELINE_VALUES
    from simulation.scenarios import ScenarioType, ScenarioProfile, SCENARIO_REGISTRY
    from simulation.sensor_generator import SensorGenerator
    from simulation.simulator import MineGuardSimulator
    from simulation.validation import validate_reading, is_valid_reading, ValidationError

__all__ = [
    "SimulationConfig",
    "DEFAULT_BASELINE_VALUES",
    "ScenarioType",
    "ScenarioProfile",
    "SCENARIO_REGISTRY",
    "SensorGenerator",
    "MineGuardSimulator",
    "validate_reading",
    "is_valid_reading",
    "ValidationError",
]


def __getattr__(name: str):
    if name in ("SimulationConfig", "DEFAULT_BASELINE_VALUES"):
        from simulation.config import SimulationConfig, DEFAULT_BASELINE_VALUES
        return locals()[name]
    if name in ("ScenarioType", "ScenarioProfile", "SCENARIO_REGISTRY"):
        from simulation.scenarios import ScenarioType, ScenarioProfile, SCENARIO_REGISTRY
        return locals()[name]
    if name == "SensorGenerator":
        from simulation.sensor_generator import SensorGenerator
        return SensorGenerator
    if name == "MineGuardSimulator":
        from simulation.simulator import MineGuardSimulator
        return MineGuardSimulator
    if name in ("validate_reading", "is_valid_reading", "ValidationError"):
        from simulation.validation import validate_reading, is_valid_reading, ValidationError
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
