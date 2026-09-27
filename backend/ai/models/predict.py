"""
Local inference CLI script for landslide risk prediction.
Command:
    python -m models.predict --input dataset/test_sample.json --model_dir saved_models/
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Union

from ai.config.config import get_default_config, Config
from ai.preprocessing.feature_schema import FeatureSchema
from ai.preprocessing.feature_builder import FeatureBuilder
from ai.models.model_utils import load_xgboost_model, compute_risk_level

logger = logging.getLogger("predict")


class LandslidePredictor:
    """Local inference engine for loading trained models and evaluating single JSON samples."""

    def __init__(self, model_dir: Union[str, Path]) -> None:
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "landslide_xgboost.json"
        self.schema_path = self.model_dir / "feature_schema.json"

        if not self.model_path.exists():
            raise FileNotFoundError(f"Trained model not found at: {self.model_path}")
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Feature schema not found at: {self.schema_path}")

        self.schema = FeatureSchema.load(self.schema_path)
        self.model = load_xgboost_model(self.model_path)
        self.builder = FeatureBuilder(schema=self.schema)

    def predict_sample(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict landslide risk for a single sample dictionary.

        Args:
            record: Raw sample dictionary matching JSON schema.

        Returns:
            Dictionary containing landslide_probability, risk_score, and risk_level.
        """
        X = self.builder.transform_record(record)
        # Reshape to (1, N_features) for batch prediction
        X_2d = X.reshape(1, -1)

        proba = float(self.model.predict_proba(X_2d)[0, 1])
        score, level = compute_risk_level(proba)

        return {
            "landslide_probability": round(proba, 4),
            "risk_score": score,
            "risk_level": level
        }


def main():
    cfg = get_default_config()
    parser = argparse.ArgumentParser(description="Local Landslide Risk Prediction CLI")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to JSON file containing sample data"
    )
    parser.add_argument(
        "--model_dir",
        type=str,
        default=str(cfg.SAVED_MODELS_DIR),
        help="Directory containing trained model and feature schema"
    )

    args = parser.parse_args()
    input_p = Path(args.input)
    model_dir_p = Path(args.model_dir)

    if not input_p.exists():
        print(f"Error: Input JSON file '{input_p}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_p, "r", encoding="utf-8") as f:
            record = json.load(f)
    except Exception as err:
        print(f"Error reading JSON input: {err}", file=sys.stderr)
        sys.exit(1)

    try:
        predictor = LandslidePredictor(model_dir=model_dir_p)
        result = predictor.predict_sample(record)
        # Print formatted JSON result to stdout
        print(json.dumps(result, indent=2))
    except Exception as err:
        print(f"Prediction failed: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
