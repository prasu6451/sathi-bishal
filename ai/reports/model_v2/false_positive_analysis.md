# SATHI Hard-Negative False Positive Forensic Analysis

## Executive Finding
Under synthetic hard-negative stress testing (steep slope $25^\circ-48^\circ$, 24h rainfall $50-150	ext{mm}$, $y=0$), `xgb-v1` yielded a False Positive Rate of **100.0%** (300/300 records incorrectly flagged as landslide hazards).

## Root Cause Analysis
1. **Topographic & Hydrologic Separability**: In the baseline training set, slope $> 25^\circ$ paired with $24	ext{h rain} > 50	ext{mm}$ overwhelmingly correlated with positive landslide events ($y=1$).
2. **Lack of Hard Negatives in Training**: The baseline model was not trained on steep, saturated slopes that remained stable.
3. **Mitigation Recommendation**: Retain `xgb-v1` as prototype baseline, but collect real-world hard negatives before civil defense operational deployment.
