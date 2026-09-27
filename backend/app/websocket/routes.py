"""
Native FastAPI WebSocket Route Endpoint (/ws/risk).
Pushes initial_risk_state on client connect and maintains live connection for updates.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.websocket.manager import manager
from app.database.connection import get_db
from app.database.repositories import RiskPredictionRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/risk")
async def websocket_risk_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time risk updates.
    Sends initial_risk_state upon connection and keeps connection active.
    """
    await manager.connect(websocket)

    try:
        # Fetch initial risk state for all monitored locations
        risk_repo = RiskPredictionRepository(db)
        latest_preds = risk_repo.get_latest_predictions_all_locations()

        initial_data = []
        for p in latest_preds:
            ts = getattr(p, "prediction_timestamp", None)
            ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts or datetime.now(timezone.utc).isoformat())
            initial_data.append({
                "prediction_id": p.id,
                "location_id": p.location_id,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "landslide_probability": p.landslide_probability,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "model_version": p.model_version,
                "timestamp": ts_str
            })

        # Send initial_risk_state message
        initial_msg = {
            "type": "initial_risk_state",
            "data": initial_data
        }
        await manager.send_personal_message(initial_msg, websocket)

        # Keep connection open for live broadcasts
        while True:
            # Wait for client messages or keepalive pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as err:
        logger.error(f"WebSocket error: {err}")
        manager.disconnect(websocket)
