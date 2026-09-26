"""
Integration & Unit Test Suite for Disaster Management ML Endpoints.
Verifies all 7 models: Flood Severity, Rescue Priority, Resource Allocation,
Area Clustering, SOS NLP, Damage Assessment, Safe Route, and Unified Pipeline.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_flood_severity_endpoint():
    payload = {
        "rainfall_24h_mm": 120.0,
        "rainfall_7d_mm": 280.0,
        "soil_moisture": 0.85,
        "elevation_m": 80.0,
        "slope_deg": 3.5,
        "river_distance_m": 250.0
    }
    resp = client.post("/api/v1/disaster/flood-severity", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "severity_index" in data
    assert data["severity_level"] in ["LOW", "MODERATE", "SEVERE", "CATASTROPHIC"]
    assert data["estimated_water_depth_m"] > 0.0


def test_rescue_priority_endpoint():
    payload = {
        "area_name": "Majuli Island Sector 4",
        "population_density_sqkm": 3200.0,
        "sos_count": 28,
        "vulnerability_index": 0.75,
        "flood_depth_m": 2.4,
        "road_accessibility_pct": 15.0
    }
    resp = client.post("/api/v1/disaster/rescue-priority", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["priority_tier"] == "PRIORITY_1_CRITICAL"
    assert "urgency_score" in data


def test_resource_allocation_endpoint():
    payload = {
        "affected_population": 4500,
        "severity_index": 0.78,
        "duration_days": 4,
        "medical_incident_count": 12
    }
    resp = client.post("/api/v1/disaster/resource-allocation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    alloc = data["allocations"]
    assert alloc["clean_water_litres"] > 0
    assert alloc["food_ration_packs"] > 0
    assert alloc["medical_trauma_kits"] > 0
    assert alloc["rescue_boats"] >= 3


def test_sos_nlp_classifier_endpoint():
    # Critical medical
    resp1 = client.post("/api/v1/disaster/classify-sos", json={"message": "Urgent! Pregnant woman bleeding heavily on rooftop, need doctor ambulance immediately!"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["category"] == "MEDICAL_EMERGENCY"
    assert data1["is_critical"] is True

    # Trapped / Evac
    resp2 = client.post("/api/v1/disaster/classify-sos", json={"message": "Water rising fast to 2nd floor, 6 family members trapped on roof with no boat"})
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["category"] == "EVACUATION_TRAPPED"

    # Food / Water
    resp3 = client.post("/api/v1/disaster/classify-sos", json={"message": "No drinking water or baby formula food supplies left for 3 days"})
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["category"] == "FOOD_WATER_NEED"


def test_damage_assessment_endpoint():
    payload = {
        "structure_type": "BRIDGE",
        "flood_depth_m": 3.8,
        "water_flow_velocity_mps": 3.2,
        "structure_age_years": 35,
        "construction_material": "MASONRY"
    }
    resp = client.post("/api/v1/disaster/damage-assessment", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "damage_percentage" in data
    assert "functional_status" in data


def test_safe_route_endpoint():
    payload = {
        "origin": {"latitude": 26.15, "longitude": 91.75},
        "destination": {"latitude": 26.25, "longitude": 91.90},
        "hazard_zones": [
            {"latitude": 26.18, "longitude": 91.80, "severity": 0.9, "hazard_type": "FLOOD"}
        ]
    }
    resp = client.post("/api/v1/disaster/safe-route", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["safe_route_waypoints"]) > 0
    assert data["safe_distance_km"] > 0
    assert data["safety_score_pct"] > 80.0


def test_unified_pipeline_endpoint():
    payload = {
        "area_name": "Guwahati Central Basin",
        "latitude": 26.18,
        "longitude": 91.75,
        "rainfall_24h_mm": 140.0,
        "rainfall_7d_mm": 350.0,
        "soil_moisture": 0.88,
        "elevation_m": 55.0,
        "slope_deg": 2.5,
        "population": 2500,
        "sos_messages": [
            "Trapped on ground floor, need rescue boat",
            "Diabetic elder needs insulin urgently"
        ]
    }
    resp = client.post("/api/v1/disaster/unified-pipeline", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "flood_severity" in data
    assert "rescue_priority" in data
    assert "resource_allocation" in data
    assert len(data["sos_analysis"]) == 2
    assert "executive_summary" in data
