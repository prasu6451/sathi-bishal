# SATHI Model Card V2 — `xgb-v1` Baseline Prototype

Model Card for the **SATHI / SIH26001** Landslide Early-Warning Classifier (`xgb-v1`).

---

## 1. Model Details
- **Developer**: SATHI Engineering Team / SIH26001
- **Model Type**: Gradient Boosted Decision Trees (`XGBClassifier`)
- **Version**: `xgb-v1`
- **Feature Vector Length**: 109 features
- **Decision Threshold**: 0.50 ($p \ge 0.75 \rightarrow \text{CRITICAL}$, $0.50 \le p < 0.75 \rightarrow \text{HIGH}$, $0.25 \le p < 0.50 \rightarrow \text{MODERATE}$, $p < 0.25 \rightarrow \text{LOW}$)
- **AlphaEarth Status**: `UNVERIFIED` (Satellite foundation embedding uses placeholder status)

---

## 2. Intended Use
- **Primary Use**: Prototype real-time early warning and spatial risk monitoring for North-East India.
- **Out of Scope**: Direct civil defense evacuation ordering without independent geotechnical field verification.

---

## 3. Performance Summary
- **Random Test Split**: F1 = 1.0000, ROC-AUC = 1.0000, PR-AUC = 1.0000
- **Spatial Holdout**: F1 = 1.0000, ROC-AUC = 1.0000
- **Temporal Holdout**: F1 = 1.0000, ROC-AUC = 1.0000
- **Hard-Negative Stress Test**: FPR = 82.3% (Model exhibits high sensitivity to steep wet slopes where no failure occurred)

---

## 4. Operational Risk & Guidance
Treat `xgb-v1` as a high-sensitivity prototype. High probabilities reflect severe environmental hazard potential (steep slope + heavy rain), warranting ground monitoring.
