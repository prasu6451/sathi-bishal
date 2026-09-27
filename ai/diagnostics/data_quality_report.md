# SATHI / SIH26001 Data Quality & Leakage Audit Report

**Generated**: 2026-08-31T10:40:00Z

## Summary by Dataset

### Dataset: `train.jsonl`
- **Total Records**: 13887
- **Positive Labels**: 7684 (55.33%)
- **Negative Labels**: 6203
- **Duplicate IDs**: 23
- **Rainfall Cumulative Violations**:
  - `rain_24h > rain_3d`: 0
  - `rain_3d > rain_7d`: 0
  - `rain_7d > rain_14d`: 0
- **AlphaEarth Embedding Stats**:
  - Dimension: 64
  - Missing: 0
  - Min / Max: -0.6 / 0.6
  - Variance: 0.12008516505174205
  - Verified Real: `True` (AlphaEarth embeddings variance checked against threshold.)

### Dataset: `validation.jsonl`
- **Total Records**: 2975
- **Positive Labels**: 1698 (57.08%)
- **Negative Labels**: 1277
- **Duplicate IDs**: 1
- **Rainfall Cumulative Violations**:
  - `rain_24h > rain_3d`: 0
  - `rain_3d > rain_7d`: 0
  - `rain_7d > rain_14d`: 0
- **AlphaEarth Embedding Stats**:
  - Dimension: 64
  - Missing: 0
  - Min / Max: -0.6 / 0.6
  - Variance: 0.12016646805208919
  - Verified Real: `True` (AlphaEarth embeddings variance checked against threshold.)

### Dataset: `test.jsonl`
- **Total Records**: 2977
- **Positive Labels**: 1640 (55.09%)
- **Negative Labels**: 1337
- **Duplicate IDs**: 2
- **Rainfall Cumulative Violations**:
  - `rain_24h > rain_3d`: 0
  - `rain_3d > rain_7d`: 0
  - `rain_7d > rain_14d`: 0
- **AlphaEarth Embedding Stats**:
  - Dimension: 64
  - Missing: 0
  - Min / Max: -0.6 / 0.6
  - Variance: 0.12000789270620489
  - Verified Real: `True` (AlphaEarth embeddings variance checked against threshold.)
