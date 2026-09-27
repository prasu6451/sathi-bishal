# SATHI SIH 3–5 Minute Live Demonstration Runbook

Exact step-by-step presentation runbook and commands for demonstrating the **SATHI / SIH26001** Landslide Early-Warning System to evaluators.

---

## 1. Environment Preparation & Server Startup

### Step 1: Start FastAPI AI Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
*Verify Startup*: Open `http://127.0.0.1:8000/health` in browser. Expect `"status": "ok"`, `"model_version": "xgb-v1"`.

### Step 2: Start Frontend Application
```bash
cd frontend
npm run dev
```
*Open Application*: Open `http://localhost:5173/` or `http://localhost:3000/`.

---

## 2. 3–5 Minute SIH Presentation Sequence

### Phase 1: Dashboard & Live Map Overview (1 Minute)
1. Navigate to **Home Page** (`http://localhost:5173/`).
2. Point out the **AI Model Status Card**:
   - Model Version: `xgb-v1`
   - Feature Count: `109 Vector Dims`
   - Decision Threshold: `0.50`
   - AlphaEarth Status: `UNVERIFIED` (honest disclosure of satellite foundation status).
3. Click **View Live Map** to navigate to `http://localhost:5173/liveMap`.
4. Point out the green status badge in top-right corner: `● LIVE AI WebSocket Connected`.

### Phase 2: Live Sensor Telemetry Ingestion & Real-Time Risk Update (2 Minutes)
1. Keep the browser window open at `http://localhost:5173/liveMap`.
2. Open a terminal and run the interactive simulation script or send a sensor reading via curl:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/sensors/readings \
     -H "Content-Type: application/json" \
     -d '{
       "sensor_id": "ESP32_SHILLONG_01",
       "latitude": 25.55,
       "longitude": 91.90,
       "rainfall_mm": 52.0,
       "soil_moisture": 0.65
     }'
   ```
3. **Observe the Live Map**:
   - The Shillong Ridge polygon updates **instantly** to `CRITICAL` risk level.
   - Tooltip displays Risk Score `100/100`, Probability `99.98%`, and Data Status `ALPHAEARTH_UNAVAILABLE`.
   - **No page refresh or full re-render occurs**.

### Phase 3: Ground-Truth Citizen Report Submission (1 Minute)
1. Scroll to the **Submit Citizen Landslide Report** card.
2. Enter coordinates (Lat: `25.55`, Lon: `91.90`), Severity `4 - Major Debris Slide`, and Description `"Visible 3cm cracks near highway slope"`.
3. Click **Submit Observation Report**.
4. Point out the success banner explaining that citizen reports are stored for ground-truth confirmation but strictly **excluded** from predictive AI inputs to eliminate target leakage.

---

## 3. Verification Commands Summary

```bash
# Run AI Unit Tests (18 passed)
python -m pytest ai/tests/

# Run Backend Integration Tests (10 passed)
cd backend && python -m pytest tests/

# Run Frontend Production Build (Built cleanly in 4.23s)
cd frontend && npm run build
```
