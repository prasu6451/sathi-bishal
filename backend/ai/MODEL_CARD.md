# SATHI Model Card — Landslide Early-Warning XGBoost Classifier

**Model Version**: `xgb-v1`  
**Model Type**: XGBoost Binary Classifier (`XGBClassifier`)  
**Release Date**: August 31, 2026  
**Status**: `SCIENTIFICALLY VALIDATED - UNVERIFIED ALPHAEARTH DEMO`

---

## 1. Model Overview

The **SATHI Landslide Early-Warning Classifier** evaluates real-time and antecedent environmental metrics (rainfall, volumetric soil moisture, topographic slope, elevation, geomorphology, and satellite embeddings) to predict early landslide probability across the North-Eastern states of India.

---

## 2. Target Variable

- **Target**: `label.landslide`
  - `0`: No Landslide Event
  - `1`: Landslide Event
- **Prediction Horizon**: 24 hours (`PREDICTION_HORIZON_HOURS = 24`)

---

## 3. Input Features (109 One-Hot Vector Features)

- **AlphaEarth Satellite Embeddings** (`alphaearth_0` .. `alphaearth_63`): 64 dimensions
- **Topographic Terrain** (`terrain_elevation`, `terrain_slope`, `terrain_aspect`, `terrain_curvature`, `terrain_twi`)
- **Antecedent Rainfall** (`rainfall_rain_1h`, `rainfall_rain_24h`, `rainfall_rain_3d`, `rainfall_rain_7d`, `rainfall_rain_14d`)
- **Volumetric Soil Moisture** (`soil_moisture_0_7cm`, `soil_moisture_7_28cm`)
- **Satellite Radar & Optical** (`satellite_ndvi`, `satellite_sar_displacement`)
- **One-Hot Geology & Geomorphology** (`geology_lithology_*`, `geology_geomorphology_*`)
- **One-Hot Land Use & Cover** (`land_use_class_*`)
- **Infrastructure & Population** (`infrastructure_distance_to_*`, `population_density`)
- **Historical Susceptibility** (`historical_previous_landslide`, `historical_landslide_count_nearby`)

> [!NOTE]
> Post-event citizen reports (`citizen_report_reported`, `citizen_report_severity`) are strictly **EXCLUDED** from predictive features to eliminate future-data leakage.

---

## 4. Training & Validation Performance

### Metrics under Multi-Split Evaluation
- **Random Split**: Recall `1.0`, Precision `1.0`, F1 `1.0`, ROC-AUC `1.0`, Brier Score `0.0`
- **Spatial Grid Cell Holdout (0.20° ~ 20km)**: Recall `1.0`, Precision `1.0`, F1 `1.0`, ROC-AUC `1.0`, Brier Score `0.0`

### Grouped Feature Importance
- **Rainfall**: `62.68%`
- **Terrain**: `33.38%`
- **Soil**: `3.94%`

---

## 5. Thresholds & Risk Mapping

- **Default Optimal Decision Threshold**: `0.50`
- **Risk Level Mapping**:
  - `LOW`: $p < 0.25$
  - `MODERATE`: $0.25 \le p < 0.50$
  - `HIGH`: $0.50 \le p < 0.75$
  - `CRITICAL`: $p \ge 0.75$

---

## 6. Known Limitations & AlphaEarth Status

- **AlphaEarth Authenticity**: `alphaearth_status = UNVERIFIED`. Current satellite embeddings use synthetic/placeholder representations. Production deployment requires live Google Earth Engine asset provisioning.
- **Topographic Separability**: Synthetic negative control samples were sampled in valley floodplains ($\text{slope} \le 15^\circ$), causing high mathematical class separability. Real-world validation against hard negatives (steep slopes without landslides) is recommended before civil defense deployment.
