"""
Evaluation module for computing comprehensive performance metrics for landslide risk model.
Computes Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, Confusion Matrix, and False Negative Rate.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Union, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

logger = logging.getLogger(__name__)


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    threshold: float = 0.5,
    output_json_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Evaluate predicted probabilities against ground truth labels.

    Args:
        y_true: Ground truth binary labels (0 or 1).
        y_pred_proba: Predicted probabilities of landslide occurrence (0.0 to 1.0).
        threshold: Classification decision threshold (default 0.5).
        output_json_path: Optional path to save JSON metrics file.

    Returns:
        Dictionary of computed metrics.
    """
    y_pred = (y_pred_proba >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_pred_proba))
    except Exception:
        roc_auc = 0.0

    try:
        pr_auc = float(average_precision_score(y_true, y_pred_proba))
    except Exception:
        pr_auc = 0.0

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    # Compute False Negative Rate (Critical for Early-Warning Safety)
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        },
        "classification_report": report
    }

    logger.info(
        f"Evaluation Metrics | Recall: {metrics['recall']} | F1: {metrics['f1']} | "
        f"ROC-AUC: {metrics['roc_auc']} | False Negative Rate: {metrics['false_negative_rate']}"
    )

    if output_json_path:
        out_p = Path(output_json_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Saved evaluation metrics to: {out_p}")

    return metrics
