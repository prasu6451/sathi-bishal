"""
Central configuration for SIH26001 Landslide Early-Warning AI Pipeline.
Updated to enforce strict leakage prevention and One-Hot Encoding for categoricals.
"""

import os
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Master configuration class for the AI pipeline."""

    # Project directories
    AI_DIR: Path = Path(__file__).resolve().parent.parent
    DATASET_DIR: Path = AI_DIR / "dataset"
    SAVED_MODELS_DIR: Path = AI_DIR / "saved_models"
    EXPERIMENTS_DIR: Path = AI_DIR / "experiments"
    RESULTS_DIR: Path = EXPERIMENTS_DIR / "results"
    DIAGNOSTICS_DIR: Path = AI_DIR / "diagnostics"

    # Default file paths
    TRAIN_JSONL: Path = DATASET_DIR / "train.jsonl"
    VALIDATION_JSONL: Path = DATASET_DIR / "validation.jsonl"
    TEST_JSONL: Path = DATASET_DIR / "test.jsonl"

    MODEL_SAVE_PATH: Path = SAVED_MODELS_DIR / "landslide_xgboost.json"
    SCHEMA_SAVE_PATH: Path = SAVED_MODELS_DIR / "feature_schema.json"
    PREPROCESSING_SAVE_PATH: Path = SAVED_MODELS_DIR / "preprocessing.json"
    METADATA_SAVE_PATH: Path = SAVED_MODELS_DIR / "model_metadata.json"

    METRICS_SAVE_PATH: Path = RESULTS_DIR / "metrics.json"
    MODEL_COMPARISON_JSON: Path = RESULTS_DIR / "model_comparison.json"
    MODEL_COMPARISON_MD: Path = RESULTS_DIR / "model_comparison.md"
    FEATURE_IMPORTANCE_PATH: Path = RESULTS_DIR / "feature_importance.csv"
    FEATURE_IMPORTANCE_PLOT: Path = RESULTS_DIR / "feature_importance.png"

    # AlphaEarth Foundations Configuration
    ALPHAEARTH_EMBEDDING_DIM: int = 64
    EARTHENGINE_PROJECT: str = os.getenv("EARTHENGINE_PROJECT", "sathi-507115")
    ALPHAEARTH_EE_ASSET_ID: str = os.getenv(
        "ALPHAEARTH_EE_ASSET_ID",
        "projects/google/alphaearth/foundations/v1"
    )

    # Prediction horizon for early warning
    PREDICTION_HORIZON_HOURS: int = 24

    # Risk level classification thresholds
    RISK_LEVEL_THRESHOLDS: Dict[str, float] = {
        "LOW": 0.25,
        "MODERATE": 0.50,
        "HIGH": 0.75,
        "CRITICAL": 1.00
    }

    # Baseline XGBoost Hyperparameters
    XGB_PARAMS: Dict[str, Any] = {
        "n_estimators": 500,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "eval_metric": "logloss"
    }

    # Known Categorical Column Values
    KNOWN_CATEGORICAL_VALUES: Dict[str, List[str]] = {
        "geology_lithology": [
            "unknown", "metamorphic_rock", "sedimentary_rock",
            "igneous_rock", "unconsolidated_sediment", "alluvium"
        ],
        "geology_geomorphology": [
            "unknown", "steep_slope", "gentle_slope", "valley_bottom",
            "ridge", "scarp", "plateau"
        ],
        "land_use_class": [
            "unknown", "forest", "agriculture", "barren_land",
            "built_up", "shrubland", "water_body"
        ]
    }

    # Predictive Early-Warning Numerical Features (Excluded post-event citizen reports to avoid leakage)
    NUMERICAL_FEATURES: List[str] = [
        "terrain_elevation",
        "terrain_slope",
        "terrain_aspect",
        "terrain_curvature",
        "terrain_twi",
        "rainfall_rain_1h",
        "rainfall_rain_24h",
        "rainfall_rain_3d",
        "rainfall_rain_7d",
        "rainfall_rain_14d",
        "soil_moisture_0_7cm",
        "soil_moisture_7_28cm",
        "satellite_ndvi",
        "satellite_sar_displacement",
        "geology_lineament_distance_m",
        "infrastructure_distance_to_road_m",
        "infrastructure_distance_to_stream_m",
        "infrastructure_distance_to_bridge_m",
        "infrastructure_distance_to_hospital_m",
        "infrastructure_distance_to_village_m",
        "population_density",
        "historical_previous_landslide",
        "historical_landslide_count_nearby",
        "iot_rainfall_mm",
        "iot_soil_moisture"
    ]

    RANDOM_SEED: int = 42


def get_default_config() -> Config:
    """Return an instance of the default configuration."""
    return Config()
