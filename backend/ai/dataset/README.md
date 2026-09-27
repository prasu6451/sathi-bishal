# SIH26001 Dataset Storage Directory

This directory stores raw and processed JSONL format data for training, validation, and testing.

## Master Training Format: JSONL

Each line in `train.jsonl`, `validation.jsonl`, and `test.jsonl` is a single spatial-temporal training record.

### Expected JSON Schema:
```json
{
  "id": "sample_000001",
  "location": { "latitude": 30.3165, "longitude": 78.0322 },
  "timestamp": "2025-08-20T12:00:00Z",
  "alphaearth": { "embedding": [0.123, -0.382, ... 64 floats ...] },
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

## Synthetic vs Real Data Notice
Small synthetic dataset samples (`train.jsonl`, `validation.jsonl`, `test.jsonl`) are generated for testing and validation. Production training must use verified geospatial data.
