"""
End-to-End Real-Time System Integration Test.
Tests: Sensor/Weather Ingestion -> DB Persistence -> Feature Assembly -> AI Inference -> MySQL -> WebSocket.
Matches Phase 37 of Master Prompt.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_end_to_end_realtime_pipeline():
    with TestClient(app) as client:
        # STEP 1: Health & Model Status Check
        health_resp = client.get("/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "ok"

        model_resp = client.get("/api/v1/model/status")
        assert model_resp.status_code == 200
        assert model_resp.json()["loaded"] is True
        assert model_resp.json()["model_version"] == "xgb-v1"

        # STEP 2: Ingest Weather Observation
        weather_payload = {
            "latitude": 26.15,
            "longitude": 91.75,
            "rain_1h": 28.0,
            "rain_24h": 110.0,
            "rain_3d": 195.0,
            "rain_7d": 320.0,
            "rain_14d": 480.0
        }
        w_resp = client.post("/api/v1/weather/observations", json=weather_payload)
        assert w_resp.status_code == 201

        # STEP 3: Ingest IoT Sensor Reading & Verify Automatic AI Prediction Trigger
        sensor_payload = {
            "sensor_id": "ESP32_E2E_001",
            "latitude": 26.15,
            "longitude": 91.75,
            "rainfall_mm": 28.0,
            "soil_moisture": 0.52,
            "temperature": 25.5,
            "humidity": 88.0
        }
        s_resp = client.post("/api/v1/sensors/readings", json=sensor_payload)
        assert s_resp.status_code == 201
        s_data = s_resp.json()
        assert s_data["status"] == "success"
        assert "prediction" in s_data
        assert s_data["prediction"]["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]

        # STEP 4: Verify Risk History Retransmits Stored Prediction
        hist_resp = client.get("/api/v1/risk/latest")
        assert hist_resp.status_code == 200
        latest = hist_resp.json()
        assert isinstance(latest, list)
        assert len(latest) > 0

        # STEP 5: WebSocket Connection & Initial State Verification
        with client.websocket_connect("/ws/risk") as ws:
            ws_data = ws.receive_json()
            assert ws_data["type"] == "initial_risk_state"
            assert isinstance(ws_data["data"], list)
