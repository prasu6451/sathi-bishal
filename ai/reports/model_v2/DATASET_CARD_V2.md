# SATHI Dataset Card V2 — North-East India Landslide Corpus

Dataset Specification and Audit for **SATHI / SIH26001** Landslide Risk Corpus (`dataset-v2`).

---

## 1. Dataset Overview
- **Total Records**: 19,839 records
  - `train.jsonl`: 13,887 records
  - `validation.jsonl`: 2,975 records
  - `test.jsonl`: 2,977 records
  - `hard_negative_stress_test.jsonl`: 300 records (Synthetic Stress Test)
- **Spatial Coverage**: 8 North-Eastern States of India (Assam, Meghalaya, Arunachal Pradesh, Sikkim, Manipur, Mizoram, Nagaland, Tripura).
- **Target Label**: `label.landslide` ($0 = \text{No Landslide}$, $1 = \text{Landslide}$).

---

## 2. Forensic Distribution Summary
- **Slope Distribution**:
  - Positive Class ($y=1$): Mean $34.2^\circ$, Range $25.0^\circ - 52.0^\circ$
  - Negative Class ($y=0$): Mean $8.5^\circ$, Range $2.0^\circ - 15.0^\circ$
- **24h Antecedent Rainfall**:
  - Positive Class ($y=1$): Mean $88.5\text{mm}$, Range $52.9 - 153.1\text{mm}$
  - Negative Class ($y=0$): Mean $4.2\text{mm}$, Range $0.3 - 18.7\text{mm}$

---

## 3. Known Biases & Data Limitations
1. **Class Separability Bias**: Baseline training records show near-complete separation in slope ($>25^\circ$) and 24h rainfall ($>50\text{mm}$) between positive and negative classes.
2. **Hard Negative Gap**: Baseline dataset contains few stable steep slopes under heavy rain. Hard negative collection protocol specified in `ai/dataset/hard_negative_requirements.md`.
