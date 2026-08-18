"""
MineGuard AI — Real-Time WebSocket Telemetry & Risk Streaming
Streams combined sensor telemetry and AI risk predictions to connected clients.
"""

import asyncio
import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.services import simulation_service
from simulation.validation import validate_reading

logger = logging.getLogger("mineguard.websocket")


class ConnectionManager:
    """
    Manages active WebSocket telemetry connections.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            "WebSocket client connected. Total active: %s",
            len(self.active_connections),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info(
            "WebSocket client disconnected. Total active: %s",
            len(self.active_connections),
        )

    async def broadcast(self, message: dict) -> None:
        disconnected = set()

        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


def build_stream_message(reading: dict, prediction: dict) -> dict:
    """
    Builds the unified WebSocket payload.
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

    message = dict(reading)

    message["scenario"] = simulation_service.get_status()["scenario"]    
    message["telemetry"] = reading
    message["risk"] = risk_block

    return message


async def stream_sensor_telemetry(websocket: WebSocket) -> None:
    """
    Handles /ws/sensors.

    Generates live telemetry using the CURRENT simulation configuration.
    """

    await manager.connect(websocket)

    try:
        while True:

            # Read current simulation state immediately before generation.
            is_running = simulation_service.is_running
            interval = max(0.05, simulation_service.interval_seconds)

            if is_running:
                reading = simulation_service.generate_next_reading()
            else:
                reading = simulation_service.get_latest_reading()

            validate_reading(reading)

            prediction = simulation_service.get_latest_prediction()

            payload = build_stream_message(
                reading,
                prediction,
            )

            await websocket.send_json(payload)

            # Sleep only after sending the current step.
            await asyncio.sleep(interval)

    except WebSocketDisconnect:
        logger.info("Client disconnected normally from /ws/sensors")

    except asyncio.CancelledError:
        logger.info("WebSocket streaming task cancelled")

    except Exception as exc:
        logger.warning("WebSocket connection closed: %s", exc)

    finally:
        manager.disconnect(websocket)