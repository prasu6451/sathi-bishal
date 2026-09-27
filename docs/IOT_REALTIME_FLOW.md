# SATHI IoT Telemetry & Dynamic Real-Time Prediction Architecture

Detailed technical specification for IoT sensor telemetry ingestion, cumulative rainfall window calculation, feature assembly, AI prediction, database persistence, and WebSocket broadcasting.

---

## 1. End-to-End System Architecture Flow

```text
  [ Physical IoT Sensors / Simulation Panel ]
                      │
                      │ POST /api/v1/sensors/readings
                      │ {sensor_id, temperature, humidity, soil_moisture, rainfall_mm}
                      ▼
        [ FastAPI Sensors Endpoint ]
                      │
                      ├── Physical Telemetry Validation (-50°C..60°C, 0..100%, >=0mm)
                      │
                      ▼
         [ MySQL SensorReading Store ]
                      │
                      ▼
   [ Cumulative Rainfall Window Aggregator ]
   (Computes rain_1h, rain_24h, rain_3d, rain_7d, rain_14d from DB history)
                      │
                      ▼
        [ Real-Time Feature Assembler ]
  (Assembles 109-feature raw input vector for XGBoost model)
                      │
                      ▼
       [ XGBoost Inference Engine (xgb-v1) ]
  (Generates landslide_probability, risk_score, risk_level)
                      │
                      ▼
       [ MySQL RiskPrediction Database Store ]
                      │
                      ▼
       [ WebSocket Manager (/ws/risk) ]
  (Broadcasts risk_update + telemetry payload to active clients)
                      │
                      ▼
         [ Frontend Leaflet Live Map ]
  (Updates specific location marker immediately WITHOUT page reload)
```

---

## 2. Key Technical Implementations

### A. Telemetry API Endpoint (`GET /api/v1/sensors`)
Returns array of active IoT monitoring stations across North-East India with:
- `sensor_id`, `latitude`, `longitude`
- `temperature` (°C), `humidity` (%)
- `soil_moisture` (ratio 0.0–1.0)
- `rainfall_mm` (1h rainfall observation)
- `status`: `ONLINE` (if telemetry received $\le 3600\text{s}$ ago), `STALE` ($> 3600\text{s}$ ago), or `NO_DATA`.

### B. Cumulative Rainfall Aggregation
Rainfall is aggregated dynamically from database historical observations:
$$\text{rain}_{24\text{h}} = \sum_{t - 24\text{h}}^{t} \text{rainfall\_mm}$$
Monotonicity constraint enforced across windows: $\text{rain}_{14\text{d}} \ge \text{rain}_{7\text{d}} \ge \text{rain}_{3\text{d}} \ge \text{rain}_{24\text{h}} \ge \text{rain}_{1\text{h}}$.

### C. Soil Depth Attenuation Profile
$$\text{moisture}_{0\_7\text{cm}} = \text{soil\_moisture}$$
$$\text{moisture}_{7\_28\text{cm}} = \text{soil\_moisture} \times 0.95$$

### D. Zero-Fabrication Rule
The frontend NEVER computes or fabricates `risk_score` or `risk_level` locally. The backend AI model is the sole authority for all predictions.
