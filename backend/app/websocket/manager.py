"""
Native FastAPI WebSocket ConnectionManager.
Tracks active WebSocket clients and broadcasts live risk updates.
Matches Section 14, 16 of Master Prompt.
"""

import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("websocket_manager")


class ConnectionManager:
    """Thread-safe ConnectionManager for active WebSockets."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    @property
    def client_count(self) -> int:
        return len(self.active_connections)

    async def connect(self, websocket: WebSocket) -> None:
        """Accept WebSocket connection and register client."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections count: {self.client_count}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove WebSocket client on disconnect."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Active connections count: {self.client_count}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """Send direct JSON message to a single WebSocket client."""
        try:
            await websocket.send_json(message)
        except Exception as err:
            logger.error(f"Error sending WebSocket message: {err}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast live JSON risk update to all active WebSocket clients."""
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as err:
                logger.error(f"Error broadcasting to WebSocket client: {err}")
                disconnected_clients.append(connection)

        for conn in disconnected_clients:
            self.disconnect(conn)


# Global Singleton Manager
manager = ConnectionManager()
