"""
Unit tests for LandslidePredictor inference engine, batch prediction,
schema validation mismatch, and edge case handling (Phase 13-14 of Master Prompt).
"""

import pytest
from pathlib import Path
from ai.config.config import get_default_config
from ai.inference.predictor import LandslidePredictor


@pytest.fixture
def predictor():
    cfg = get_default_config()
    model_dir = cfg.SAVED_MODELS_DIR / "current"
    return LandslidePredictor(model_dir=model_dir)


@pytest.fixture
def valid_record():
    return {
        "id": "inf_sample_1",
        "location": {"latitude": 26.15, "longitude": 91.75},
        "timestamp": "2025-08-20T12:00:00Z",
        "alphaearth": {"embedding": [0.05] * 64},
        "terrain": {"elevation": 1800.0, "slope": 38.0, "aspect": 120.0, "curvature": 0.1, "twi": 8.5},
        "rainfall": {"rain_1h": 30.0, "rain_24h": 110.0, "rain_3d": 180.0, "rain_7d": 310.0, "rain_14d": 450.0},
        "soil": {"moisture_0_7cm": 0.55, "moisture_7_28cm": 0.50},
        "satellite": {"ndvi": 0.50, "sar_displacement": -12.0},
        "geology": {"lithology": "metamorphic_rock", "geomorphology": "steep_slope", "lineament_distance_m": 450.0},
        "infrastructure": {
            "distance_to_road_m": 200.0, "distance_to_stream_m": 150.0, "distance_to_bridge_m": 1500.0,
            "distance_to_hospital_m": 6000.0, "distance_to_village_m": 400.0
        },
        "population": {"density": 200.0},
        "land_use": {"class": "forest"},
        "historical": {"previous_landslide": True, "landslide_count_nearby": 3},
        "iot": {"rainfall_mm": 30.0, "soil_moisture": 0.55}
    }


def test_predictor_single_sample(predictor, valid_record):
    result = predictor.predict(valid_record)
    assert "landslide_probability" in result
    assert "risk_score" in result
    assert "risk_level" in result
    assert result["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert result["model_version"] == "xgb-v1"


def test_predictor_batch(predictor, valid_record):
    records = [valid_record, valid_record]
    results = predictor.predict_batch(records)
    assert len(results) == 2
    assert results[0]["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


def test_predictor_invalid_latitude(predictor, valid_record):
    rec = dict(valid_record)
    rec["location"] = {"latitude": 120.0, "longitude": 91.75}
    with pytest.raises(ValueError, match="Invalid latitude"):
        predictor.predict(rec)


def test_predictor_wrong_alphaearth_dim(predictor, valid_record):
    rec = dict(valid_record)
    rec["alphaearth"] = {"embedding": [0.1] * 10}  # Wrong dim (expected 64)
    with pytest.raises(ValueError, match="dimension mismatch"):
        predictor.predict(rec)


def test_predictor_schema_mismatch_detection(predictor):
    predictor.schema.feature_names = ["wrong_f1", "wrong_f2"]
    with pytest.raises(ValueError, match="Feature count mismatch"):
        predictor.schema.validate_feature_schema(predictor.builder.feature_names)
