# SATHI 109-Feature Contract & Real-Time Source Specification

Authoritative feature mapping table for all **109 input features** required by XGBoost model version `xgb-v1`.

---

## Feature Groups & Real-Time Sources

| Index Range | Feature Group | Vector Dimension | Static / Dynamic | Real-Time Production Source | Required | Zero-Fabrication Rule |
| --- | --- | --- | --- | --- | --- | --- |
| `0..63` | `alphaearth_0` .. `alphaearth_63` | 64 | Static | `AlphaEarthProvider` (GEE foundation embeddings) | Yes | **Must NOT** use random or zero vectors; flag `ALPHAEARTH_UNAVAILABLE` if missing |
| `64..68` | `terrain_*` (elevation, slope, aspect, curvature, twi) | 5 | Static | Monitored Location GIS / DEM Store | Yes | Must be retrieved from SRTM DEM for location |
| `69..73` | `rainfall_rain_*` (1h, 24h, 3d, 7d, 14d) | 5 | Dynamic | Ingested Sensor / Weather DB History Aggregation | Yes | Must be aggregated from real historical observations ($\text{14d} \ge \text{7d} \ge \text{3d} \ge \text{24h} \ge \text{1h}$) |
| `74..75` | `soil_moisture_0_7cm`, `soil_moisture_7_28cm` | 2 | Dynamic | IoT Soil Sensor / Weather Observation | Yes | Must map physical soil depth measurements |
| `76..77` | `satellite_*` (ndvi, sar_displacement) | 2 | Static / Slow | Sentinel-1/2 GIS Rasters | Yes | Derived from static satellite assets |
| `78` | `geology_lineament_distance_m` | 1 | Static | Geological Survey India (GSI) GIS Layer | Yes | Distance to nearest structural fault line |
| `79..83` | `infrastructure_distance_to_*` (road, stream, bridge, hospital, village) | 5 | Static | OpenStreetMap / State GIS Infrastructure Layer | Yes | Spatial proximity metrics in meters |
| `84` | `population_density` | 1 | Static | WorldPop / Census Spatial Raster | Yes | Persons per $\text{km}^2$ |
| `85..86` | `historical_previous_landslide`, `historical_landslide_count_nearby` | 2 | Static / Historical | Landslide Inventory DB (Time-aware before timestamp $T$) | Yes | Pre-event historical hazard metrics |
| `87..88` | `iot_rainfall_mm`, `iot_soil_moisture` | 2 | Dynamic | Live ESP32 / Gateway IoT Reading | Optional | Direct interval telemetry |
| `89..94` | `geology_lithology_*` (One-Hot 6 categories) | 6 | Static | One-Hot Encoded Lithology Class | Yes | `unknown`, `metamorphic_rock`, `sedimentary_rock`, `igneous_rock`, `unconsolidated_sediment`, `alluvium` |
| `95..101` | `geology_geomorphology_*` (One-Hot 7 categories) | 7 | Static | One-Hot Encoded Landform Class | Yes | `unknown`, `steep_slope`, `gentle_slope`, `valley_bottom`, `ridge`, `scarp`, `plateau` |
| `102..108` | `land_use_class_*` (One-Hot 7 categories) | 7 | Static | One-Hot Encoded LULC Class | Yes | `unknown`, `forest`, `agriculture`, `barren_land`, `built_up`, `shrubland`, `water_body` |

---

## Critical Input Validation Rules

1. **Monotonicity**: Antecedent rainfall windows strictly satisfy:
   $$\text{rain\_14d} \ge \text{rain\_7d} \ge \text{rain\_3d} \ge \text{rain\_24h} \ge \text{rain\_1h}$$
2. **Missing Feature Error Payload**:
   If required environmental features are unavailable, the API returns HTTP 400/422 with:
   ```json
   {
     "status": "INSUFFICIENT_DATA",
     "missing_features": ["rainfall.rain_24h", "soil.moisture_0_7cm"]
   }
   ```
3. **Leakage Elimination**: Citizen reports (`citizen_report.reported`, `citizen_report.severity`) are strictly **EXCLUDED** from the 109 feature vector to prevent target leakage.
