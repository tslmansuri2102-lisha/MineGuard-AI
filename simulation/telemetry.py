"""
MineGuard AI — Telemetry Event Factory for Simulator
"""

import uuid
from datetime import datetime, timezone
from iot.sensor_schema import TelemetrySchema


def create_simulated_telemetry(
    step_idx: int,
    scenario_metrics: dict,
    zone_id: str = "ZONE-003",
    sensor_id: str = "SENSOR-003",
    latitude: float = 23.7954,
    longitude: float = 86.4304,
    battery_pct: float = 98.5
) -> TelemetrySchema:
    """
    Factory creating canonical TelemetrySchema object from physical simulation metrics.
    """
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    evt_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
    
    return TelemetrySchema(
        event_id=evt_id,
        timestamp=now_iso,
        sensor_id=sensor_id,
        zone_id=zone_id,
        latitude=latitude,
        longitude=longitude,
        vibration_g=scenario_metrics["vibration_g"],
        strain=scenario_metrics["strain"],
        displacement_mm=scenario_metrics["displacement_mm"],
        slope_velocity_mm_s=scenario_metrics["slope_velocity_mm_s"],
        temperature_c=scenario_metrics["temperature_c"],
        rainfall_mm=scenario_metrics["rainfall_mm"],
        rainfall_1h=scenario_metrics["rainfall_1h"],
        rainfall_6h=scenario_metrics["rainfall_6h"],
        battery_pct=battery_pct,
        human_report_count=0
    )
