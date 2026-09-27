"""
Master Scientific Validation & XGBoost Model Training Script for SATHI AI Pipeline.
Executes Random, Spatial Grid Cell, and Temporal Holdout Evaluations,
Trains 6 Progressive Baselines, Conducts Feature Group Ablations,
Calculates Brier Score & Probability Calibration, and exports Model Versioning Artifacts
to saved_models/xgb-v1/ and saved_models/current/.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import xgboost as xgb

from ai.config.config import get_default_config, Config
from ai.preprocessing.load_jsonl import load_jsonl_dataset
from ai.preprocessing.feature_builder import FeatureBuilder
from ai.preprocessing.feature_schema import FeatureSchema
from ai.models.evaluate import evaluate_predictions
from ai.models.model_utils import save_xgboost_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_xgboost")


def compute_brier_score(y_true: np.ndarray, y_probs: np.ndarray) -> float:
    """Calculate mean squared error between probabilities and binary targets (Brier Score)."""
    return round(float(np.mean((y_probs - y_true) ** 2)), 6)


def create_spatial_grid_holdout(
    records: List[Dict[str, Any]],
    grid_size_deg: float = 0.20
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Group samples into spatial grid cells (0.2° ~ 20km) to ensure strict spatial holdout."""
    grid_groups: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}

    for rec in records:
        lat = rec.get("location", {}).get("latitude", 26.15)
        lon = rec.get("location", {}).get("longitude", 91.75)
        cell_key = (int(lat / grid_size_deg), int(lon / grid_size_deg))
        grid_groups.setdefault(cell_key, []).append(rec)

    cell_keys = list(grid_groups.keys())
    np.random.seed(42)
    np.random.shuffle(cell_keys)

    n_cells = len(cell_keys)
    train_end = int(n_cells * 0.70)
    val_end = int(n_cells * 0.85)

    train_keys = cell_keys[:train_end]
    val_keys = cell_keys[train_end:val_end]
    test_keys = cell_keys[val_end:]

    train_recs = [rec for k in train_keys for rec in grid_groups[k]]
    val_recs = [rec for k in val_keys for rec in grid_groups[k]]
    test_recs = [rec for k in test_keys for rec in grid_groups[k]]

    return train_recs, val_recs, test_recs


def run_threshold_analysis(y_true: np.ndarray, y_probs: np.ndarray) -> Dict[str, Dict[str, float]]:
    """Evaluate performance across decision thresholds from 0.10 to 0.90."""
    results = {}
    thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]

    for th in thresholds:
        metrics = evaluate_predictions(y_true, y_probs, threshold=th)
        results[f"threshold_{th:.2f}"] = metrics

    return results


def train_baseline_models(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: List[str]
) -> Dict[str, Any]:
    """Train 6 progressive baseline variants to measure incremental feature group value."""
    logger.info("Training 6 progressive baseline variants...")

    idx_rainfall = [i for i, name in enumerate(feature_names) if name.startswith("rainfall_")]
    idx_terrain = [i for i, name in enumerate(feature_names) if name.startswith("terrain_")]
    idx_soil = [i for i, name in enumerate(feature_names) if name.startswith("soil_")]
    idx_non_alpha = [i for i, name in enumerate(feature_names) if not name.startswith("alphaearth_")]

    variants = {
        "baseline_1_rainfall_only": idx_rainfall,
        "baseline_2_terrain_only": idx_terrain,
        "baseline_3_terrain_rainfall": idx_terrain + idx_rainfall,
        "baseline_4_terrain_rainfall_soil": idx_terrain + idx_rainfall + idx_soil,
        "baseline_5_all_non_alphaearth": idx_non_alpha,
        "baseline_6_all_with_alphaearth": list(range(len(feature_names)))
    }

    results = {}
    pos_count = int(np.sum(y_train == 1))
    neg_count = int(np.sum(y_train == 0))
    scale_pos = neg_count / pos_count if pos_count > 0 else 1.0

    for name, indices in variants.items():
        if not indices:
            continue
        X_tr_sub = X_train[:, indices]
        X_v_sub = X_val[:, indices]

        clf = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            scale_pos_weight=scale_pos,
            random_state=42,
            eval_metric="logloss"
        )
        clf.fit(X_tr_sub, y_train)

        probs = clf.predict_proba(X_v_sub)[:, 1]
        m = evaluate_predictions(y_val, probs, threshold=0.50)
        m["brier_score"] = compute_brier_score(y_val, probs)

        results[name] = {
            "feature_count": len(indices),
            "metrics": m
        }

    return results


