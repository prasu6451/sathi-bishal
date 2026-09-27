# SATHI Dataset Card — North-East India Landslide Risk Dataset

**Dataset Name**: SATHI Real Landslide Inventory & Feature Dataset  
**Geographic Coverage**: North-East India 8 States (Assam, Meghalaya, Arunachal Pradesh, Sikkim, Manipur, Mizoram, Nagaland, Tripura)  
**Total Records**: 19,839 records (`train.jsonl`: 13,887, `validation.jsonl`: 2,975, `test.jsonl`: 2,977)  
**Status**: `PROCESSED WITH CUMULATIVE MONOTONICITY`

---

## 1. Data Sources

1. **Positive Landslide Events**:
   - `01_landslide_inventory_NE_8_states.json` (11,026 real historical landslide records from Geological Survey of India / ISRO landslide atlas across North-East India).
   - `Global_Landslide_Catalog_Export_rows.json` (11,033 NASA Global Landslide Catalog records).
2. **Terrain & Topography**:
   - SRTM GL1 Ellipsoidal DEM rasters (Elevation, Slope, Aspect, Curvature, TWI).
3. **Rainfall & Weather**:
   - NetCDF gridded daily rainfall (`RF25_ind2024_rfp25.nc` & `RF25_ind2025_rfp25.nc`) and live weather observations.
4. **Infrastructure Features**:
   - GeoJSON infrastructure features (`export.geojson`, distance to roads, streams, bridges, hospitals, villages).

---

## 2. Dataset Splits

- **Train Set (70%)**: `13,887` records
- **Validation Set (15%)**: `2,975` records
- **Test Set (15%)**: `2,977` records

---

## 3. Physical Consistency Constraints

- **Rainfall Monotonicity**: All antecedent rainfall windows strictly satisfy:
  $$\text{rain\_14d} \ge \text{rain\_7d} \ge \text{rain\_3d} \ge \text{rain\_24h} \ge \text{rain\_1h}$$
- **Duplicate Records**: 0 exact duplicate records across train/val/test splits.

---

## 4. Known Data Limitations

- **AlphaEarth Source**: `Source Not Verified`. 64-dimensional embedding vectors are synthetic/placeholder representations generated deterministically.
- **Negative Sample Sampling**: Negative samples were generated across low-lying floodplains ($\text{slope} \le 15^\circ$), creating clean separation between positive and negative training classes.
