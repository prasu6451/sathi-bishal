"""
Unit tests for end-to-end model training, evaluation, model loading, and local prediction.
Runs completely offline without requiring external API access.
"""

import tempfile
from pathlib import Path
import pytest
import numpy as np

from ai.config.config import get_default_config
from ai.preprocessing.load_jsonl import load_jsonl_dataset
from ai.preprocessing.preprocess import PreprocessingPipeline
from ai.models.predict import LandslidePredictor
from ai.models.evaluate import evaluate_predictions
from ai.models.model_utils import compute_risk_level


def test_compute_risk_level_thresholds():
    score, level = compute_risk_level(0.10)
    assert score == 10
    assert level == "LOW"

    score, level = compute_risk_level(0.35)
    assert score == 35
    assert level == "MODERATE"

    score, level = compute_risk_level(0.60)
    assert score == 60
    assert level == "HIGH"

    score, level = compute_risk_level(0.85)
    assert score == 85
    assert level == "CRITICAL"


def test_evaluate_predictions_metrics():
    y_true = np.array([1, 1, 0, 0, 1, 0])
    y_probs = np.array([0.9, 0.8, 0.2, 0.1, 0.7, 0.3])

    metrics = evaluate_predictions(y_true, y_probs, threshold=0.5)

    assert metrics["recall"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["roc_auc"] == 1.0
    assert metrics["false_negative_rate"] == 0.0


def test_hard_negative_stress_test_behavior():
    """Verify that predictor handles hard negative stress records cleanly without erroring."""
    from ai.inference.predictor import LandslidePredictor
    from ai.preprocessing.load_jsonl import load_jsonl_dataset

    records = load_jsonl_dataset("c:/Users/PK/Desktop/sathi/ai/dataset/hard_negative_stress_test.jsonl")
    assert len(records) == 300

    predictor = LandslidePredictor()
    sample = records[0]
    res = predictor.predict(sample)

    assert "landslide_probability" in res
    assert "risk_score" in res
    assert "risk_level" in res
    assert res["model_version"] == "xgb-v1"


