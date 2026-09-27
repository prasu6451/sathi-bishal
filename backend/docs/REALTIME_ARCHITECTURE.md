# SATHI Real-Time Technical Architecture

Documenting the complete data flow and execution path for **SATHI / SIH26001** Real-Time Landslide Early-Warning System.

---

## 1. End-to-End Execution Flow

```text
  [ IoT Sensor / Weather Data ]
               │
               ▼
  [ FastAPI REST / Worker Ingestion ]
               │
               ▼
   [ MySQL / SQLite Database ]
               │
               ▼
     [ Feature Assembler ]
    (Combines Static GIS + 
     Dynamic Cumulative Rainfall)
               │
               ▼
    [ Feature Validation ]
  (Checks Completeness & Data Age)
         │           │
         ▼ (Ready)   ▼ (Incomplete / Missing)
  [ AI Predictor ]  [ Status: INSUFFICIENT_DATA ]
   (XGBoost xgb-v1)
         │
         ▼
  [ Risk Score & Level ]
         │
         ├───► [ Store in MySQL risk_predictions ]
         │
         └───► [ WebSocket Manager Broadcast (/ws/risk) ]
                     │
                     ▼
             [ Frontend Live Map ]
```

---

## 2. Dynamic vs Static Feature Separation

1. **Static Environmental Features** (Loaded from GIS / Monitored Locations Store):
   - Terrain: Elevation, Slope, Aspect, Curvature, TWI
   - Geology & Geomorphology: Lithology unit, Landform class
   - Land Use: Forest, Agriculture, Urban, Barren
   - Infrastructure & Population: Distance to roads/streams, Population density
   - AlphaEarth Foundation Embeddings (Currently `UNVERIFIED`)

2. **Dynamic Observation Features** (Ingested in Real-Time):
   - Interval Rainfall Readings (IoT Rain Gauge)
   - Cumulative Antecedent Rainfall Windows (1h, 24h, 3d, 7d, 14d calculated from DB history)
   - Soil Moisture Depths (0-7cm, 7-28cm)
   - Weather Observations & Radar Estimates

---

## 3. Data Freshness & Status Tagging

Every prediction payload is tagged with an authoritative `data_status`:
- `COMPLETE`: All required dynamic observations are fresh and AlphaEarth vectors are available.
- `ALPHAEARTH_UNAVAILABLE`: Environmental features complete, but AlphaEarth satellite vectors use unverified placeholder state.
- `STALE`: Environmental metrics exceed maximum age thresholds (`MAX_SENSOR_DATA_AGE_SECONDS`).
- `INSUFFICIENT_DATA`: Missing required input features (prediction blocked).
