"""
MineGuard AI — FastAPI Route Handlers
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from iot.sensor_schema import TelemetrySchema, validate_raw_telemetry_dict
from iot.device_manager import DeviceManager
from inference.predictor import RealTimePredictor
from inference.rolling_window import RollingWindowBuffer
from risk_engine.risk_calculator import RiskCalculator
from alerts.alert_store import AlertStore
from alerts.alert_manager import AlertManager
from api.websocket import ws_manager
from ml.utils import logger

router = APIRouter(prefix="/api/v1")

# Instantiate Pipeline Components
device_mgr = DeviceManager()
rolling_buffer = RollingWindowBuffer()
predictor = RealTimePredictor()
risk_calc = RiskCalculator()
alert_store = AlertStore()
alert_mgr = AlertManager(alert_store=alert_store)

# Memory Cache for Zone Latest Risk Status
zone_risk_cache: dict = {}


@router.get("/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "HEALTHY",
        "system": "MineGuard-AI Real-Time Early-Warning Prototype",
        "version": "1.0.0",
        "active_sensors": len(device_mgr.get_all_devices()),
        "active_zones": len(device_mgr.get_all_zones()),
        "ml_model_status": "LOADED" if predictor.model is not None else "DEGRADED"
    }


@router.post("/telemetry")
async def ingest_telemetry(payload: dict):
    """
    Primary Canonical Telemetry Ingestion Endpoint.
    Handles ESP32 edge devices and Simulator POST requests.
    """
    # 1. Validation & Normalization
    is_valid, schema_obj, err_msg = validate_raw_telemetry_dict(payload)
    if not is_valid:
        logger.warning("Rejected malformed telemetry payload: %s", err_msg)
        raise HTTPException(status_code=400, detail=f"Malformed Telemetry Payload: {err_msg}")
        
    telemetry_dict = schema_obj.to_dict()
    sensor_id = telemetry_dict["sensor_id"]
    zone_id = telemetry_dict["zone_id"]
    
    # 2. Register Device Activity
    device_mgr.register_telemetry(
        sensor_id=sensor_id,
        zone_id=zone_id,
        lat=telemetry_dict["latitude"],
        lon=telemetry_dict["longitude"],
        timestamp_iso=telemetry_dict["timestamp"]
    )
    
    # Check Stale Device status
    status = device_mgr.check_device_status(sensor_id)
    is_stale = (status == "STALE")
    zone_sensors = device_mgr.get_zone_sensors(zone_id)
    
    # 3. Rolling Window Temporal Feature Engineering
    rolling_features = rolling_buffer.add_telemetry(telemetry_dict)
    
    # 4. Real-Time ML Inference
    ml_result = predictor.predict(telemetry_dict, rolling_features)
    
    # 5. Risk Engine Fusion
    risk_result = risk_calc.calculate_risk(
        telemetry=telemetry_dict,
        ml_result=ml_result,
        rolling_features=rolling_features,
        is_stale=is_stale,
        sensor_count_in_zone=len(zone_sensors)
    )
    
    # Cache Zone Risk Status
    zone_risk_cache[zone_id] = {
        "zone_id": zone_id,
        "timestamp": telemetry_dict["timestamp"],
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "trend": risk_result["trend"],
        "confidence": risk_result["confidence"],
        "contributing_factors": risk_result["contributing_factors"],
        "recommended_action": risk_result["recommended_action"],
        "latitude": telemetry_dict["latitude"],
        "longitude": telemetry_dict["longitude"]
    }
    
    # 6. Alert Engine Evaluation
    alert_record = alert_mgr.evaluate_risk_and_trigger_alert(telemetry_dict, risk_result)
    
    # 7. WebSocket Event Broadcast
    await ws_manager.broadcast_event("TELEMETRY_INGESTED", {
        "telemetry": telemetry_dict,
        "risk": risk_result,
        "ml": ml_result
    })
    
    if alert_record:
        await ws_manager.broadcast_event("ALERT_TRIGGERED", alert_record)
        
    return {
        "status": "ACCEPTED",
        "event_id": telemetry_dict["event_id"],
        "ml_result": ml_result,
        "risk_result": risk_result,
        "alert_triggered": alert_record is not None,
        "alert_id": alert_record["alert_id"] if alert_record else None
    }


@router.get("/risk/{zone_id}")
def get_zone_risk(zone_id: str):
    """Retrieve current risk evaluation status for a specific mine zone."""
    if zone_id in zone_risk_cache:
        return zone_risk_cache[zone_id]
        
    # Return default baseline if zone has no active readings yet
    return {
        "zone_id": zone_id,
        "timestamp": None,
        "risk_score": 0.0,
        "risk_level": "LOW",
        "trend": "STABLE",
        "confidence": 1.0,
        "contributing_factors": [],
        "recommended_action": "Routine observation."
    }


@router.get("/alerts")
def get_alerts(zone_id: Optional[str] = None):
    """Retrieve safety alerts (optional zone_id filter)."""
    return alert_store.get_all_alerts(zone_id=zone_id)


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str):
    """Acknowledge an active alert."""
    alert = alert_store.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    return alert


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    """Resolve an active alert."""
    alert = alert_store.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    return alert


@router.get("/zones")
def get_zones():
    """List all registered mine zones and coordinates."""
    zones = device_mgr.get_all_zones()
    for z in zones:
        z_id = z["zone_id"]
        if z_id in zone_risk_cache:
            z["risk_score"] = zone_risk_cache[z_id]["risk_score"]
            z["risk_level"] = zone_risk_cache[z_id]["risk_level"]
        else:
            z["risk_score"] = 0.0
            z["risk_level"] = "LOW"
    return zones


@router.get("/sensors")
def get_sensors():
    """List all registered sensor devices and live status."""
    return device_mgr.get_all_devices()
