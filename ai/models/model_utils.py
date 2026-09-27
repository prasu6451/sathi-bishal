"""
Model persistence, risk score calculation, and feature importance visualization helpers.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union

import numpy as np
import pandas as pd
import xgboost as xgb

try:
    from ai.config.config import get_default_config
except ImportError:
    from config.config import get_default_config

logger = logging.getLogger(__name__)


def compute_risk_level(probability: float) -> Tuple[int, str]:
    """
    Convert landslide probability (0.0 - 1.0) into risk score (0 - 100) and risk level.

    Args:
        probability: Float between 0.0 and 1.0.

    Returns:
        Tuple of (risk_score_integer, risk_level_string).
    """
    prob = max(0.0, min(1.0, float(probability)))
    score = int(round(prob * 100.0))

    cfg = get_default_config()
    thresholds = cfg.RISK_LEVEL_THRESHOLDS

    if prob < thresholds["LOW"]:
        level = "LOW"
    elif prob < thresholds["MODERATE"]:
        level = "MODERATE"
    elif prob < thresholds["HIGH"]:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return score, level


def save_xgboost_model(model: xgb.XGBClassifier, save_path: Union[str, Path]) -> None:
    """Save trained XGBoost model to native JSON file."""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Use native JSON format
    model.save_model(str(path))
    logger.info(f"Saved native XGBoost model to: {path}")


def load_xgboost_model(load_path: Union[str, Path]) -> xgb.XGBClassifier:
    """Load native XGBoost model from JSON file."""
    path = Path(load_path)
    if not path.is_file():
        raise FileNotFoundError(f"Model file not found at: {path}")

    model = xgb.XGBClassifier()
    model.load_model(str(path))
    logger.info(f"Successfully loaded XGBoost model from: {path}")
    return model


def export_feature_importances(
    model: xgb.XGBClassifier,
    feature_names: List[str],
    csv_path: Union[str, Path],
    plot_path: Union[str, Path],
    top_n: int = 20
) -> pd.DataFrame:
    """
    Generate, save, and plot feature importances.

    Args:
        model: Trained XGBClassifier.
        feature_names: List of feature names matching model input shape.
        csv_path: Output CSV file path.
        plot_path: Output PNG image path.
        top_n: Number of top features to highlight in plot.

    Returns:
        Pandas DataFrame of feature importances sorted descending.
    """
    try:
        importances = model.feature_importances_
    except AttributeError:
        importances = np.zeros(len(feature_names))

    df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False).reset_index(drop=True)

    csv_p = Path(csv_path)
    csv_p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_p, index=False)
    logger.info(f"Saved feature importances to: {csv_p}")

    # Generate plot if matplotlib/seaborn available
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(10, 6))
        top_df = df.head(top_n)
        sns.barplot(data=top_df, x="importance", y="feature", hue="feature", legend=False, palette="viridis")
        plt.title(f"Top {top_n} Features - Landslide Risk XGBoost Baseline")
        plt.xlabel("Importance Score")
        plt.ylabel("Feature")
        plt.tight_layout()

        plot_p = Path(plot_path)
        plot_p.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(plot_p, dpi=300)
        plt.close()
        logger.info(f"Saved feature importance plot to: {plot_p}")
    except Exception as err:
        logger.warning(f"Could not generate feature importance plot: {err}")

    return df
