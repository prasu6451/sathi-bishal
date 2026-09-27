"""Integration tests for AI Prediction API and Sensor Ingestion."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_create_prediction():
    with TestClient(app) as client:
        payload = {
            "location": {"latitude": 26.15, "longitude": 91.75},
            "rainfall": {"rain_1h": 35.0, "rain_24h": 120.0, "rain_3d": 210.0, "rain_7d": 350.0, "rain_14d": 500.0},
            "terrain": {"elevation": 2000.0, "slope": 42.0, "aspect": 180.0, "curvature": 0.1, "twi": 8.5},
            "soil": {"moisture_0_7cm": 0.55, "moisture_7_28cm": 0.50}
        }
        response = client.post("/api/v1/predictions/predict", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "landslide_probability" in data
        assert "risk_score" in data
        assert "risk_level" in data
        assert data["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_sensor_reading_ingestion():
    with TestClient(app) as client:
        payload = {
            "sensor_id": "TEST_ESP32_01",
            "latitude": 26.15,
            "longitude": 91.75,
            "rainfall_mm": 25.0,
            "soil_moisture": 0.50,
            "temperature": 26.0,
            "humidity": 90.0
        }
        response = client.post("/api/v1/sensors/readings", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "sensor_reading_id" in data
