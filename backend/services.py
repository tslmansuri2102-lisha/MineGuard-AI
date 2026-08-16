"""
MineGuard AI — Simulation & Risk Service Layer
Coordinates simulation engine, AI risk prediction engine, alert dispatching, and prediction history.
"""

from collections import deque
from datetime import datetime, timezone
import threading
from typing import Any, Dict, List, Optional, Tuple

from ai.risk_engine import risk_engine
from backend.alerts import alert_service
from simulation.config import SimulationConfig
from simulation.scenarios import ScenarioType
from simulation.simulator import MineGuardSimulator
from simulation.validation import validate_reading, ValidationError


class SimulationService:
    """
    Service coordinating the MineGuard simulation engine, AI risk prediction engine,
    and alert dispatch system for REST and WebSocket consumers.
    """

    def __init__(self, max_history: int = 500):
        self._lock = threading.Lock()
        self._config: SimulationConfig = SimulationConfig(
            mine_id="MINE-001",
            zone_id="ZONE-003",
            sensor_id="SENSOR-003",
            scenario=ScenarioType.NORMAL,
            interval_seconds=1.0,
        )
        self._simulator: MineGuardSimulator = MineGuardSimulator(self._config)
        self._latest_reading: Optional[Dict[str, Any]] = None
        self._latest_prediction: Optional[Dict[str, Any]] = None
        self._prediction_history: deque[Dict[str, Any]] = deque(maxlen=max_history)
        self._is_running: bool = True
        self._step_count: int = 0

        # Generate initial baseline reading & prediction
        self._generate_initial_step()

    def _generate_initial_step(self) -> None:
        """Generates the initial reading and risk prediction upon startup/reset."""
        self._latest_reading = self._simulator.step()
        self._latest_prediction = risk_engine.evaluate_reading(self._latest_reading)
        self._prediction_history.append(dict(self._latest_prediction))
        self._step_count = 1

    def start_simulation(
        self,
        mine_id: str = "MINE-001",
        zone_id: str = "ZONE-003",
        sensor_id: str = "SENSOR-003",
        scenario: str = "NORMAL",
        interval: float = 1.0,
        seed: Optional[int] = None,
        initial_values: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Reconfigures and restarts the simulation and risk feature buffers.
        """
        scenario_enum = ScenarioType.from_string(scenario)

        with self._lock:
            self._config = SimulationConfig(
                mine_id=mine_id.strip(),
                zone_id=zone_id.strip(),
                sensor_id=sensor_id.strip(),
                scenario=scenario_enum,
                interval_seconds=interval,
                random_seed=seed,
                initial_values=initial_values,
            )
            self._simulator = MineGuardSimulator(self._config)
            risk_engine.reset(mine_id=mine_id, zone_id=zone_id, sensor_id=sensor_id)
            self._is_running = True
            self._generate_initial_step()

            return self.get_status()

    def stop_simulation(self) -> Dict[str, Any]:
        """Stops the active simulation loop."""
        with self._lock:
            self._is_running = False
            return self.get_status()

    def get_latest_reading(self) -> Dict[str, Any]:
        """Returns the most recent valid sensor reading."""
        with self._lock:
            if self._latest_reading is None:
                self._generate_initial_step()
            return dict(self._latest_reading)

    def get_latest_prediction(self) -> Dict[str, Any]:
        """Returns the most recent AI risk prediction."""
        with self._lock:
            if self._latest_prediction is None:
                self._generate_initial_step()
            return dict(self._latest_prediction)

    def generate_next_reading(self) -> Dict[str, Any]:
        """
        Advances the simulation engine by one step, runs risk prediction,
        dispatches alerts if applicable, and updates caches.
        """
        with self._lock:
            reading = self._simulator.step()
            validate_reading(reading)
            self._latest_reading = reading
            self._step_count += 1

            # Run AI risk prediction
            prediction = risk_engine.evaluate_reading(reading)
            self._latest_prediction = prediction
            self._prediction_history.append(dict(prediction))

            # Trigger alert check
            alert_service.evaluate_and_dispatch(prediction)

            return reading

    def generate_next_stream_payload(self) -> Dict[str, Any]:
        """
        Generates next step and returns combined telemetry + risk prediction payload.
        """
        reading = self.generate_next_reading()
        with self._lock:
            prediction = dict(self._latest_prediction)
        return {
            "telemetry": reading,
            "risk": prediction,
        }

    def evaluate_external_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates risk for an externally supplied sensor reading (e.g. from POST /api/v1/risk/predict).
        """
        validate_reading(reading)
        prediction = risk_engine.evaluate_reading(reading)
        with self._lock:
            self._prediction_history.append(dict(prediction))
            alert_service.evaluate_and_dispatch(prediction)
        return prediction

    def get_sensor_reading(self, mine_id: str, zone_id: str, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves current reading for a specified sensor."""
        with self._lock:
            if (
                self._config.mine_id == mine_id.strip()
                and self._config.zone_id == zone_id.strip()
                and self._config.sensor_id == sensor_id.strip()
            ):
                return dict(self._latest_reading)
            return None

    def get_sensor_risk(self, mine_id: str, zone_id: str, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves current risk prediction for a specified sensor."""
        with self._lock:
            if (
                self._config.mine_id == mine_id.strip()
                and self._config.zone_id == zone_id.strip()
                and self._config.sensor_id == sensor_id.strip()
            ):
                return dict(self._latest_prediction)
            return None

    def get_prediction_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns chronological history of risk predictions."""
        with self._lock:
            items = list(self._prediction_history)
            if limit is not None and limit > 0:
                items = items[-limit:]
            return [dict(p) for p in reversed(items)]

    def get_status(self) -> Dict[str, Any]:
        """Returns current operational status of the simulation service."""
        return {
            "status": "Simulation running" if self._is_running else "Simulation stopped",
            "is_running": self._is_running,
            "mine_id": self._config.mine_id,
            "zone_id": self._config.zone_id,
            "sensor_id": self._config.sensor_id,
            "scenario": self._config.scenario.value if hasattr(self._config.scenario, "value") else str(self._config.scenario),
            "interval_seconds": self._config.interval_seconds,
            "reading_count": self._step_count,
            "latest_reading": self._latest_reading,
        }

    @property
    def interval_seconds(self) -> float:
        return self._config.interval_seconds

    @property
    def is_running(self) -> bool:
        return self._is_running


# Global singleton simulation service
simulation_service = SimulationService()
