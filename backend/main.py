"""
MineGuard AI — FastAPI Application Entrypoint
Exposes REST and WebSocket endpoints for mine sensor simulation, AI risk prediction, and alerting.
Strictly conforms to API_CONTRACT.md.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure repository root is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from fastapi import FastAPI, HTTPException, WebSocket, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.alerts import alert_service
from backend.models import (
    HealthResponse,
    SensorTelemetryPayload,
    SimulationStartRequest,
    SimulationStatusResponse,
    RiskPredictionPayload,
    AlertEventModel,
    ErrorResponse,
)
from backend.services import simulation_service
from backend.websocket import stream_sensor_telemetry
from simulation.scenarios import ScenarioType
from simulation.validation import validate_reading, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mineguard.backend")

# Create FastAPI instance with rich OpenAPI metadata
app = FastAPI(
    title="MineGuard AI Backend & Risk API",
    description=(
        "Backend REST and WebSocket telemetry and AI risk assessment service for MineGuard AI — "
        "AI-based rockfall prediction and early-warning system for open-pit mines. "
        "Conforms to API Contract v1.0.0."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for future frontend/dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers for clean API error responses
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    logger.warning(f"Payload validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Sensor validation error: {str(exc)}", "error_code": "INVALID_TELEMETRY"},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Value error encountered: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "error_code": "INVALID_PARAMETER"},
    )


# -------------------------------------------------------------
# SYSTEM & TELEMETRY ENDPOINTS
# -------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Returns the operational health status of the backend service."""
    return HealthResponse(status="ok", service="MineGuard AI backend")


@app.get(
    "/api/v1/sensors/latest",
    response_model=SensorTelemetryPayload,
    summary="Get Latest Sensor Reading",
    tags=["Sensors"],
    responses={
        200: {"description": "Latest valid sensor telemetry payload."},
        500: {"model": ErrorResponse, "description": "Internal server error."},
    },
)
async def get_latest_sensor_reading() -> Dict[str, Any]:
    """
    Returns the latest valid sensor telemetry payload.
    Adheres strictly to the schema defined in API_CONTRACT.md.
    """
    reading = simulation_service.get_latest_reading()
    validate_reading(reading)
    return reading

@app.post(
    "/api/v1/sensors/readings",
    response_model=SensorTelemetryPayload,
    summary="Ingest External IoT Sensor Reading",
    tags=["Sensors"],
    responses={
        200: {"description": "External sensor telemetry accepted and processed."},
        400: {"model": ErrorResponse, "description": "Invalid sensor telemetry payload."},
    },
)
async def ingest_sensor_reading(
    reading: SensorTelemetryPayload,
) -> Dict[str, Any]:
    """
    Accepts an externally supplied IoT sensor reading.

    The reading is validated, evaluated by the risk engine,
    and passed through the alert system.
    """
    reading_dict = reading.model_dump()

    validate_reading(reading_dict)

    simulation_service.evaluate_external_reading(reading_dict)

    return reading_dict


@app.get(
    "/api/v1/sensors/{mine_id}/{zone_id}/{sensor_id}",
    response_model=SensorTelemetryPayload,
    summary="Get Specific Sensor Reading",
    tags=["Sensors"],
    responses={
        200: {"description": "Current reading for the specified sensor."},
        404: {"model": ErrorResponse, "description": "Requested sensor not found."},
    },
)
async def get_sensor_by_id(mine_id: str, zone_id: str, sensor_id: str) -> Dict[str, Any]:
    """
    Retrieves the latest reading for a specific mine, zone, and sensor identifier.
    """
    reading = simulation_service.get_sensor_reading(mine_id, zone_id, sensor_id)
    if reading is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor '{sensor_id}' in zone '{zone_id}' of mine '{mine_id}' not found.",
        )
    validate_reading(reading)
    return reading


