"""
MineGuard AI — Rolling Window Temporal Feature Buffer Module
"""

import numpy as np
from typing import Dict, List
from datetime import datetime, timezone
from ml.utils import logger


class RollingWindowBuffer:
    """
    Maintains in-memory rolling time-series buffer per sensor/zone to calculate temporal features.
    """
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.buffers: Dict[str, List[dict]] = {}

    def add_telemetry(self, telemetry: dict) -> Dict[str, float]:
        """
        Incorporate new telemetry event into rolling window and compute temporal features.
        """
        sensor_id = telemetry["sensor_id"]
        if sensor_id not in self.buffers:
            self.buffers[sensor_id] = []
            
        buffer = self.buffers[sensor_id]
        buffer.append(telemetry)
        
        # Maintain window size limit
        if len(buffer) > self.window_size:
            buffer.pop(0)
            
        # Extract series
        vibs = [t["vibration_g"] for t in buffer]
        strains = [t["strain"] for t in buffer]
        disps = [t["displacement_mm"] for t in buffer]
        vels = [t["slope_velocity_mm_s"] for t in buffer]
        rains = [t["rainfall_mm"] for t in buffer]
        
        # Compute mean & std
        vib_curr = vibs[-1]
        vib_mean_1m = float(np.mean(vibs[-10:]))
        vib_mean_5m = float(np.mean(vibs))
        vib_std_1m = float(np.std(vibs[-10:])) if len(vibs) > 1 else 0.0
        
        vib_rate = float(vibs[-1] - vibs[-2]) if len(vibs) >= 2 else 0.0
        vib_accel = float(vibs[-1] - 2 * vibs[-2] + vibs[-3]) if len(vibs) >= 3 else 0.0
        
        strain_curr = strains[-1]
        strain_mean_1m = float(np.mean(strains[-10:]))
        strain_rate = float(strains[-1] - strains[-2]) if len(strains) >= 2 else 0.0
        
        disp_curr = disps[-1]
        disp_rate = float(disps[-1] - disps[-2]) if len(disps) >= 2 else 0.0
        
        vel_curr = vels[-1]
        vel_rate = float(vels[-1] - vels[-2]) if len(vels) >= 2 else 0.0
        
        # Simple statistical Z-score anomaly score
        anomaly_score = 0.0
        if vib_std_1m > 0.001:
            z_score = abs(vib_curr - vib_mean_1m) / vib_std_1m
            anomaly_score = float(min(1.0, z_score / 4.0))
            
        return {
            "vibration_current": float(vib_curr),
            "vibration_mean_1m": float(vib_mean_1m),
            "vibration_mean_5m": float(vib_mean_5m),
            "vibration_std_1m": float(vib_std_1m),
            "vibration_change_rate": float(vib_rate),
            "vibration_acceleration": float(vib_accel),
            "strain_current": float(strain_curr),
            "strain_mean_1m": float(strain_mean_1m),
            "strain_change_rate": float(strain_rate),
            "displacement_current": float(disp_curr),
            "displacement_change_rate": float(disp_rate),
            "slope_velocity_current": float(vel_curr),
            "slope_velocity_change_rate": float(vel_rate),
            "rainfall_1h": float(telemetry.get("rainfall_1h", float(np.sum(rains[-10:])))),
            "rainfall_6h": float(telemetry.get("rainfall_6h", float(np.sum(rains)))),
            "sensor_anomaly_score": float(anomaly_score)
        }
