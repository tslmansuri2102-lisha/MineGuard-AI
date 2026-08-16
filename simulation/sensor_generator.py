"""
MineGuard AI — Sensor Data Generator
Generates realistic open-pit mine sensor telemetry with physics-based dynamic transitions.
Supports all 8 operational and hazard scenarios defined in API_CONTRACT.md.
"""

from datetime import datetime, timezone
import math
import random
from typing import Dict, Any, Optional

from simulation.config import DEFAULT_BASELINE_VALUES, REQUIRED_SENSOR_KEYS
from simulation.scenarios import ScenarioType, SCENARIO_REGISTRY


# Elevated starting conditions for RECOVERY scenario when initial_values are not specified
DEFAULT_RECOVERY_INITIAL_VALUES: Dict[str, float] = {
    "displacement_mm": 24.5,
    "strain": 0.78,
    "pore_pressure_kpa": 68.0,
    "rainfall_mm": 55.0,
    "temperature_c": 28.4,
    "vibration_g": 1.25,
}


class SensorGenerator:
    """
    Generates realistic, physically grounded mine sensor telemetry.
    Implements scenario-specific dynamic physics models, cross-sensor physical coupling
    (e.g., rainfall driving pore pressure, pore pressure driving displacement creep),
    and deterministic repeatability with random seeds.
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        initial_values: Optional[Dict[str, float]] = None,
        scenario: ScenarioType = ScenarioType.NORMAL,
    ):
        """
        Initialize the sensor generator.
        
        Args:
            seed: Optional integer seed for deterministic repeatability.
            initial_values: Optional initial sensor state.
            scenario: Active scenario type.
        """
        self.rng = random.Random(seed)
        self.scenario = scenario if isinstance(scenario, ScenarioType) else ScenarioType.from_string(scenario)
        
        # Initialize internal state
        self._state: Dict[str, float] = {}
        if initial_values is not None:
            init_source = initial_values
        elif self.scenario == ScenarioType.RECOVERY:
            init_source = DEFAULT_RECOVERY_INITIAL_VALUES
        elif self.scenario == ScenarioType.SENSOR_FAILURE:
            init_source = {k: 0.0 for k in REQUIRED_SENSOR_KEYS}
        else:
            init_source = DEFAULT_BASELINE_VALUES

        for key in REQUIRED_SENSOR_KEYS:
            self._state[key] = float(init_source.get(key, DEFAULT_BASELINE_VALUES[key]))
            
        # Target baselines for normal equilibrium
        self._baselines: Dict[str, float] = dict(DEFAULT_BASELINE_VALUES)
        
        # Step counter
        self.step_count = 0

    def set_state(self, values: Dict[str, float]) -> None:
        """Explicitly override the current sensor state."""
        for k, v in values.items():
            if k in REQUIRED_SENSOR_KEYS:
                self._state[k] = float(v)

    def get_state(self) -> Dict[str, float]:
        """Returns a copy of the current raw sensor state."""
        return dict(self._state)

    def generate_next_values(self, delta_time_seconds: float = 1.0) -> Dict[str, float]:
        """
        Advances the sensor physics by delta_time_seconds and generates the next values.
        Dispatches to scenario-specific physical evolution models.
        """
        self.step_count += 1
        dt = max(0.01, min(delta_time_seconds, 3600.0))  # Bound dt for numerical stability
        dt_factor = math.sqrt(dt)

        if self.scenario == ScenarioType.NORMAL:
            self._step_normal(dt, dt_factor)
        elif self.scenario == ScenarioType.HEAVY_RAIN:
            self._step_heavy_rain(dt, dt_factor)
        elif self.scenario == ScenarioType.PROGRESSIVE_INSTABILITY:
            self._step_progressive_instability(dt, dt_factor)
        elif self.scenario == ScenarioType.RAPID_DISPLACEMENT:
            self._step_rapid_displacement(dt, dt_factor)
        elif self.scenario == ScenarioType.HIGH_VIBRATION:
            self._step_high_vibration(dt, dt_factor)
        elif self.scenario == ScenarioType.CRITICAL_COMBINED:
            self._step_critical_combined(dt, dt_factor)
        elif self.scenario == ScenarioType.SENSOR_FAILURE:
            self._step_sensor_failure(dt, dt_factor)
        elif self.scenario == ScenarioType.RECOVERY:
            self._step_recovery(dt, dt_factor)
        else:
            self._step_normal(dt, dt_factor)

        # Enforce physical non-negativity constraints
        self._state["displacement_mm"] = max(0.0, self._state["displacement_mm"])
        self._state["strain"] = max(0.0, self._state["strain"])
        self._state["pore_pressure_kpa"] = max(0.0, self._state["pore_pressure_kpa"])
        self._state["rainfall_mm"] = max(0.0, self._state["rainfall_mm"])
        self._state["vibration_g"] = max(0.0, self._state["vibration_g"])

        # Return formatted values rounded to 2 decimal places for clean JSON serialization
        return {
            "displacement_mm": round(self._state["displacement_mm"], 2),
            "strain": round(self._state["strain"], 2),
            "pore_pressure_kpa": round(self._state["pore_pressure_kpa"], 2),
            "rainfall_mm": round(self._state["rainfall_mm"], 2),
            "temperature_c": round(self._state["temperature_c"], 2),
            "vibration_g": round(self._state["vibration_g"], 2),
        }

    # 1. NORMAL SCENARIO
    def _step_normal(self, dt: float, dt_factor: float) -> None:
        """Baseline mine conditions with gradual micro-creep and diurnal variations."""
        # Displacement: micro creep + minor noise
        disp_drift = 0.005 * dt
        disp_noise = self.rng.gauss(0, 0.015) * dt_factor
        self._state["displacement_mm"] += disp_drift + disp_noise

        # Strain: correlates slightly with displacement
        strain_target = self._baselines["strain"] + (self._state["displacement_mm"] - self._baselines["displacement_mm"]) * 0.002
        strain_pull = 0.05 * (strain_target - self._state["strain"]) * dt
        strain_noise = self.rng.gauss(0, 0.001) * dt_factor
        self._state["strain"] += strain_pull + strain_noise

        # Pore pressure: mean-reverting around baseline
        pore_pull = 0.08 * (self._baselines["pore_pressure_kpa"] - self._state["pore_pressure_kpa"]) * dt
        pore_noise = self.rng.gauss(0, 0.15) * dt_factor
        self._state["pore_pressure_kpa"] += pore_pull + pore_noise

        # Rainfall: baseline light fluctuation
        rain_pull = 0.1 * (self._baselines["rainfall_mm"] - self._state["rainfall_mm"]) * dt
        rain_noise = self.rng.gauss(0, 0.05) * dt_factor
        self._state["rainfall_mm"] += rain_pull + rain_noise

        # Temperature: ambient drift
        temp_pull = 0.03 * (self._baselines["temperature_c"] - self._state["temperature_c"]) * dt
        temp_noise = self.rng.gauss(0, 0.08) * dt_factor
        self._state["temperature_c"] += temp_pull + temp_noise

        # Vibration: ambient mining noise
        vib_pull = 0.2 * (self._baselines["vibration_g"] - self._state["vibration_g"]) * dt
        vib_noise = self.rng.gauss(0, 0.01) * dt_factor
        self._state["vibration_g"] += vib_pull + vib_noise

    # 2. HEAVY_RAIN SCENARIO
    def _step_heavy_rain(self, dt: float, dt_factor: float) -> None:
        """Gradual accumulation of heavy rainfall driving pore pressure and moderate slope creep."""
        # Rainfall increases steadily up to extreme precipitation bounds (~100 mm)
        rain_increase = 4.8 * dt + self.rng.gauss(0, 0.12) * dt_factor
        self._state["rainfall_mm"] = min(120.0, self._state["rainfall_mm"] + rain_increase)

        # Pore water pressure rises proportionally to rainfall infiltration
        pore_influx = (0.05 * (self._state["rainfall_mm"] - self._baselines["rainfall_mm"]) + 0.8) * dt
        pore_noise = self.rng.gauss(0, 0.15) * dt_factor
        self._state["pore_pressure_kpa"] = min(100.0, self._state["pore_pressure_kpa"] + pore_influx + pore_noise)

        # Displacement increases moderately as elevated pore pressure reduces effective shear stress
        excess_pore = max(0.0, self._state["pore_pressure_kpa"] - self._baselines["pore_pressure_kpa"])
        disp_rate = (0.12 + 0.008 * excess_pore) * dt
        disp_noise = self.rng.gauss(0, 0.02) * dt_factor
        self._state["displacement_mm"] += disp_rate + disp_noise

        # Strain responds smoothly to displacement
        strain_target = self._baselines["strain"] + (self._state["displacement_mm"] - self._baselines["displacement_mm"]) * 0.015
        strain_pull = 0.1 * (strain_target - self._state["strain"]) * dt
        self._state["strain"] += strain_pull + self.rng.gauss(0, 0.001) * dt_factor

        # Temperature slightly drops during heavy precipitation storm
        temp_target = 22.0
        temp_pull = 0.05 * (temp_target - self._state["temperature_c"]) * dt
        self._state["temperature_c"] += temp_pull + self.rng.gauss(0, 0.05) * dt_factor

        # Vibration remains approximately normal background
        vib_pull = 0.15 * (self._baselines["vibration_g"] - self._state["vibration_g"]) * dt
        self._state["vibration_g"] += vib_pull + self.rng.gauss(0, 0.015) * dt_factor

    # 3. PROGRESSIVE_INSTABILITY SCENARIO
    def _step_progressive_instability(self, dt: float, dt_factor: float) -> None:
        """Progressive secondary-to-tertiary creep showing gradual destabilization over time."""
        # Accelerating displacement rate over steps
        step_factor = min(self.step_count, 50)
        disp_rate = (0.75 + 0.12 * step_factor) * dt
        disp_noise = self.rng.gauss(0, 0.03) * dt_factor
        self._state["displacement_mm"] += disp_rate + disp_noise

        # Strain increases consistently and proportionally with displacement
        strain_target = self._baselines["strain"] + (self._state["displacement_mm"] - self._baselines["displacement_mm"]) * 0.022
        strain_pull = 0.15 * (strain_target - self._state["strain"]) * dt
        self._state["strain"] += strain_pull + self.rng.gauss(0, 0.002) * dt_factor

        # Pore pressure increases moderately
        pore_rate = 0.45 * dt + self.rng.gauss(0, 0.1) * dt_factor
        self._state["pore_pressure_kpa"] = min(70.0, self._state["pore_pressure_kpa"] + pore_rate)

        # Rainfall remains normal baseline
        rain_pull = 0.1 * (self._baselines["rainfall_mm"] - self._state["rainfall_mm"]) * dt
        self._state["rainfall_mm"] += rain_pull + self.rng.gauss(0, 0.04) * dt_factor

        # Vibration increases slightly due to acoustic emissions / rock micro-fracturing
        vib_target = min(0.40, self._baselines["vibration_g"] + 0.015 * step_factor)
        vib_pull = 0.1 * (vib_target - self._state["vibration_g"]) * dt
        self._state["vibration_g"] += vib_pull + self.rng.gauss(0, 0.01) * dt_factor

        # Temperature ambient
        temp_pull = 0.03 * (self._baselines["temperature_c"] - self._state["temperature_c"]) * dt
        self._state["temperature_c"] += temp_pull + self.rng.gauss(0, 0.05) * dt_factor

    # 4. RAPID_DISPLACEMENT SCENARIO
    def _step_rapid_displacement(self, dt: float, dt_factor: float) -> None:
        """Fast high-velocity tertiary displacement representing imminent slope collapse."""
        # High velocity displacement, accelerating significantly faster than progressive instability
        step_factor = min(self.step_count, 30)
        disp_rate = (4.8 + 0.9 * step_factor) * dt
        disp_noise = self.rng.gauss(0, 0.08) * dt_factor
        self._state["displacement_mm"] += disp_rate + disp_noise

        # Strain increases rapidly with large displacement
        strain_target = self._baselines["strain"] + (self._state["displacement_mm"] - self._baselines["displacement_mm"]) * 0.028
        strain_pull = 0.25 * (strain_target - self._state["strain"]) * dt
        self._state["strain"] += strain_pull + self.rng.gauss(0, 0.005) * dt_factor

        # Pore pressure remains moderately elevated
        pore_rate = 0.3 * dt + self.rng.gauss(0, 0.1) * dt_factor
        self._state["pore_pressure_kpa"] = min(65.0, self._state["pore_pressure_kpa"] + pore_rate)

        # Rainfall remains normal
        rain_pull = 0.1 * (self._baselines["rainfall_mm"] - self._state["rainfall_mm"]) * dt
        self._state["rainfall_mm"] += rain_pull + self.rng.gauss(0, 0.04) * dt_factor

        # Vibration elevated due to intense acoustic emissions from shearing rock
        vib_target = min(0.85, 0.45 + 0.04 * step_factor)
        vib_pull = 0.2 * (vib_target - self._state["vibration_g"]) * dt
        self._state["vibration_g"] += vib_pull + self.rng.gauss(0, 0.02) * dt_factor

        # Temperature ambient
        temp_pull = 0.03 * (self._baselines["temperature_c"] - self._state["temperature_c"]) * dt
        self._state["temperature_c"] += temp_pull + self.rng.gauss(0, 0.05) * dt_factor

    # 5. HIGH_VIBRATION SCENARIO
    def _step_high_vibration(self, dt: float, dt_factor: float) -> None:
        """Intense seismic or heavy blasting vibration with dynamic oscillation."""
        # Vibration significantly elevated (1.8 to 3.2 g) with cyclic blast shockwaves
        wave = 0.5 * math.sin(1.4 * self.step_count)
        target_vib = 2.2 + wave
        vib_pull = 0.4 * (target_vib - self._state["vibration_g"]) * dt
        vib_noise = self.rng.gauss(0, 0.12) * dt_factor
        self._state["vibration_g"] = max(1.2, self._state["vibration_g"] + vib_pull + vib_noise)

        # Displacement increases slightly from dynamic cyclic shake
        disp_rate = 0.06 * dt + self.rng.gauss(0, 0.015) * dt_factor
        self._state["displacement_mm"] += disp_rate

        # Strain slightly elevated
        strain_target = 0.26
        strain_pull = 0.1 * (strain_target - self._state["strain"]) * dt
        self._state["strain"] += strain_pull + self.rng.gauss(0, 0.002) * dt_factor

        # Rainfall and pore pressure remain near normal baseline
        pore_pull = 0.1 * (self._baselines["pore_pressure_kpa"] - self._state["pore_pressure_kpa"]) * dt
        self._state["pore_pressure_kpa"] += pore_pull + self.rng.gauss(0, 0.1) * dt_factor

        rain_pull = 0.1 * (self._baselines["rainfall_mm"] - self._state["rainfall_mm"]) * dt
        self._state["rainfall_mm"] += rain_pull + self.rng.gauss(0, 0.05) * dt_factor

        # Temperature ambient
        temp_pull = 0.03 * (self._baselines["temperature_c"] - self._state["temperature_c"]) * dt
        self._state["temperature_c"] += temp_pull + self.rng.gauss(0, 0.05) * dt_factor

    # 6. CRITICAL_COMBINED SCENARIO
    def _step_critical_combined(self, dt: float, dt_factor: float) -> None:
        """Compound multi-hazard scenario combining extreme rainfall, high pore pressure, displacement, and vibration."""
        step_factor = min(self.step_count, 40)

        # High rainfall surge
        rain_rate = 5.2 * dt + self.rng.gauss(0, 0.15) * dt_factor
        self._state["rainfall_mm"] = min(120.0, self._state["rainfall_mm"] + rain_rate)

        # High pore pressure surge
        pore_rate = (3.2 + 0.04 * (self._state["rainfall_mm"] - self._baselines["rainfall_mm"])) * dt
        self._state["pore_pressure_kpa"] = min(95.0, self._state["pore_pressure_kpa"] + pore_rate + self.rng.gauss(0, 0.2) * dt_factor)

        # Accelerating displacement surge
        disp_rate = (2.8 + 0.4 * step_factor) * dt
        self._state["displacement_mm"] += disp_rate + self.rng.gauss(0, 0.06) * dt_factor

        # High strain surge
        strain_target = self._baselines["strain"] + (self._state["displacement_mm"] - self._baselines["displacement_mm"]) * 0.025
        strain_pull = 0.2 * (strain_target - self._state["strain"]) * dt
        self._state["strain"] += strain_pull + self.rng.gauss(0, 0.004) * dt_factor

        # High vibration surge (seismic activity / collapsing mass)
        vib_target = min(2.5, 1.2 + 0.06 * step_factor)
        vib_pull = 0.25 * (vib_target - self._state["vibration_g"]) * dt
        self._state["vibration_g"] += vib_pull + self.rng.gauss(0, 0.03) * dt_factor

        # Temperature stormy ambient
        temp_target = 23.0
        temp_pull = 0.04 * (temp_target - self._state["temperature_c"]) * dt
        self._state["temperature_c"] += temp_pull + self.rng.gauss(0, 0.05) * dt_factor

    # 7. SENSOR_FAILURE SCENARIO
    def _step_sensor_failure(self, dt: float, dt_factor: float) -> None:
        """
        Hardware malfunction: flatlines to zero-variance 0.0 across channels.
        Fully conforms to API_CONTRACT.md schema (finite numeric, non-negative, valid JSON).
        """
        for key in REQUIRED_SENSOR_KEYS:
            self._state[key] = 0.0

    # 8. RECOVERY SCENARIO
    def _step_recovery(self, dt: float, dt_factor: float) -> None:
        """Smoothly returns from elevated hazard values toward normal equilibrium baselines."""
        decay_rate = 0.20 * dt  # Exponential decay speed toward baseline

        # Smoothly relax each sensor toward normal baseline
        for key in ("pore_pressure_kpa", "rainfall_mm", "vibration_g", "temperature_c"):
            delta = self._baselines[key] - self._state[key]
            noise = self.rng.gauss(0, 0.02) * dt_factor
            self._state[key] += delta * decay_rate + noise

        # Strain relaxes toward baseline as rock pressure relieves
        strain_delta = self._baselines["strain"] - self._state["strain"]
        self._state["strain"] += strain_delta * (decay_rate * 0.8) + self.rng.gauss(0, 0.001) * dt_factor

        # Displacement creep decelerates and stabilizes toward post-mitigation stable state
        disp_delta = self._baselines["displacement_mm"] - self._state["displacement_mm"]
        self._state["displacement_mm"] += disp_delta * (decay_rate * 0.5) + self.rng.gauss(0, 0.01) * dt_factor