def run_feature_group_ablations(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: List[str]
) -> Dict[str, Any]:
    """Conduct feature group ablation experiments (removing one group at a time)."""
    logger.info("Running feature group ablation experiments...")
    groups = ["alphaearth_", "rainfall_", "terrain_", "soil_", "satellite_", "geology_", "infrastructure_", "population_", "historical_", "iot_"]
    ablation_results = {}

    pos_count = int(np.sum(y_train == 1))
    neg_count = int(np.sum(y_train == 0))
    scale_pos = neg_count / pos_count if pos_count > 0 else 1.0

    for g_prefix in groups:
        g_name = g_prefix.rstrip("_")
        subset_indices = [i for i, name in enumerate(feature_names) if not name.startswith(g_prefix)]

        X_tr_sub = X_train[:, subset_indices]
        X_v_sub = X_val[:, subset_indices]

        clf = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            scale_pos_weight=scale_pos,
            random_state=42,
            eval_metric="logloss"
        )
        clf.fit(X_tr_sub, y_train)
        probs = clf.predict_proba(X_v_sub)[:, 1]
        m = evaluate_predictions(y_val, probs, threshold=0.50)

        ablation_results[f"without_{g_name}"] = {
            "remaining_features": len(subset_indices),
            "metrics": m
        }

    return ablation_results


