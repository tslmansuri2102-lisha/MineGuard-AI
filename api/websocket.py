"""
MineGuard AI — Real-Time WebSocket Event Broadcaster
"""

import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from ml.utils import logger


class WebSocketManager:
    """
    Manages active WebSocket client connections and broadcasts real-time telemetry/alert events.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket Client Connected. Active subscribers: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket Client Disconnected. Remaining subscribers: %d", len(self.active_connections))

    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcast JSON event to all connected clients."""
        payload = {
            "event_type": event_type,
            "data": data
        }
        json_str = json.dumps(payload)
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json_str)
            except Exception as e:
                logger.warning("Failed to send WebSocket message, removing client: %s", e)
                disconnected.append(connection)
                
        for dead in disconnected:
            self.disconnect(dead)


ws_manager = WebSocketManager()
