"""
MineGuard AI — Backend Pydantic Models
Defines request and response schemas strictly adhering to API_CONTRACT.md.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="ok", description="Service health status", example="ok")
    service: str = Field(
        default="MineGuard AI backend",
        description="Service description",
        example="MineGuard AI backend",
    )


class SensorReadingValues(BaseModel):
    """Raw sensor readings structure matching API_CONTRACT.md exactly."""
    displacement_mm: float = Field(
        ...,
        ge=0.0,
        description="Slope surface displacement in millimeters",
        example=24.2,
    )
    strain: float = Field(
        ...,
        ge=0.0,
        description="Dimensionless rock shear strain",
        example=0.81,
    )
    pore_pressure_kpa: float = Field(
        ...,
        ge=0.0,
        description="Pore water pressure in kilopascals",
        example=62.0,
    )
    rainfall_mm: float = Field(
        ...,
        ge=0.0,
        description="Precipitation accumulation in millimeters",
        example=74.0,
    )
    temperature_c: float = Field(
        ...,
        description="Ambient bench temperature in degrees Celsius",
        example=32.0,
    )
    vibration_g: float = Field(
        ...,
        ge=0.0,
        description="Vibration amplitude in g-force",
        example=1.2,
    )


class SensorTelemetryPayload(BaseModel):
    """Complete sensor reading payload structure conforming to API_CONTRACT.md."""
    mine_id: str = Field(..., description="Unique mine identifier", example="MINE-001")
    zone_id: str = Field(..., description="Unique zone identifier", example="ZONE-003")
    sensor_id: str = Field(..., description="Unique sensor identifier", example="SENSOR-003")
    timestamp: str = Field(
        ...,
        description="UTC ISO 8601 timestamp with trailing 'Z'",
        example="2026-08-14T10:30:00Z",
    )
    sensors: SensorReadingValues = Field(..., description="Sensor measurements dictionary")


class SimulationStartRequest(BaseModel):
    """Request body to configure and launch sensor simulation."""
    mine_id: str = Field(default="MINE-001", description="Target Mine ID", example="MINE-001")
    zone_id: str = Field(default="ZONE-003", description="Target Zone ID", example="ZONE-003")
    sensor_id: str = Field(default="SENSOR-003", description="Target Sensor ID", example="SENSOR-003")
    scenario: str = Field(
        default="NORMAL",
        description="Simulation scenario (NORMAL, HEAVY_RAIN, PROGRESSIVE_INSTABILITY, RAPID_DISPLACEMENT, HIGH_VIBRATION, CRITICAL_COMBINED, SENSOR_FAILURE, RECOVERY)",
        example="HEAVY_RAIN",
    )
    interval: float = Field(
        default=1.0,
        gt=0.0,
        description="Simulation interval in seconds between readings",
        example=1.0,
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional seed for deterministic random numbers",
        example=42,
    )


class SimulationStatusResponse(BaseModel):
    """Current status of the simulation service."""
    status: str = Field(..., description="Service status message", example="Simulation running")
    is_running: bool = Field(..., description="Whether simulation is active", example=True)
    mine_id: str = Field(..., example="MINE-001")
    zone_id: str = Field(..., example="ZONE-003")
    sensor_id: str = Field(..., example="SENSOR-003")
    scenario: str = Field(..., example="HEAVY_RAIN")
    interval_seconds: float = Field(..., example=1.0)
    reading_count: int = Field(..., example=5)
    latest_reading: Optional[SensorTelemetryPayload] = None


class ContributingFactor(BaseModel):
    """Explaining factor with impact rating."""
    feature: str = Field(..., description="Name of contributing sensor/kinematic feature", example="displacement_rate")
    impact: str = Field(..., description="Impact severity (HIGH, MEDIUM, LOW)", example="HIGH")


class RiskPredictionPayload(BaseModel):
    """Geotechnical rockfall/slope failure risk assessment prediction."""
    mine_id: str = Field(..., example="MINE-001")
    zone_id: str = Field(..., example="ZONE-003")
    sensor_id: str = Field(..., example="SENSOR-003")
    timestamp: str = Field(..., example="2026-08-16T10:30:00Z")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk score from 0 to 100", example=84.2)
    risk_level: str = Field(..., description="Categorical risk level (LOW, MODERATE, HIGH, CRITICAL)", example="CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence / data quality score", example=0.92)
    status: str = Field(..., description="Data health status (NORMAL, DEGRADED, INSUFFICIENT_DATA)", example="NORMAL")
    factors: List[ContributingFactor] = Field(default_factory=list, description="Top contributing factors")
    recommended_action: str = Field(..., description="Recommended safety mitigation action")


class CombinedStreamPayload(BaseModel):
    """Combined real-time telemetry and risk prediction for WebSocket streaming."""
    telemetry: SensorTelemetryPayload
    risk: RiskPredictionPayload


class AlertEventModel(BaseModel):
    """Alert event record."""
    alert_id: str = Field(..., example="ALERT-000001")
    timestamp: str = Field(..., example="2026-08-16T10:30:00Z")
    mine_id: str = Field(..., example="MINE-001")
    zone_id: str = Field(..., example="ZONE-003")
    sensor_id: str = Field(..., example="SENSOR-003")
    risk_level: str = Field(..., example="CRITICAL")
    risk_score: float = Field(..., example=87.4)
    message: str = Field(..., example="Geotechnical hazard detected in Zone ZONE-003 of Mine MINE-001.")
    recommended_action: str = Field(..., example="Evacuate personnel from the affected zone.")
    factors: List[ContributingFactor] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standardized API error response format."""
    detail: str = Field(..., description="Human-readable error explanation")
    error_code: Optional[str] = Field(default=None, description="System error category code")
