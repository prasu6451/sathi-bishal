# SATHI Frontend & Backend Integration Architecture

Documenting the existing frontend architecture and integration strategy with the FastAPI AI backend.

---

## 1. Frontend Technology Stack Overview
- **Build Tool**: Vite 8+
- **UI Framework**: React 19
- **Routing**: React Router DOM v7 (`/`, `/liveMap`, `/about`, `/contact`)
- **Map Engine**: Leaflet 1.9 + React-Leaflet 5.0
- **Icons**: React Icons (GoShieldCheck, FaBell)
- **Styling**: Modular Vanilla CSS (`Header.css`, `MapView.css`, `Pages.css`, `home.css`)

---

## 2. Existing Frontend Map & WebSocket Component (`MapView.jsx`)
- **Center & Zoom**: Center `[26.0, 93.0]`, Zoom `7` (covering all 8 North-Eastern states: Assam, Meghalaya, Arunachal Pradesh, Sikkim, Manipur, Mizoram, Nagaland, Tripura).
- **REST Ingestion**: `GET http://localhost:8000/api/v1/zones`
- **Real-Time WebSocket**: `ws://localhost:8000/ws/risk`
- **Fallback Data**: `frontend/src/data/riskZones.js` (used only when backend is offline).

---

## 3. Integration Plan & Enhancements
1. **Centralized API & WebSocket Config**:
   - Environment variables: `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`) and `VITE_WS_URL` (default `ws://127.0.0.1:8000/ws/risk`).
   - Create centralized API client service [`frontend/src/services/api.js`](file:///c:/Users/PK/Desktop/sathi/frontend/src/services/api.js) and TypeScript/JSDoc types [`frontend/src/types/api.js`](file:///c:/Users/PK/Desktop/sathi/frontend/src/types/api.js).
2. **Data Status & AlphaEarth Warnings**:
   - Display `data_status` indicators (`COMPLETE`, `ALPHAEARTH_UNAVAILABLE`, `STALE`, `INSUFFICIENT_DATA`) in map tooltips and risk cards.
   - Display warning badges when `alphaearth_status = UNVERIFIED`.
3. **Robust WebSocket Reconnection**:
   - Exponential backoff auto-reconnect strategy for `/ws/risk`.
   - Update connection state badge (`LIVE`, `CONNECTING`, `OFFLINE`).
4. **Dashboard & Model Status Components**:
   - Add model status card displaying `model_version` (`xgb-v1`), `feature_count` (`109`), threshold (`0.50`), and AlphaEarth status (`UNVERIFIED`).
   - Connect Citizen Report submission form to `POST /api/v1/reports`.
