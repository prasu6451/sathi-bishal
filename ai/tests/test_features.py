"""
Unit tests for feature builder, 64-dim AlphaEarth flattening, categorical encoding, and schema serialization.
"""

import tempfile
from pathlib import Path
import numpy as np
import pytest

from ai.preprocessing.feature_builder import FeatureBuilder
from ai.preprocessing.feature_schema import FeatureSchema


def test_feature_builder_alphaearth_embedding_dim():
    builder = FeatureBuilder()
    assert builder.embedding_dim == 64
    assert "alphaearth_0" in builder.feature_names
    assert "alphaearth_63" in builder.feature_names


def test_extract_sample_features_full():
    sample = {
        "id": "t1",
        "location": {"latitude": 30.0, "longitude": 78.0},
        "timestamp": "2025-08-20T12:00:00Z",
        "alphaearth": {"embedding": [0.1 * i for i in range(64)]},
        "terrain": {"elevation": 1200.0, "slope": 25.0, "aspect": 180.0, "curvature": 0.1, "twi": 6.0},
        "rainfall": {"rain_1h": 10.0, "rain_24h": 50.0, "rain_3d": 100.0, "rain_7d": 150.0, "rain_14d": 200.0},
        "soil": {"moisture_0_7cm": 0.4, "moisture_7_28cm": 0.35},
        "satellite": {"ndvi": 0.6, "sar_displacement": -5.0},
        "geology": {"lithology": "metamorphic_rock", "geomorphology": "steep_slope", "lineament_distance_m": 500.0},
        "infrastructure": {"distance_to_road_m": 100.0, "distance_to_stream_m": 200.0},
        "population": {"density": 150.0},
        "land_use": {"class": "forest"},
        "historical": {"previous_landslide": True, "landslide_count_nearby": 2},
        "label": {"landslide": 1}
    }

    builder = FeatureBuilder()
    X_vec = builder.transform_record(sample)

    assert isinstance(X_vec, np.ndarray)
    assert len(X_vec) == len(builder.feature_names)
    assert not np.isnan(X_vec[0])  # alphaearth_0 = 0.0


def test_extract_sample_features_missing_optional_fields():
    # Sparse sample missing IoT, citizen reports, satellite SAR, geology
    sample = {
        "id": "sparse_1",
        "location": {"latitude": 30.0, "longitude": 78.0},
        "timestamp": "2025-08-20T12:00:00Z",
        "terrain": {"elevation": 1000.0, "slope": 15.0},
        "label": {"landslide": 0}
    }

    builder = FeatureBuilder()
    X_vec = builder.transform_record(sample)

    assert isinstance(X_vec, np.ndarray)
    assert len(X_vec) == len(builder.feature_names)
    # AlphaEarth missing -> expected NaN for embedding entries
    alpha_idx = builder.feature_names.index("alphaearth_0")
    assert np.isnan(X_vec[alpha_idx])


def test_schema_save_and_load():
    builder = FeatureBuilder()
    schema = builder.schema

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp:
        tmp_path = Path(tmp.name)

    try:
        schema.save(tmp_path)
        loaded = FeatureSchema.load(tmp_path)

        assert loaded.embedding_dim == 64
        assert loaded.feature_names == schema.feature_names
        assert loaded.categorical_values == schema.categorical_values
    finally:
        tmp_path.unlink(missing_ok=True)
