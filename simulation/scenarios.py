"""
MineGuard AI — Simulation Scenarios & Physical Trend Definitions
"""

import math
import random
from typing import Dict


class ScenarioGenerator:
    """
    Generates physically plausible temporal telemetry trends for specific mine bench risk scenarios.
    """
    SCENARIOS = ["NORMAL", "DEVELOPING_INSTABILITY", "HIGH_RISK", "CRITICAL_ROCKFALL"]

    def __init__(self, scenario: str = "NORMAL", seed: int = 42):
        if scenario.upper() not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Must be one of {self.SCENARIOS}")
        self.scenario = scenario.upper()
        self.seed = seed
        random.seed(seed)

    def generate_step(self, step_idx: int, total_steps: int = 60) -> Dict[str, float]:
        """
        Generate physically consistent telemetry metrics for a given time step.
        
        Args:
            step_idx (int): Current time step index (0 to total_steps).
            total_steps (int): Total steps in simulation run.
            
        Returns:
            dict: Sensor physical values.
        """
        t = min(max(step_idx / max(total_steps, 1), 0.0), 1.0)
        noise = random.gauss(0, 0.05)
        
        if self.scenario == "NORMAL":
            vibration = 0.10 + 0.05 * math.sin(t * 10) + random.uniform(-0.02, 0.02)
            strain = 0.20 + random.uniform(-0.02, 0.02)
            displacement = 2.0 + t * 0.5 + random.uniform(-0.1, 0.1)
            velocity = 0.002 + random.uniform(-0.0005, 0.0005)
            rainfall = max(0.0, random.uniform(0.0, 2.0))
            temp = 24.0 + random.uniform(-0.5, 0.5)

        elif self.scenario == "DEVELOPING_INSTABILITY":
            vibration = 0.30 + t * 1.2 + random.uniform(-0.05, 0.05)
            strain = 0.50 + t * 2.0 + random.uniform(-0.05, 0.05)
            displacement = 5.0 + t * 25.0 + random.uniform(-0.5, 0.5)
            velocity = 0.01 + t * 0.15 + random.uniform(-0.005, 0.005)
            rainfall = 10.0 + t * 30.0 + random.uniform(-1.0, 1.0)
            temp = 22.0 + random.uniform(-0.5, 0.5)

        elif self.scenario == "HIGH_RISK":
            vibration = 1.5 + (t ** 1.5) * 3.0 + random.uniform(-0.1, 0.1)
            strain = 2.5 + (t ** 1.5) * 4.5 + random.uniform(-0.1, 0.1)
            displacement = 30.0 + (t ** 2) * 60.0 + random.uniform(-1.0, 1.0)
            velocity = 0.15 + (t ** 1.5) * 0.8 + random.uniform(-0.02, 0.02)
            rainfall = 40.0 + t * 65.0 + random.uniform(-2.0, 2.0)
            temp = 18.0 + random.uniform(-0.5, 0.5)

        elif self.scenario == "CRITICAL_ROCKFALL":
            # Exponential acceleration curve matching tertiary creep slope failure
            exp_factor = math.exp(t * 2.5) / math.exp(2.5)
            vibration = 3.0 + exp_factor * 8.5 + random.uniform(-0.2, 0.2)
            strain = 5.0 + exp_factor * 12.0 + random.uniform(-0.2, 0.2)
            displacement = 80.0 + exp_factor * 220.0 + random.uniform(-2.0, 2.0)
            velocity = 1.0 + exp_factor * 12.0 + random.uniform(-0.1, 0.1)
            rainfall = 80.0 + t * 110.0 + random.uniform(-3.0, 3.0)
            temp = 15.0 + random.uniform(-0.5, 0.5)

        return {
            "vibration_g": max(0.0, float(round(vibration, 3))),
            "strain": max(0.0, float(round(strain, 3))),
            "displacement_mm": max(0.0, float(round(displacement, 2))),
            "slope_velocity_mm_s": max(0.0, float(round(velocity, 4))),
            "rainfall_mm": max(0.0, float(round(rainfall, 1))),
            "rainfall_1h": max(0.0, float(round(rainfall * 0.8, 1))),
            "rainfall_6h": max(0.0, float(round(rainfall * 2.5, 1))),
            "temperature_c": float(round(temp, 1)),
        }
