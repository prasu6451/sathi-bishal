"""
Production-grade Landslide Risk Predictor Engine for SATHI AI Pipeline.
Handles model loading, schema validation, One-Hot preprocessing, structured prediction,
and robust edge case error handling (Phase 12-15 of Master Prompt).
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
import numpy as np

from ai.config.config import get_default_config
from ai.preprocessing.feature_schema import FeatureSchema
from ai.preprocessing.feature_builder import FeatureBuilder
from ai.models.model_utils import load_xgboost_model, compute_risk_level

logger = logging.getLogger("inference_predictor")


class LandslidePredictor:
    """Production Landslide Risk Prediction Engine."""

    def __init__(self, model_dir: Optional[Union[str, Path]] = None) -> None:
        self.cfg = get_default_config()
        self.model_dir = Path(model_dir) if model_dir else (self.cfg.SAVED_MODELS_DIR / "current")
        self.model = None
        self.schema = None
        self.builder = None
        self.metadata = {}
        self.model_version = "xgb-v1"

        self.load(self.model_dir)

    def load(self, model_dir: Path) -> None:
        """Load trained model, authoritative feature schema, and model metadata."""
        model_path = model_dir / "landslide_xgboost.json"
        schema_path = model_dir / "feature_schema.json"
        meta_path = model_dir / "model_metadata.json"

        if not model_path.exists():
            raise FileNotFoundError(f"Trained XGBoost model file not found at: {model_path}")
        if not schema_path.exists():
            raise FileNotFoundError(f"Feature schema file not found at: {schema_path}")

        self.schema = FeatureSchema.load(schema_path)
        self.model = load_xgboost_model(model_path)
        self.builder = FeatureBuilder(schema=self.schema)

        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                    self.model_version = self.metadata.get("model_version", "xgb-v1")
            except Exception as e:
                logger.warning(f"Could not load model metadata: {e}")

        logger.info(f"LandslidePredictor loaded model version '{self.model_version}' from {model_dir}")

    def _validate_input_record(self, record: Dict[str, Any]) -> None:
        """Validate input record for edge case constraints."""
        if not isinstance(record, dict):
            raise ValueError("Input sample record must be a valid JSON dictionary.")

        loc = record.get("location", {})
        if isinstance(loc, dict) and "latitude" in loc and "longitude" in loc:
            try:
                lat = float(loc["latitude"])
                lon = float(loc["longitude"])
                if not (-90.0 <= lat <= 90.0):
                    raise ValueError(f"Invalid latitude value: {lat}")
                if not (-180.0 <= lon <= 180.0):
                    raise ValueError(f"Invalid longitude value: {lon}")
            except (ValueError, TypeError) as err:
                raise ValueError(f"Invalid location coordinates: {err}")

        # Check AlphaEarth embedding dimension if present
        ae = record.get("alphaearth", {})
        if isinstance(ae, dict) and "embedding" in ae:
            emb = ae["embedding"]
            if isinstance(emb, list) and len(emb) > 0 and len(emb) != self.cfg.ALPHAEARTH_EMBEDDING_DIM:
                raise ValueError(
                    f"AlphaEarth embedding dimension mismatch: expected {self.cfg.ALPHAEARTH_EMBEDDING_DIM}, got {len(emb)}"
                )

    def predict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate landslide risk for a single sample record.

        Returns:
            Structured prediction dictionary matching Phase 12 schema.
        """
        self._validate_input_record(record)

        X = self.builder.transform_record(record)
        X_2d = X.reshape(1, -1)

        # Verify schema match
        self.schema.validate_feature_schema(self.builder.feature_names)

        probs = self.model.predict_proba(X_2d)[0]
        proba = float(probs[1]) if len(probs) > 1 else float(probs[0])
        score, level = compute_risk_level(proba)
        now_str = datetime.now(timezone.utc).isoformat()

        return {
            "landslide_probability": round(proba, 4),
            "risk_score": score,
            "risk_level": level,
            "model_version": self.model_version,
            "alphaearth_status": self.metadata.get("alphaearth_status", "VERIFIED"),
            "timestamp": now_str
        }


    def predict_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate landslide risk in batch mode for multiple sample records."""
        if not records:
            return []

        for rec in records:
            self._validate_input_record(rec)

        X_mat, _ = self.builder.transform_records(records)
        self.schema.validate_feature_schema(self.builder.feature_names)

        probs = self.model.predict_proba(X_mat)[:, 1]
        results = []
        now_str = datetime.now(timezone.utc).isoformat()

        for proba in probs:
            p_val = float(proba)
            score, level = compute_risk_level(p_val)
            results.append({
                "landslide_probability": round(p_val, 4),
                "risk_score": score,
                "risk_level": level,
                "model_version": self.model_version,
                "alphaearth_status": self.metadata.get("alphaearth_status", "VERIFIED"),
                "timestamp": now_str
            })


        return results

