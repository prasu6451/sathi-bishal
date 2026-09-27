# SATHI Frontend Integration Contract

Specification of REST endpoints, WebSocket lifecycle, payload structures, risk levels, and status codes for frontend developers.

---

## 1. WebSocket Interface (`ws://localhost:8000/ws/risk`)

### Client Lifecycle Flow
```text
CLIENT -> Connect ws://localhost:8000/ws/risk
SERVER -> Accept Connection
SERVER -> Send initial_risk_state JSON
SERVER -> Keepalive Ping/Pong loop
SERVER -> Broadcast risk_update JSON when background evaluation completes
```

### Initial Risk Message (`initial_risk_state`)
```json
{
  "type": "initial_risk_state",
  "data": [
    {
      "prediction_id": 101,
      "location_id": 1,
      "latitude": 26.15,
      "longitude": 91.75,
      "landslide_probability": 0.8542,
      "risk_score": 85,
      "risk_level": "CRITICAL",
      "data_status": "ALPHAEARTH_UNAVAILABLE",
      "model_version": "xgb-v1",
      "timestamp": "2026-08-31T11:25:00Z"
    }
  ]
}
```

### Live Risk Update Message (`risk_update`)
```json
{
  "type": "risk_update",
  "data": {
    "prediction_id": 102,
    "location_id": 1,
    "latitude": 26.15,
    "longitude": 91.75,
    "landslide_probability": 0.8912,
    "risk_score": 89,
    "risk_level": "CRITICAL",
    "data_status": "ALPHAEARTH_UNAVAILABLE",
    "model_version": "xgb-v1",
    "timestamp": "2026-08-31T11:26:00Z"
  }
}
```

---

## 2. Risk Level Thresholds

| Risk Level | Score Range | Landslide Probability ($p$) | Map Color Code | Action Required |
| --- | --- | --- | --- | --- |
| `LOW` | `0 .. 24` | $p < 0.25$ | `#10B981` (Green) | Normal monitoring |
| `MODERATE` | `25 .. 49` | $0.25 \le p < 0.50$ | `#F59E0B` (Amber) | Advisory alert |
| `HIGH` | `50 .. 74` | $0.50 \le p < 0.75$ | `#EF4444` (Orange-Red) | Warning alert |
| `CRITICAL` | `75 .. 100` | $p \ge 0.75$ | `#DC2626` (Red) | Evacuation alert |

---

## 3. Data Status Indicators (`data_status`)

- `COMPLETE`: Full real-time sensor, weather, and Earth Engine satellite inputs available.
- `ALPHAEARTH_UNAVAILABLE`: Environmental metrics complete; AlphaEarth embedding uses placeholder status.
- `STALE`: Dynamic weather/sensor observations exceed 3600s max age threshold.
- `INSUFFICIENT_DATA`: Prediction blocked due to missing required inputs.