@app.post(
    "/api/v1/simulation/start",
    response_model=SimulationStatusResponse,
    summary="Start / Reconfigure Simulation",
    tags=["Simulation"],
    responses={
        200: {"description": "Simulation successfully started or reconfigured."},
        400: {"model": ErrorResponse, "description": "Invalid scenario or configuration."},
    },
)
async def start_simulation(req: SimulationStartRequest) -> Dict[str, Any]:
    """
    Starts or reconfigures the sensor simulation engine with specified parameters.
    """
    try:
        status_info = simulation_service.start_simulation(
            mine_id=req.mine_id,
            zone_id=req.zone_id,
            sensor_id=req.sensor_id,
            scenario=req.scenario,
            interval=req.interval,
            seed=req.seed,
        )
        return status_info
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@app.post(
    "/api/v1/simulation/stop",
    response_model=SimulationStatusResponse,
    summary="Stop Simulation",
    tags=["Simulation"],
)
async def stop_simulation() -> Dict[str, Any]:
    """Stops the active telemetry simulation."""
    return simulation_service.stop_simulation()


@app.get(
    "/api/v1/simulation/status",
    response_model=SimulationStatusResponse,
    summary="Get Simulation Status",
    tags=["Simulation"],
)
async def get_simulation_status() -> Dict[str, Any]:
    """Returns current configuration and operational status of the simulation."""
    return simulation_service.get_status()


# -------------------------------------------------------------
# AI RISK PREDICTION ENDPOINTS
# -------------------------------------------------------------

@app.get(
    "/api/v1/risk/latest",
    response_model=RiskPredictionPayload,
    summary="Get Latest AI Risk Assessment",
    tags=["Risk Engine"],
)
async def get_latest_risk() -> Dict[str, Any]:
    """
    Returns the latest AI geotechnical slope-failure risk prediction.
    """
    return simulation_service.get_latest_prediction()


@app.get(
    "/api/v1/risk/{mine_id}/{zone_id}/{sensor_id}",
    response_model=RiskPredictionPayload,
    summary="Get Sensor Risk Assessment",
    tags=["Risk Engine"],
    responses={
        200: {"description": "Current risk assessment for the requested sensor."},
        404: {"model": ErrorResponse, "description": "Sensor not found."},
    },
)
async def get_sensor_risk_by_id(mine_id: str, zone_id: str, sensor_id: str) -> Dict[str, Any]:
    """
    Retrieves the latest risk assessment for a specific sensor.
    """
    prediction = simulation_service.get_sensor_risk(mine_id, zone_id, sensor_id)
    if prediction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk assessment for sensor '{sensor_id}' in zone '{zone_id}' of mine '{mine_id}' not found.",
        )
    return prediction


@app.post(
    "/api/v1/risk/predict",
    response_model=RiskPredictionPayload,
    summary="Evaluate Risk for Supplied Sensor Reading",
    tags=["Risk Engine"],
    responses={
        200: {"description": "Risk prediction computed successfully."},
        400: {"model": ErrorResponse, "description": "Invalid sensor reading payload."},
    },
)
async def predict_risk_for_reading(reading: SensorTelemetryPayload) -> Dict[str, Any]:
    """
    Directly evaluates risk score, level, factors, and action for an externally supplied sensor reading.
    """
    reading_dict = reading.model_dump()
    return simulation_service.evaluate_external_reading(reading_dict)


@app.get(
    "/api/v1/risk/history",
    response_model=List[RiskPredictionPayload],
    summary="Get Chronological Risk History",
    tags=["Risk Engine"],
)
async def get_risk_history(
    limit: Optional[int] = Query(default=50, ge=1, le=500, description="Max history records to return")
) -> List[Dict[str, Any]]:
    """
    Returns chronological history of recent AI risk predictions.
    """
    return simulation_service.get_prediction_history(limit=limit)


@app.get(
    "/api/v1/alerts/history",
    response_model=List[AlertEventModel],
    summary="Get Geotechnical Alert History",
    tags=["Alerts"],
)
async def get_alert_history(
    limit: Optional[int] = Query(default=50, ge=1, le=200, description="Max alerts to return")
) -> List[Dict[str, Any]]:
    """
    Returns historical log of triggered HIGH and CRITICAL geotechnical safety alerts.
    """
    return alert_service.get_history(limit=limit)


# -------------------------------------------------------------
# WEBSOCKET STREAMING ENDPOINT
# -------------------------------------------------------------

@app.websocket("/ws/sensors")
async def websocket_sensors_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint streaming combined sensor telemetry and AI risk predictions.
    """
    await stream_sensor_telemetry(websocket)
