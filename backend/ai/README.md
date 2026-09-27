# SIH26001 — AI Landslide Early-Warning & Risk-Monitoring System

This package provides the standalone AI/ML training, feature engineering, dataset validation, evaluation, and local inference pipeline for the **SIH26001 Landslide Early-Warning & Risk-Monitoring System**.

> **Note**: This directory strictly contains the AI/ML modeling pipeline. REST API wrappers (FastAPI), web frontends, database integrations, MQTT servers, and cloud deployment manifests are handled separately outside this package.

---

## 1. Project Objective

The system predicts the probability and risk level of landslide occurrences at specific geographic locations using heterogeneous geospatial, satellite, hydrometeorological, and socio-infrastructure features.

Primary Target Outputs:
- `landslide_probability`: Float probability index `[0.0, 1.0]`
- `risk_score`: Integer score `[0, 100]`
- `risk_level`: Configurable risk category (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)

---

## 2. Model Architecture & AlphaEarth Role

The system utilizes **AlphaEarth Foundations** pretrained satellite representations combined with tabular domain-engineered features fed into a high-performance **XGBoost Classifier**.

```
[AlphaEarth 64-dim Embeddings] + [Terrain, Rainfall, Soil, Geology, Spatial, IoT]
                                       ↓
                           XGBoost Classifier Model
                                       ↓
              Landslide Probability → Risk Score & Category
```

### AlphaEarth Strategy:
- **No Fine-Tuning**: AlphaEarth Foundation embeddings are treated as fixed 64-dimensional feature representations (`alphaearth_0` .. `alphaearth_63`).
- **Feature Fusion**: Flattened AlphaEarth embeddings are concatenated directly with domain-engineered features prior to model training.

---

## 3. Directory Structure

```
ai/
├── README.md                           # Master documentation
├── requirements.txt                    # Project Python dependencies
├── .gitignore                          # Git ignore rules for datasets & models
│
├── config/
│   ├── __init__.py
│   └── config.py                       # Master configuration parameters & thresholds
│
├── dataset/
│   ├── README.md                       # Data formatting guidelines
│   ├── raw/                            # Raw data store
│   ├── processed/                      # Preprocessed output matrices
│   ├── train.jsonl                     # Master training set
│   ├── validation.jsonl                # Temporal/spatial validation set
│   └── test.jsonl                      # Held-out test set
│
├── data_collection/
│   ├── __init__.py
│   ├── alphaearth/                     # Earth Engine AlphaEarth extraction
│   │   ├── README.md
│   │   └── export_alphaearth.py
│   ├── rainfall/                       # Antecedent & cumulative rainfall features
│   │   └── rainfall_features.py
│   ├── terrain/                        # Topographic & TWI feature tools
│   │   └── terrain_features.py
│   └── gis/                            # Proximity & spatial features
│       └── spatial_features.py
│
├── preprocessing/
│   ├── __init__.py
│   ├── load_jsonl.py                   # JSONL dataset loader & writer
│   ├── validate_dataset.py             # CLI dataset validator tool
│   ├── feature_schema.py               # Serialized schema model
│   ├── feature_builder.py              # Feature matrix extractor & encoder
│   └── preprocess.py                   # Pipeline workflow orchestrator
│
├── models/
│   ├── __init__.py
│   ├── train_xgboost.py                # Model training CLI
│   ├── evaluate.py                     # Metric evaluation suite
│   ├── predict.py                      # Local JSON inference CLI
│   └── model_utils.py                  # Persistence & plot utilities
│
├── saved_models/
│   ├── .gitkeep
│   ├── README.md
│   ├── landslide_xgboost.json          # Trained XGBoost model artifact
│   └── feature_schema.json             # Serialized feature ordering schema
│
├── experiments/
│   ├── README.md
│   └── results/                        # Evaluation metrics & importances
│
└── tests/                              # Standalone unit tests (no GEE required)
    ├── __init__.py
    ├── test_jsonl.py
    ├── test_features.py
    └── test_model.py
```

