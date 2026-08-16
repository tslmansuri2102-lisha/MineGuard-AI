"""
MineGuard AI — Canonical IoT Telemetry Schema & Validation Rules
"""

from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class TelemetrySchema(BaseModel):
    """
    Canonical Telemetry Contract for MineGuard AI.
    Used by both physical IoT/ESP32 edge hardware and simulated telemetry streams.
    """
    event_id: str = Field(..., description="Unique event identifier (e.g., EVT-000001)")
    timestamp: str = Field(..., description="UTC ISO 8601 timestamp (e.g., 2026-08-14T10:30:00Z)")
    sensor_id: str = Field(..., description="Sensor unit identifier (e.g., SENSOR-003)")
    zone_id: str = Field(..., description="Mine zone identifier (e.g., ZONE-003)")
    
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 longitude")
    
    vibration_g: float = Field(..., ge=0.0, le=50.0, description="Peak particle acceleration in g")
    strain: float = Field(..., ge=0.0, le=100.0, description="Microstrain deformation ratio")
    displacement_mm: float = Field(..., ge=0.0, le=5000.0, description="Cumulative displacement in mm")
    slope_velocity_mm_s: float = Field(..., ge=0.0, le=1000.0, description="Slope movement velocity in mm/s")
    
    temperature_c: float = Field(..., ge=-50.0, le=80.0, description="Ambient/rock temperature in °C")
    rainfall_mm: float = Field(..., ge=0.0, le=500.0, description="Current precipitation intensity in mm")
    rainfall_1h: float = Field(0.0, ge=0.0, le=500.0, description="1-hour cumulative rainfall in mm")
    rainfall_6h: float = Field(0.0, ge=0.0, le=500.0, description="6-hour cumulative rainfall in mm")
    
    battery_pct: float = Field(100.0, ge=0.0, le=100.0, description="Sensor battery percentage")
    human_report_count: int = Field(0, ge=0, description="Auxiliary field observations count")

    @field_validator("timestamp")
    @classmethod
    def validate_utc_timestamp(cls, v: str) -> str:
        """Ensure timestamp is valid ISO 8601 string."""
        try:
            # Parse datetime
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception as e:
            raise ValueError(f"Invalid UTC ISO 8601 timestamp format: '{v}'. Error: {e}")

    def to_dict(self) -> dict:
        return self.model_dump()


def validate_raw_telemetry_dict(payload: dict) -> tuple[bool, Optional[TelemetrySchema], Optional[str]]:
    """
    Safely validate incoming telemetry payload without raising unhandled exceptions.
    
    Returns:
        tuple[bool, Optional[TelemetrySchema], Optional[str]]: (is_valid, schema_object, error_message)
    """
    try:
        schema_obj = TelemetrySchema(**payload)
        return True, schema_obj, None
    except Exception as err:
        return False, None, str(err)
