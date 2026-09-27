# SATHI — Real-Time Landslide Early-Warning Backend

Production backend service for **SATHI / SIH26001** built with **FastAPI**, **MySQL 8+** (with SQLAlchemy 2.x & PyMySQL, featuring automatic SQLite fallback for offline local testing), **Native WebSockets (`/ws/risk`)**, **Async Risk Monitoring Worker**, and integration with the trained **XGBoost AI Model (`xgb-v1`)**.

---

## Architecture Flow

```text
               IoT Sensor Reading / Weather Data
                              │
                              ▼
                POST /api/v1/sensors/readings
                              │
                              ▼
                Save Reading to MySQL / SQLite
                              │
                              ▼
                  AI Model Inference (xgb-v1)
                              │
                              ▼
                Save Prediction & Risk Score
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
       Database Store               WebSocket Broadcast (/ws/risk)
                                               │
                                               ▼
                                     Frontend Map Renderer
                              (Live Map Updates Instantly)
```

---

## REST Endpoints & WebSockets Summary

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Application status, database connection, model status, and WebSocket client count |
| `GET` | `/docs` | Interactive Swagger OpenAPI documentation |
| `POST` | `/api/v1/predictions/predict` | Evaluate landslide risk for a geospatial location through the trained AI model |
| `POST` | `/api/v1/sensors/readings` | Ingest IoT sensor reading, persist to DB, evaluate AI prediction, and broadcast WebSocket update |
| `POST` | `/api/v1/weather/observations` | Ingest weather observations into database |
| `GET` | `/api/v1/weather/latest` | Fetch latest weather observation |
| `POST` | `/api/v1/reports` | Submit citizen landslide report (stored for monitoring; excluded from AI input) |
| `GET` | `/api/v1/reports` | List citizen landslide reports |
| `GET` | `/api/v1/risk/latest` | Fetch latest risk prediction for each monitored location |
| `GET` | `/api/v1/risk/history` | Historical risk predictions log |
| `GET` | `/api/v1/risk/map` | Spatial risk map payload for map rendering |
| `GET` | `/api/v1/zones` | Multi-tier spatial risk polygons across all 8 North-Eastern states |
| `WS` | `/ws/risk` | Real-time WebSocket connection for live risk updates (`initial_risk_state` and `risk_update`) |

---

## Getting Started

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default MySQL Connection String:
`DATABASE_URL=mysql+pymysql://root:password@localhost:3306/sathi`
*(Note: If MySQL is offline, the backend automatically uses `sqlite:///./landslide_system.db` for offline testing).*

### 2. Launch FastAPI Server
From the `backend/` directory:
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Real-Time WebSocket: `ws://localhost:8000/ws/risk`

### 3. Run Test Suite
```bash
python -m pytest tests/
```

---

## Important AI Model Limitations
1. **AlphaEarth Status**: `alphaearth_status = UNVERIFIED`. Current satellite embeddings use synthetic/placeholder representations. Production deployment requires live Google Earth Engine asset provisioning.
2. **Hard Negatives**: Recommending collection of hard negative control samples (steep slopes under heavy rainfall without landslides) prior to civil defense deployment.