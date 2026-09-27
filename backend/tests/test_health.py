"""Integration tests for FastAPI Health Endpoint."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"
        assert "model" in data
        assert "websocket_clients" in data


def test_zones_root_alias():
    with TestClient(app) as client:
        response = client.get("/zones")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


def test_dashboard_overview_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert "stat_cards" in data
        assert "zone_summary" in data
        assert "alerts" in data
        assert "trend_data" in data
        assert "recommendations" in data
        assert len(data["stat_cards"]) == 4
        assert len(data["zone_summary"]) >= 5