---

## 4. Master JSONL Data Format

The master dataset format is **JSONL** (JSON Lines). Each line represents one spatial-temporal record:

```json
{
  "id": "sample_000001",
  "location": { "latitude": 30.3165, "longitude": 78.0322 },
  "timestamp": "2025-08-20T12:00:00Z",
  "alphaearth": { "embedding": [0.123, -0.382, 0.551, "... 64 floats ..."] },
  "terrain": { "elevation": 1820.4, "slope": 34.7, "aspect": 210.3, "curvature": 0.18, "twi": 7.4 },
  "rainfall": { "rain_1h": 18.2, "rain_24h": 84.5, "rain_3d": 162.2, "rain_7d": 280.1, "rain_14d": 421.3 },
  "soil": { "moisture_0_7cm": 0.42, "moisture_7_28cm": 0.38 },
  "satellite": { "ndvi": 0.62, "sar_displacement": -12.4 },
  "geology": { "lithology": "metamorphic_rock", "geomorphology": "steep_slope", "lineament_distance_m": 1200.4 },
  "infrastructure": { "distance_to_road_m": 83.2, "distance_to_stream_m": 94.1, "distance_to_bridge_m": 1500.0, "distance_to_hospital_m": 4200.0, "distance_to_village_m": 420.0 },
  "population": { "density": 342.0 },
  "land_use": { "class": "forest" },
  "historical": { "previous_landslide": true, "landslide_count_nearby": 3 },
  "iot": { "rainfall_mm": 18.2, "soil_moisture": 0.43 },
  "citizen_report": { "reported": false, "severity": 0 },
  "label": { "landslide": 1, "risk_level": "HIGH", "risk_score": 0.82 }
}
```

---

## 5. Data Leakage Prevention

Landslide prediction models are susceptible to **spatial** and **temporal leakage**:

1. **Temporal Leakage**:
   - Never incorporate satellite imagery, rainfall measurements, or citizen reports generated **after** the prediction timestamp.
   - Ground truth post-event disaster surveys must NOT be included as input features.

2. **Spatial Leakage**:
   - Random cross-validation splits across adjacent grid cells cause data leakage because contiguous terrain shares identical geological attributes.
   - Use **Spatial Block Split** or **Held-Out Geographic Region Split** for validation and test splits.

---

## 6. Earth Engine Authentication & Setup

To extract live AlphaEarth embeddings using Google Earth Engine:

1. Install Google Earth Engine API:
   ```bash
   pip install earthengine-api
   ```
2. Authenticate CLI:
   ```bash
   earthengine authenticate
   ```
3. Export Earth Engine Cloud Project ID:
   ```bash
   export EARTHENGINE_PROJECT="your-gee-project-id"
   ```

---

## 7. Execution Commands

### Installation
```bash
pip install -r requirements.txt
```

### Run Unit Tests
```bash
pytest tests/
```

### Validate Dataset
```bash
python -m preprocessing.validate_dataset --input dataset/train.jsonl
```

### Train Model Baseline
```bash
python -m models.train_xgboost \
    --train dataset/train.jsonl \
    --validation dataset/validation.jsonl \
    --output saved_models/
```

### Local JSON Inference
```bash
python -m models.predict --input dataset/test_sample.json --model_dir saved_models/
```

Sample output:
```json
{
  "landslide_probability": 0.8842,
  "risk_score": 88,
  "risk_level": "CRITICAL"
}
```

---

## 8. Extension Pathways

- **Adding New Features**: Update `NUMERICAL_FEATURES` or `CATEGORICAL_COLUMNS` in `config/config.py` and implement extraction in `FeatureBuilder.extract_sample_features()`.
- **Replacing XGBoost**: Maintain the `FeatureBuilder` matrix interface `(X, y)` and implement new model architectures (e.g. PyTorch neural fusion) under `models/`.
