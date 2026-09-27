"""Integration tests for Native FastAPI WebSockets (/ws/risk)."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_websocket_connection_and_initial_state():
    with client.websocket_connect("/ws/risk") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "initial_risk_state"
        assert "data" in data
        assert isinstance(data["data"], list)


def test_websocket_ping_pong():
    with client.websocket_connect("/ws/risk") as websocket:
        initial = websocket.receive_json()
        assert initial["type"] == "initial_risk_state"

        websocket.send_text("ping")
        resp = websocket.receive_text()
        assert resp == "pong"