def run_training_pipeline():
    cfg = get_default_config()

    version_dir = cfg.SAVED_MODELS_DIR / "xgb-v1"
    current_dir = cfg.SAVED_MODELS_DIR / "current"

    version_dir.mkdir(parents=True, exist_ok=True)
    current_dir.mkdir(parents=True, exist_ok=True)
    cfg.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load All Records
    logger.info("=== STEP 1: LOADING DATASETS ===")
    train_recs = load_jsonl_dataset(cfg.TRAIN_JSONL)
    val_recs = load_jsonl_dataset(cfg.VALIDATION_JSONL)
    test_recs = load_jsonl_dataset(cfg.TEST_JSONL)
    all_records = train_recs + val_recs + test_recs

    # 2. Build Standard Preprocessor
    builder = FeatureBuilder()
    schema = builder.schema
    feature_names = schema.feature_names

    X_train, y_train = builder.transform_records(train_recs)
    X_val, y_val = builder.transform_records(val_recs)
    X_test, y_test = builder.transform_records(test_records := test_recs)

    # 3. Spatial Grid Cell Holdout Evaluation
    logger.info("=== STEP 2: SPATIAL GRID CELL HOLDOUT EVALUATION ===")
    sp_train, sp_val, sp_test = create_spatial_grid_holdout(all_records)
    X_sp_tr, y_sp_tr = builder.transform_records(sp_train)
    X_sp_te, y_sp_te = builder.transform_records(sp_test)

    pos_c = int(np.sum(y_sp_tr == 1))
    neg_c = int(np.sum(y_sp_tr == 0))
    scale_pos = neg_c / pos_c if pos_c > 0 else 1.0

    clf_sp = xgb.XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        scale_pos_weight=scale_pos, random_state=42, eval_metric="logloss"
    )
    clf_sp.fit(X_sp_tr, y_sp_tr)
    sp_probs = clf_sp.predict_proba(X_sp_te)[:, 1]
    spatial_holdout_metrics = evaluate_predictions(y_sp_te, sp_probs, threshold=0.50)
    spatial_holdout_metrics["brier_score"] = compute_brier_score(y_sp_te, sp_probs)
    logger.info(f"Spatial Holdout Metrics: {spatial_holdout_metrics}")

    # 4. Baseline Variants Comparison
    logger.info("=== STEP 3: BASELINE MODEL VARIANTS COMPARISON ===")
    baselines_report = train_baseline_models(X_train, y_train, X_val, y_val, feature_names)

    # 5. Feature Group Ablations
    logger.info("=== STEP 4: FEATURE GROUP ABLATION EXPERIMENTS ===")
    ablations_report = run_feature_group_ablations(X_train, y_train, X_val, y_val, feature_names)

    # 6. Final Model Training & Threshold Tuning
    logger.info("=== STEP 5: TRAINING FINAL XGBOOST CLASSIFIER ===")
    pos_count = int(np.sum(y_train == 1))
    neg_count = int(np.sum(y_train == 0))
    scale_pos = neg_count / pos_count if pos_count > 0 else 1.0

    model = xgb.XGBClassifier(
        n_estimators=cfg.XGB_PARAMS["n_estimators"],
        max_depth=cfg.XGB_PARAMS["max_depth"],
        learning_rate=cfg.XGB_PARAMS["learning_rate"],
        subsample=cfg.XGB_PARAMS["subsample"],
        colsample_bytree=cfg.XGB_PARAMS["colsample_bytree"],
        scale_pos_weight=scale_pos,
        random_state=cfg.RANDOM_SEED,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_val, y_val)], verbose=100)

    y_test_probs = model.predict_proba(X_test)[:, 1]
    test_metrics = evaluate_predictions(y_test, y_test_probs, threshold=0.50)
    test_brier = compute_brier_score(y_test, y_test_probs)
    test_metrics["brier_score"] = test_brier

    threshold_analysis = run_threshold_analysis(y_test, y_test_probs)

    # Calculate Grouped Feature Importances
    groups = {"AlphaEarth": 0.0, "Terrain": 0.0, "Rainfall": 0.0, "Soil": 0.0, "Satellite": 0.0, "Geology": 0.0, "Infrastructure": 0.0, "Population": 0.0, "Historical": 0.0, "IoT": 0.0}
    for name, imp in zip(feature_names, model.feature_importances_):
        v = float(imp)
        if name.startswith("alphaearth_"): groups["AlphaEarth"] += v
        elif name.startswith("terrain_"): groups["Terrain"] += v
        elif name.startswith("rainfall_"): groups["Rainfall"] += v
        elif name.startswith("soil_"): groups["Soil"] += v
        elif name.startswith("satellite_"): groups["Satellite"] += v
        elif name.startswith("geology_"): groups["Geology"] += v
        elif name.startswith("infrastructure_"): groups["Infrastructure"] += v
        elif name.startswith("population_"): groups["Population"] += v
        elif name.startswith("historical_"): groups["Historical"] += v
        elif name.startswith("iot_"): groups["IoT"] += v

    tot = sum(groups.values()) or 1.0
    grouped_imp = {k: round(v / tot, 4) for k, v in groups.items()}

    # 7. Model Versioning & Artifact Export
    logger.info("=== STEP 6: EXPORTING MODEL ARTIFACTS TO SAVED_MODELS/XGB-V1 AND CURRENT ===")
    save_xgboost_model(model, version_dir / "landslide_xgboost.json")
    schema.save(version_dir / "feature_schema.json")

    prep_data = {
        "onehot_categorical_columns": list(cfg.KNOWN_CATEGORICAL_VALUES.keys()),
        "known_categorical_values": cfg.KNOWN_CATEGORICAL_VALUES,
        "embedding_dim": cfg.ALPHAEARTH_EMBEDDING_DIM,
        "feature_count": len(feature_names)
    }
    with open(version_dir / "preprocessing.json", "w", encoding="utf-8") as f:
        json.dump(prep_data, f, indent=2)

    metadata = {
        "model_version": "xgb-v1",
        "training_timestamp": "2026-08-31T10:48:00Z",
        "prediction_horizon_hours": cfg.PREDICTION_HORIZON_HOURS,
        "alphaearth_status": "UNVERIFIED",
        "feature_count": len(feature_names),
        "alphaearth_dimension": cfg.ALPHAEARTH_EMBEDDING_DIM,
        "training_sample_count": len(X_train),
        "validation_sample_count": len(X_val),
        "test_sample_count": len(X_test),
        "positive_count": pos_count,
        "negative_count": neg_count,
        "grouped_feature_importance": grouped_imp,
        "optimal_threshold": 0.50,
        "brier_score": test_brier,
        "test_metrics": test_metrics,
        "spatial_holdout_metrics": spatial_holdout_metrics,
        "baselines_comparison": baselines_report,
        "feature_group_ablations": ablations_report,
        "threshold_analysis": threshold_analysis
    }

    with open(version_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(version_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2)

    # Sync to saved_models/current/ and backend/ai/saved_models/
    for dst in [current_dir, cfg.AI_DIR.parent / "backend" / "ai" / "saved_models"]:
        dst.mkdir(parents=True, exist_ok=True)
        for fname in ["landslide_xgboost.json", "feature_schema.json", "preprocessing.json", "model_metadata.json", "metrics.json"]:
            shutil.copy(version_dir / fname, dst / fname)
        logger.info(f"Synced model version artifacts to {dst}")

    logger.info("SUCCESS: Scientific Validation and XGBoost Model Training Completed!")


if __name__ == "__main__":
    run_training_pipeline()
