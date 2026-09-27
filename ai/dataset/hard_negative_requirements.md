# SATHI Hard-Negative Field Data Collection Specification

Requirements and field protocol for acquiring verified hard-negative observations (no landslide occurrence under high-risk environmental conditions) for Model Validation V2.

---

## 1. Definition of a Hard Negative
In landslide risk modeling, a **Hard Negative** is defined as an observation where **no landslide occurred** ($\text{label} = 0$), but environmental and trigger conditions strongly resemble positive landslide environments:

- **Steep Slope**: Terrain inclination between $25^\circ$ and $50^\circ$.
- **Heavy Antecedent Rainfall**: $24\text{h} \ge 50\text{mm}$, $3\text{d} \ge 120\text{mm}$, $7\text{d} \ge 250\text{mm}$.
- **Elevated Soil Saturation**: Volumetric soil moisture $\ge 0.40\text{ m}^3/\text{m}^3$.
- **High Topographic Wetness Index (TWI)**: Concentrated drainage convergence ($\text{TWI} \ge 8.0$).

---

## 2. Field Collection Schema
For each verified no-landslide observation, record:

| Field Name | Type | Range / Description |
|---|---|---|
| `latitude` | float | Decimal degrees ($20^\circ\text{N} - 29^\circ\text{N}$) |
| `longitude` | float | Decimal degrees ($88^\circ\text{E} - 97^\circ\text{E}$) |
| `timestamp` | string | ISO 8601 UTC timestamp |
| `slope` | float | Slope in degrees ($25.0 - 50.0^\circ$) |
| `elevation` | float | Meters above sea level |
| `rain_1h` | float | 1-hour rainfall accumulation (mm) |
| `rain_24h` | float | 24-hour antecedent rainfall accumulation (mm) |
| `rain_3d` | float | 3-day cumulative rainfall (mm) |
| `rain_7d` | float | 7-day cumulative rainfall (mm) |
| `rain_14d` | float | 14-day cumulative rainfall (mm) |
| `soil_moisture` | float | Surface volumetric moisture ($0.0 - 1.0$) |
| `geology_code` | int/str | Formational lithology classification |
| `land_use_code` | int/str | Land cover category |
| `landslide` | int | Strictly `0` (confirmed no landslide) |
| `verification_method` | string | Field Inspection / High-Res Optical Satellite Audit |

---

## 3. Label Integrity Guidelines
1. **No Pseudo-Negatives**: Do not assign $\text{label} = 0$ to unvisited or unverified remote slopes during intense monsoons.
2. **Ground Truth Confirmation**: Confirm absence of slope failure via multi-temporal satellite imagery or local disaster management records.
