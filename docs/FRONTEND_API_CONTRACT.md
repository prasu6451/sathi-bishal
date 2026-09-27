# SATHI Frontend / Backend API Contract

Full API and WebSocket specification for SATHI real-time landslide monitoring system.

---

## 1. REST API Endpoints

### `GET /health`
- **Response**:
  ```json
  {
    "status": "ok",
    "database": "connected",
    "model": { "loaded": true, "version": "xgb-v1" },
    "websocket_clients": 1,
    "risk_monitor": { "running": true, "interval_seconds": 60 }
  }
  ```

### `GET /api/v1/model/status`
- **Response**:
  ```json
  {
    "model_version": "xgb-v1",
    "loaded": true,
    "feature_count": 109,
    "alphaearth_status": "UNVERIFIED",
    "threshold": 0.50,
    "prediction_horizon_hours": 24
  }
  ```

### `GET /api/v1/zones`
- **Response**: Array of spatial risk polygons covering all 8 North-Eastern states evaluated through the trained XGBoost model.

### `POST /api/v1/predictions/predict`
- **Request Payload**:
  ```json
  {
    "location": { "latitude": 26.15, "longitude": 91.75 },
    "rainfall": { "rain_1h": 35.0, "rain_24h": 120.0, "rain_3d": 210.0, "rain_7d": 350.0, "rain_14d": 500.0 },
    "terrain": { "elevation": 2000.0, "slope": 42.0, "twi": 8.5 },
    "soil": { "moisture_0_7cm": 0.55, "moisture_7_28cm": 0.50 }
  }
  ```
- **Response Payload**:
  ```json
  {
    "prediction_id": 101,
    "latitude": 26.15,
    "longitude": 91.75,
    "landslide_probability": 0.9998,
    "risk_score": 100,
    "risk_level": "CRITICAL",
    "data_status": "ALPHAEARTH_UNAVAILABLE",
    "model_version": "xgb-v1",
    "timestamp": "2026-08-31T12:00:00Z"
  }
  ```

### `POST /api/v1/sensors/readings`
- Ingests IoT reading, calculates cumulative rainfall windows, executes AI inference, persists to DB, and broadcasts update over WebSockets.

---

## 2. WebSocket Protocol (`ws://127.0.0.1:8000/ws/risk`)

- **Connection Message (`initial_risk_state`)**:
  Pushed immediately upon client connection containing initial array of latest predictions for all monitored locations.
- **Broadcast Message (`risk_update`)**:
  Pushed whenever a new prediction is generated. Map updates affected polygon without page reload.
