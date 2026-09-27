"""
Sanity and Responsiveness Unit Tests for SATHI AI Pipeline.
Matches Section 27 & 38 of AI Audit Prompt.
"""

import json
from pathlib import Path
import numpy as np
import pytest

from ai.config.config import get_default_config
from ai.preprocessing.feature_schema import FeatureSchema
from ai.preprocessing.feature_builder import FeatureBuilder
from ai.models.predict import LandslidePredictor


@pytest.fixture
def sample_high_risk():
    return {
        "id": "test_high_risk",
        "location": {"latitude": 26.15, "longitude": 91.75},
        "timestamp": "2025-08-20T12:00:00Z",
        "alphaearth": {"embedding": [0.1] * 64},
        "terrain": {"elevation": 2100.0, "slope": 48.5, "aspect": 180.0, "curvature": 0.2, "twi": 9.5},
        "rainfall": {"rain_1h": 45.0, "rain_24h": 140.0, "rain_3d": 220.0, "rain_7d": 380.0, "rain_14d": 520.0},
        "soil": {"moisture_0_7cm": 0.65, "moisture_7_28cm": 0.60},
        "satellite": {"ndvi": 0.45, "sar_displacement": -25.0},
        "geology": {"lithology": "metamorphic_rock", "geomorphology": "steep_slope", "lineament_distance_m": 200.0},
        "infrastructure": {
            "distance_to_road_m": 150.0, "distance_to_stream_m": 100.0, "distance_to_bridge_m": 1000.0,
            "distance_to_hospital_m": 5000.0, "distance_to_village_m": 300.0
        },
        "population": {"density": 250.0},
        "land_use": {"class": "forest"},
        "historical": {"previous_landslide": True, "landslide_count_nearby": 5},
        "iot": {"rainfall_mm": 45.0, "soil_moisture": 0.65}
    }


@pytest.fixture
def sample_low_risk():
    return {
        "id": "test_low_risk",
        "location": {"latitude": 26.15, "longitude": 91.75},
        "timestamp": "2025-08-20T12:00:00Z",
        "alphaearth": {"embedding": [0.1] * 64},
        "terrain": {"elevation": 150.0, "slope": 3.2, "aspect": 45.0, "curvature": 0.0, "twi": 2.1},
        "rainfall": {"rain_1h": 0.0, "rain_24h": 1.2, "rain_3d": 5.0, "rain_7d": 12.0, "rain_14d": 25.0},
        "soil": {"moisture_0_7cm": 0.12, "moisture_7_28cm": 0.08},
        "satellite": {"ndvi": 0.55, "sar_displacement": 0.1},
        "geology": {"lithology": "alluvium", "geomorphology": "gentle_slope", "lineament_distance_m": 1200.0},
        "infrastructure": {
            "distance_to_road_m": 500.0, "distance_to_stream_m": 800.0, "distance_to_bridge_m": 3000.0,
            "distance_to_hospital_m": 10000.0, "distance_to_village_m": 1500.0
        },
        "population": {"density": 100.0},
        "land_use": {"class": "agriculture"},
        "historical": {"previous_landslide": False, "landslide_count_nearby": 0},
        "iot": {"rainfall_mm": 0.0, "soil_moisture": 0.12}
    }


def test_feature_builder_dimension_and_onehot(sample_high_risk):
    builder = FeatureBuilder()
    vec = builder.transform_record(sample_high_risk)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == builder.schema.feature_count
    # AlphaEarth 64 dims
    assert not np.isnan(vec[:64]).any()


def test_feature_schema_validation():
    schema = FeatureSchema(feature_names=["f1", "f2", "f3"])
    assert schema.validate_feature_schema(["f1", "f2", "f3"]) is True
    with pytest.raises(ValueError):
        schema.validate_feature_schema(["f1", "f2"])
    with pytest.raises(ValueError):
        schema.validate_feature_schema(["f1", "f3", "f2"])


def test_model_responsiveness_sanity(sample_high_risk, sample_low_risk):
    cfg = get_default_config()
    model_dir = cfg.SAVED_MODELS_DIR

    if not (model_dir / "landslide_xgboost.json").exists():
        pytest.skip("Trained model artifact not present.")

    predictor = LandslidePredictor(model_dir=model_dir)

    res_high = predictor.predict_sample(sample_high_risk)
    res_low = predictor.predict_sample(sample_low_risk)

    assert res_high["landslide_probability"] > res_low["landslide_probability"]
    assert res_high["risk_score"] > res_low["risk_score"]
