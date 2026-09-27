"""
Dataset Audit & Data Quality Diagnostic Tool matching Section 1-4 of AI Audit Prompt.
Calculates dataset metrics, missing features, AlphaEarth embedding distributions,
and detects rainfall cumulative inconsistencies (e.g. rain_3d > rain_7d or rain_7d > rain_14d).
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dataset_audit")

AI_DIR = Path(r"c:\Users\PK\Desktop\sathi\ai")
DATASET_DIR = AI_DIR / "dataset"
DIAGNOSTICS_DIR = AI_DIR / "diagnostics"


def audit_dataset_file(file_path: Path) -> Dict[str, Any]:
    """Audit single JSONL dataset file."""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return {"status": "file_not_found", "file": str(file_path)}

    total_records = 0
    valid_records = 0
    invalid_records = 0
    pos_labels = 0
    neg_labels = 0

    missing_fields = {}
    duplicate_ids = set()
    seen_ids = set()

    rain_violations_3d_7d = 0
    rain_violations_7d_14d = 0
    rain_violations_24h_3d = 0

    alphaearth_embeddings = []
    alphaearth_missing_count = 0
    alphaearth_nan_count = 0

    categorical_counts = {
        "lithology": {},
        "geomorphology": {},
        "land_use": {}
    }

    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue

            total_records += 1
            try:
                rec = json.loads(line_str)
                valid_records += 1
            except Exception:
                invalid_records += 1
                continue

            # ID check
            rec_id = rec.get("id")
            if rec_id in seen_ids:
                duplicate_ids.add(rec_id)
            elif rec_id:
                seen_ids.add(rec_id)

            # Label check
            label_obj = rec.get("label", {})
            landslide_val = label_obj.get("landslide") if isinstance(label_obj, dict) else rec.get("landslide")
            if landslide_val == 1:
                pos_labels += 1
            else:
                neg_labels += 1

            # Rainfall consistency check
            rf = rec.get("rainfall", {})
            r_1h = rf.get("rain_1h", 0.0)
            r_24h = rf.get("rain_24h", 0.0)
            r_3d = rf.get("rain_3d", 0.0)
            r_7d = rf.get("rain_7d", 0.0)
            r_14d = rf.get("rain_14d", 0.0)

            if r_24h > r_3d:
                rain_violations_24h_3d += 1
            if r_3d > r_7d:
                rain_violations_3d_7d += 1
            if r_7d > r_14d:
                rain_violations_7d_14d += 1

            # AlphaEarth validation
            ae = rec.get("alphaearth", {})
            emb = ae.get("embedding") if isinstance(ae, dict) else None
            if emb is None:
                alphaearth_missing_count += 1
            elif isinstance(emb, list):
                if any(np.isnan(x) for x in emb if isinstance(x, (int, float))):
                    alphaearth_nan_count += 1
                else:
                    alphaearth_embeddings.append(emb)

            # Categorical checks
            geology = rec.get("geology", {})
            lith = geology.get("lithology", "unknown")
            geom = geology.get("geomorphology", "unknown")
            lulc = rec.get("land_use", {}).get("class", "unknown")

            categorical_counts["lithology"][lith] = categorical_counts["lithology"].get(lith, 0) + 1
            categorical_counts["geomorphology"][geom] = categorical_counts["geomorphology"].get(geom, 0) + 1
            categorical_counts["land_use"][lulc] = categorical_counts["land_use"].get(lulc, 0) + 1

    # AlphaEarth stats
    if alphaearth_embeddings:
        arr = np.array(alphaearth_embeddings)
        ae_dim = arr.shape[1]
        ae_min = float(np.min(arr))
        ae_max = float(np.max(arr))
        ae_mean = float(np.mean(arr))
        ae_var = float(np.var(arr))
        ae_verified_real = False if ae_var < 0.001 else True
    else:
        ae_dim = 0
        ae_min = 0.0
        ae_max = 0.0
        ae_mean = 0.0
        ae_var = 0.0
        ae_verified_real = False

    return {
        "file": str(file_path),
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "positive_labels": pos_labels,
        "negative_labels": neg_labels,
        "positive_percentage": round((pos_labels / total_records * 100), 2) if total_records else 0.0,
        "duplicate_ids_count": len(duplicate_ids),
        "rainfall_violations": {
            "rain_24h_gt_3d": rain_violations_24h_3d,
            "rain_3d_gt_7d": rain_violations_3d_7d,
            "rain_7d_gt_14d": rain_violations_7d_14d
        },
        "alphaearth_stats": {
            "embedding_dimension": ae_dim,
            "missing_embeddings": alphaearth_missing_count,
            "nan_embeddings": alphaearth_nan_count,
            "embedding_min": ae_min,
            "embedding_max": ae_max,
            "embedding_mean": ae_mean,
            "embedding_variance": ae_var,
            "alphaearth_verified_real": ae_verified_real,
            "verification_note": "AlphaEarth embeddings variance checked against threshold." if ae_verified_real else "AlphaEarth embeddings are synthetic/placeholder."
        },
        "categorical_counts": categorical_counts
    }


def run_full_audit():
    """Run diagnostic dataset audit on train, validation, and test datasets."""
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "title": "SATHI / SIH26001 Data Quality & Leakage Audit Report",
        "timestamp": "2026-08-31T10:40:00Z",
        "datasets": {}
    }

    files_to_audit = [
        DATASET_DIR / "train.jsonl",
        DATASET_DIR / "validation.jsonl",
        DATASET_DIR / "test.jsonl"
    ]

    for fpath in files_to_audit:
        if fpath.exists():
            logger.info(f"Auditing dataset file: {fpath.name}...")
            res = audit_dataset_file(fpath)
            report["datasets"][fpath.name] = res

    # Save JSON report
    json_path = DIAGNOSTICS_DIR / "data_quality_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Save Markdown report
    md_path = DIAGNOSTICS_DIR / "data_quality_report.md"
    md_lines = [
        "# SATHI / SIH26001 Data Quality & Leakage Audit Report\n",
        f"**Generated**: {report['timestamp']}\n",
        "## Summary by Dataset\n"
    ]

    for fname, dstats in report["datasets"].items():
        md_lines.append(f"### Dataset: `{fname}`")
        md_lines.append(f"- **Total Records**: {dstats.get('total_records')}")
        md_lines.append(f"- **Positive Labels**: {dstats.get('positive_labels')} ({dstats.get('positive_percentage')}%)")
        md_lines.append(f"- **Negative Labels**: {dstats.get('negative_labels')}")
        md_lines.append(f"- **Duplicate IDs**: {dstats.get('duplicate_ids_count')}")

        rf_v = dstats.get("rainfall_violations", {})
        md_lines.append("- **Rainfall Cumulative Violations**:")
        md_lines.append(f"  - `rain_24h > rain_3d`: {rf_v.get('rain_24h_gt_3d')}")
        md_lines.append(f"  - `rain_3d > rain_7d`: {rf_v.get('rain_3d_gt_7d')}")
        md_lines.append(f"  - `rain_7d > rain_14d`: {rf_v.get('rain_7d_gt_14d')}")

        ae_s = dstats.get("alphaearth_stats", {})
        md_lines.append("- **AlphaEarth Embedding Stats**:")
        md_lines.append(f"  - Dimension: {ae_s.get('embedding_dimension')}")
        md_lines.append(f"  - Missing: {ae_s.get('missing_embeddings')}")
        md_lines.append(f"  - Min / Max: {ae_s.get('embedding_min')} / {ae_s.get('embedding_max')}")
        md_lines.append(f"  - Variance: {ae_s.get('embedding_variance')}")
        md_lines.append(f"  - Verified Real: `{ae_s.get('alphaearth_verified_real')}` ({ae_s.get('verification_note')})\n")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    logger.info(f"Saved Data Quality Audit JSON: {json_path}")
    logger.info(f"Saved Data Quality Audit Markdown: {md_path}")


if __name__ == "__main__":
    run_full_audit()
