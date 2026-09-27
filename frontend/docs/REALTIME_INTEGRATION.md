# SATHI Real-Time Frontend Integration Guide

Instructions for running, configuring, and verifying the real-time AI frontend integration.

---

## 1. Environment Configuration (`.env`)

Create `.env` inside `frontend/`:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws/risk
VITE_DEMO_MODE=false
```

---

## 2. Running Frontend & Backend

1. Start FastAPI AI Backend Server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. Start Frontend Dev Server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open Browser:
   - Application UI: `http://localhost:5173/` or `http://localhost:3000/`
   - Live Map: `http://localhost:5173/liveMap`

---

## 3. Real-Time Verification Flow

1. Open `http://localhost:5173/liveMap`.
2. Confirm the green badge displays: `● LIVE AI WebSocket Connected`.
3. Ingest a sensor or weather observation in the backend:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/sensors/readings \
     -H "Content-Type: application/json" \
     -d '{"sensor_id": "ESP32_001", "rainfall_mm": 45.0, "soil_moisture": 0.60}'
   ```
4. Observe the polygon risk level and tooltip metrics on the map update **instantly** without reloading the page.
