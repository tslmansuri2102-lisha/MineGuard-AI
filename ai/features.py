"""
MineGuard AI — Feature Extraction Engine
Extracts geotechnical and kinematic features from raw sensor telemetry.
Calculates displacement velocity, acceleration, pore pressure rates, and composite stability indicators.
"""

from collections import deque
from datetime import datetime
import math
from typing import Any, Dict, List, Optional, Tuple

from simulation.validation import parse_iso8601_utc


class FeatureExtractor:
    """
    Stateful feature extraction buffer for computing temporal rates and kinematic indices.
    Maintains a sliding window of historical readings per sensor.
    """

    def __init__(self, window_size: int = 10):
        self.window_size = max(2, window_size)
        self._history: Dict[str, deque] = {}

    def _get_sensor_key(self, mine_id: str, zone_id: str, sensor_id: str) -> str:
        return f"{mine_id.strip()}:{zone_id.strip()}:{sensor_id.strip()}"

    def extract(self, reading: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Extracts raw and derived features from a sensor reading.
        
        Returns:
            Tuple of (features_dict, metadata_dict):
                features_dict: Numerical dictionary for the risk model.
                metadata_dict: Quality indicators and status flags.
        """
        mine_id = reading.get("mine_id", "UNKNOWN")
        zone_id = reading.get("zone_id", "UNKNOWN")
        sensor_id = reading.get("sensor_id", "UNKNOWN")
        timestamp_str = reading.get("timestamp", "")
        sensors = reading.get("sensors", {})

        # Parse timestamp safely
        try:
            current_dt = parse_iso8601_utc(timestamp_str)
        except Exception:
            current_dt = datetime.now()

        # Extract raw sensor values with safe defaults
        disp = float(sensors.get("displacement_mm", 0.0))
        strain = float(sensors.get("strain", 0.0))
        pore = float(sensors.get("pore_pressure_kpa", 0.0))
        rain = float(sensors.get("rainfall_mm", 0.0))
        temp = float(sensors.get("temperature_c", 0.0))
        vib = float(sensors.get("vibration_g", 0.0))

        # Check for sensor failure / zeroed telemetry dropout
        is_zero_signal = (
            abs(disp) < 1e-6
            and abs(strain) < 1e-6
            and abs(pore) < 1e-6
            and abs(rain) < 1e-6
            and abs(vib) < 1e-6
            and abs(temp) < 1e-6
        )

        sensor_key = self._get_sensor_key(mine_id, zone_id, sensor_id)
        if sensor_key not in self._history:
            self._history[sensor_key] = deque(maxlen=self.window_size)

        hist = self._history[sensor_key]

        # Calculate temporal rates if previous readings exist
        disp_rate = 0.0
        disp_accel = 0.0
        pore_rate = 0.0
        has_history = len(hist) > 0

        if has_history:
            prev_reading, prev_dt, prev_disp_rate = hist[-1]
            dt_seconds = max(0.01, (current_dt - prev_dt).total_seconds())

            prev_disp = float(prev_reading.get("sensors", {}).get("displacement_mm", disp))
            prev_pore = float(prev_reading.get("sensors", {}).get("pore_pressure_kpa", pore))

            # First derivative: Displacement rate (mm/s)
            raw_disp_rate = (disp - prev_disp) / dt_seconds
            disp_rate = max(0.0, raw_disp_rate) if math.isfinite(raw_disp_rate) else 0.0

            # Second derivative: Displacement acceleration (mm/s^2)
            raw_disp_accel = (disp_rate - prev_disp_rate) / dt_seconds
            disp_accel = raw_disp_accel if math.isfinite(raw_disp_accel) else 0.0

            # Pore pressure rate (kPa/s)
            raw_pore_rate = (pore - prev_pore) / dt_seconds
            pore_rate = raw_pore_rate if math.isfinite(raw_pore_rate) else 0.0
        else:
            prev_disp_rate = 0.0

        # Store current reading in history
        hist.append((reading, current_dt, disp_rate))

        # Derived geotechnical indices
        vibration_severity = max(0.0, vib / 0.18) if 0.18 > 0 else 1.0
        strain_severity = max(0.0, strain / 0.21) if 0.21 > 0 else 1.0
        rainfall_intensity = max(0.0, rain)

        # Composite slope instability index
        combined_instability_index = (
            (disp / 4.2) * 0.35
            + (pore / 31.5) * 0.25
            + (vib / 0.18) * 0.20
            + (strain / 0.21) * 0.20
        )

        features = {
            "displacement_mm": disp,
            "displacement_rate": round(disp_rate, 4),
            "displacement_accel": round(disp_accel, 4),
            "strain": strain,
            "strain_severity": round(strain_severity, 3),
            "pore_pressure_kpa": pore,
            "pore_pressure_rate": round(pore_rate, 4),
            "rainfall_mm": rain,
            "rainfall_intensity": round(rainfall_intensity, 2),
            "temperature_c": temp,
            "vibration_g": vib,
            "vibration_severity": round(vibration_severity, 3),
            "combined_instability_index": round(combined_instability_index, 3),
        }

        # Guard: Ensure all values are strictly finite
        for k, v in features.items():
            if not math.isfinite(v):
                features[k] = 0.0

        metadata = {
            "has_history": has_history,
            "history_length": len(hist),
            "is_zero_signal": is_zero_signal,
        }

        return features, metadata

    def reset(self, mine_id: Optional[str] = None, zone_id: Optional[str] = None, sensor_id: Optional[str] = None) -> None:
        """Resets the history buffer for specific sensor or all sensors."""
        if mine_id and zone_id and sensor_id:
            key = self._get_sensor_key(mine_id, zone_id, sensor_id)
            self._history.pop(key, None)
        else:
            self._history.clear()
