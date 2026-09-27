"""
Dataset validation CLI tool for checking JSONL integrity, coordinates, labels, and embedding dimensions.
Command: python -m preprocessing.validate_dataset
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime

from ai.config.config import get_default_config
from ai.preprocessing.load_jsonl import load_jsonl_dataset

logger = logging.getLogger("validate_dataset")


def validate_timestamp(ts_str: Any) -> bool:
    """Validate ISO timestamp format."""
    if not isinstance(ts_str, str):
        return False
    try:
        # Support ISO 8601 format
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        datetime.fromisoformat(ts_str)
        return True
    except Exception:
        return False


def validate_dataset_file(file_path: Path, expected_dim: int = 64) -> Dict[str, Any]:
    """
    Perform validation checks on a JSONL dataset file.

    Args:
        file_path: Path to dataset file.
        expected_dim: Expected AlphaEarth embedding dimension (default 64).

    Returns:
        Dictionary of validation metrics.
    """
    records = load_jsonl_dataset(file_path, ignore_errors=True)
    total_samples = len(records)

    positive_landslides = 0
    negative_landslides = 0
    missing_labels = 0
    invalid_coords = 0
    missing_rainfall = 0
    missing_alphaearth = 0
    malformed_alphaearth = 0
    invalid_timestamps = 0
    duplicate_ids = 0

    seen_ids: Set[str] = set()
    warnings: List[str] = []

    for i, record in enumerate(records):
        # 1. Sample ID check
        sample_id = record.get("id", f"auto_{i}")
        if sample_id in seen_ids:
            duplicate_ids += 1
        else:
            seen_ids.add(sample_id)

        # 2. Location check
        loc = record.get("location")
        if not isinstance(loc, dict):
            invalid_coords += 1
        else:
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if (
                lat is None or lon is None or
                not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or
                lat < -90.0 or lat > 90.0 or lon < -180.0 or lon > 180.0
            ):
                invalid_coords += 1

        # 3. Timestamp check
        ts = record.get("timestamp")
        if not validate_timestamp(ts):
            invalid_timestamps += 1

        # 4. Label check
        label_dict = record.get("label")
        if not isinstance(label_dict, dict) or "landslide" not in label_dict:
            missing_labels += 1
        else:
            lbl = label_dict.get("landslide")
            if lbl == 1:
                positive_landslides += 1
            elif lbl == 0:
                negative_landslides += 1
            else:
                missing_labels += 1

        # 5. Rainfall check
        rainfall = record.get("rainfall")
        if not isinstance(rainfall, dict) or not any(k in rainfall for k in ["rain_24h", "rain_1h"]):
            missing_rainfall += 1

        # 6. AlphaEarth check
        alpha = record.get("alphaearth")
        if not isinstance(alpha, dict) or "embedding" not in alpha:
            missing_alphaearth += 1
        else:
            emb = alpha.get("embedding")
            if not isinstance(emb, list) or len(emb) != expected_dim:
                malformed_alphaearth += 1

    pos_ratio = (
        (positive_landslides / (positive_landslides + negative_landslides)) * 100.0
        if (positive_landslides + negative_landslides) > 0 else 0.0
    )

    if pos_ratio < 15.0 or pos_ratio > 85.0:
        warnings.append("Class imbalance detected.")

    if invalid_coords > 0:
        warnings.append(f"{invalid_coords} samples have invalid coordinates.")

    if malformed_alphaearth > 0:
        warnings.append(f"{malformed_alphaearth} samples have non-{expected_dim} embedding dimensions.")

    return {
        "total_samples": total_samples,
        "positive": positive_landslides,
        "negative": negative_landslides,
        "positive_ratio": pos_ratio,
        "missing_labels": missing_labels,
        "invalid_coords": invalid_coords,
        "missing_rainfall": missing_rainfall,
        "missing_alphaearth": missing_alphaearth,
        "malformed_alphaearth": malformed_alphaearth,
        "duplicate_ids": duplicate_ids,
        "invalid_timestamps": invalid_timestamps,
        "embedding_dim": expected_dim,
        "warnings": warnings
    }


def print_validation_report(stats: Dict[str, Any]) -> None:
    """Print clean CLI report matching prompt requirement."""
    print("Dataset validation")
    print("------------------")
    print(f"Samples: {stats['total_samples']:,}\n")
    print("Positive landslide:")
    print(f"{stats['positive']:,}\n")
    print("Negative:")
    print(f"{stats['negative']:,}\n")
    print("Positive ratio:")
    print(f"{stats['positive_ratio']:.2f}%\n")
    print("Invalid coordinates:")
    print(f"{stats['invalid_coords']}\n")
    print("Missing rainfall:")
    print(f"{stats['missing_rainfall']}\n")
    print("Missing AlphaEarth:")
    print(f"{stats['missing_alphaearth']}\n")
    print("Embedding dimension:")
    print(f"{stats['embedding_dim']}\n")
    print("Warnings:")
    if stats["warnings"]:
        for w in stats["warnings"]:
            print(f"- {w}")
    else:
        print("None")
    print()


def main():
    cfg = get_default_config()
    parser = argparse.ArgumentParser(description="Validate JSONL Landslide Dataset")
    parser.add_argument(
        "--input",
        type=str,
        default=str(cfg.TRAIN_JSONL),
        help="Path to JSONL dataset file"
    )
    args = parser.parse_args()

    file_path = Path(args.input)
    if not file_path.exists():
        print(f"Error: Target dataset file '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    stats = validate_dataset_file(file_path, expected_dim=cfg.ALPHAEARTH_EMBEDDING_DIM)
    print_validation_report(stats)


if __name__ == "__main__":
    main()
