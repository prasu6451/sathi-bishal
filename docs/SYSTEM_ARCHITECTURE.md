# SATHI System Architecture — Final Verification

Technical architecture documentation for **SATHI / SIH26001** (AI-Based Landslide Early-Warning & Risk-Monitoring System).

---

## 1. System Topology & Data Flow

```text
  [ Telemetry / IoT Sensor / Weather Data ]
                       │
                       ▼
         [ FastAPI Backend (port 8000) ]
                       │
                       ▼
       [ MySQL / SQLite Database Store ]
                       │
                       ▼
       [ Real-Time Feature Assembler ]
  (Combines Static GIS DEM/Geology + 
   Dynamic Cumulative Rainfall 1h..14d)
                       │
                       ▼
            [ Input Validation ]
      (Enforces zero-fabrication rules)
                       │
                       ▼
    [ AI Predictor Engine (xgb-v1) ]
     (109-feature XGBoost Classifier)
                       │
                       ▼
       [ Landslide Probability & Score ]
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 [ MySQL Persistence ]     [ WebSocket Manager Broadcast ]
  (risk_predictions)               (/ws/risk)
                                      │
                                      ▼
                          [ Frontend Live Map ]
                           (Leaflet Renderer)
```

---

## 2. Component Specifications

### A. AI Model & Inference Engine (`ai/`)
- **Model Version**: `xgb-v1`
- **Model Type**: XGBoost Binary Classifier (`XGBClassifier`)
- **Feature Vector Length**: `109` features
- **Inference Engine**: `LandslidePredictor` in `ai/inference/predictor.py`
- **Saved Model Location**: `ai/saved_models/current/`
- **Threshold**: `0.50` ($p \ge 0.75 \rightarrow \text{CRITICAL}$, $0.50 \le p < 0.75 \rightarrow \text{HIGH}$, $0.25 \le p < 0.50 \rightarrow \text{MODERATE}$, $p < 0.25 \rightarrow \text{LOW}$)

### B. Backend Services (`backend/`)
- **Framework**: FastAPI + Uvicorn
- **ORM & Database**: SQLAlchemy 2.x + PyMySQL (MySQL 8+ with local SQLite fallback)
- **WebSockets**: Native FastAPI WebSockets (`/ws/risk`)
- **Background Worker**: `risk_monitor_worker` (evaluates North-East India locations every 60s)

### C. Frontend UI (`frontend/`)
- **Framework**: Vite 8 + React 19 + React Router DOM v7
- **Map Library**: Leaflet 1.9 + React-Leaflet 5.0
- **Live Connection**: Centralized `apiService` and `RiskWebSocketClient` in `frontend/src/services/api.js`

---

## 3. Disclosures & Prototype Limitations
1. **AlphaEarth Status**: `alphaearth_status = UNVERIFIED`. Current 64-dimensional satellite foundation vectors use placeholder representations.
2. **Topographic Class Separability**: Training dataset features strong slope/rainfall separation between positive and negative classes. Hard negative validation is recommended prior to civil defense deployment.
3. **Single-Process Worker Constraint**: In-process background monitoring worker and WebSocket connection manager run inside a single Uvicorn process. Multi-worker scaling would require a shared pub/sub message broker (e.g. Redis).
