"""
MineGuard AI — FastAPI Real-Time Server Entrypoint
"""

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.websocket import ws_manager
from ml.utils import logger

app = FastAPI(
    title="MineGuard AI — Real-Time Rockfall Prediction & Early-Warning API",
    description="Production-style modular real-time telemetry ingestion, ML inference, risk engine, alert manager, and WebSocket broadcaster.",
    version="1.0.0"
)

# Enable CORS for Frontend/Dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST Routes
app.include_router(api_router)


@app.get("/")
def root():
    return {
        "system": "MineGuard AI — Real-Time Early-Warning System",
        "status": "RUNNING",
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket event subscription endpoint."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive client messages if sent
            data = await websocket.receive_text()
            logger.debug("Received WS text from client: %s", data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning("WebSocket connection exception: %s", e)
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    logger.info("Starting MineGuard AI FastAPI server on http://localhost:8000...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
