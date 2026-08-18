"""
MineGuard AI — Real-Time WebSocket Telemetry & Risk Streaming
Streams combined sensor telemetry and AI risk predictions to connected clients.
"""

import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

from backend.services import simulation_service
from simulation.validation import validate_reading, ValidationError

logger = logging.getLogger("mineguard.websocket")


class ConnectionManager:
    """
    Manages active WebSocket telemetry connections and broadcasting.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts and registers a new WebSocket client."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Removes a disconnected client."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """Broadcasts a JSON message to all active clients."""
        disconnected = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


def build_stream_message(reading: dict, prediction: dict) -> dict:
    """
    Builds a unified stream payload containing top-level fields,
    the 'telemetry' block, and the 'risk' prediction block.
    """
    risk_block = {
        "score": prediction.get("risk_score", 0.0),
        "risk_score": prediction.get("risk_score", 0.0),
        "level": prediction.get("risk_level", "LOW"),
        "risk_level": prediction.get("risk_level", "LOW"),
        "confidence": prediction.get("confidence", 0.95),
        "status": prediction.get("status", "NORMAL"),
        "factors": prediction.get("factors", []),
        "recommended_action": prediction.get("recommended_action", ""),
    }

    # Merged payload supporting both pure telemetry keys and structured telemetry/risk blocks
    message = dict(reading)
    message["telemetry"] = reading
    message["risk"] = risk_block
    return message


async def stream_sensor_telemetry(websocket: WebSocket) -> None:
    """
    Handles WebSocket connections at /ws/sensors.
    Continuously delivers live sensor telemetry and AI risk predictions.
    """
    await manager.connect(websocket)

    try:
        while True:
            if simulation_service.is_running:
                reading = simulation_service.generate_next_reading()
                validate_reading(reading)
                prediction = simulation_service.get_latest_prediction()
                payload = build_stream_message(reading, prediction)
                await websocket.send_json(payload)
            else:
                reading = simulation_service.get_latest_reading()
                prediction = simulation_service.get_latest_prediction()
                payload = build_stream_message(reading, prediction)
                await websocket.send_json(payload)

            interval = max(0.05, simulation_service.interval_seconds)
            await asyncio.sleep(interval)

    except WebSocketDisconnect:
        logger.info("Client disconnected normally from /ws/sensors")
    except asyncio.CancelledError:
        logger.info("WebSocket streaming task cancelled")
    except Exception as e:
        logger.warning(f"WebSocket connection closed: {e}")
    finally:
        manager.disconnect(websocket)
