# SATHI IoT Telemetry & Real-Time Prediction Presentation Runbook

Step-by-step runbook for demonstrating live IoT temperature/rainfall telemetry ingestion and real-time AI risk updates to SIH evaluators.

---

## 1. System Startup Commands

### Step 1: Start FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Start Frontend Application
```bash
cd frontend
npm run dev
```

---

## 2. Demonstration Walkthrough Sequence

1. Open `http://localhost:5173/` or `http://localhost:3000/`.
2. Observe the **IoT Environmental Sensor Telemetry Card**:
   - Shows live stations across Shillong, Guwahati, Itanagar, Gangtok, Ukhrul, Aizawl, Kohima, Jampui.
   - Shows live Temperature (°C), Humidity (%), Soil Moisture (%), Rainfall (mm), and Station Status (`ONLINE`).
3. Scroll to the **Simulated Telemetry Ingestion Controls**:
   - Pick `Shillong Plateau Station (Meghalaya)`.
   - Slide **1h Rainfall** to `45 mm`.
   - Slide **Soil Moisture** to `85%`.
   - Click **Send Sensor Telemetry Reading**.
4. **Observe the Live Map**:
   - Telemetry is sent to `POST /api/v1/sensors/readings`.
   - FastAPI computes cumulative antecedent rainfall windows from MySQL history.
   - Feature Assembler builds 109-feature input vector.
   - XGBoost (`xgb-v1`) predicts `CRITICAL` risk level.
   - MySQL stores prediction record.
   - WebSocket broadcasts `risk_update` payload.
   - The Shillong polygon marker on the map updates **instantly** to red (`CRITICAL`) without reloading the browser page.
