/**
 * Centralized API & WebSocket Client for SATHI Frontend.
 * Connects to FastAPI Backend endpoints and native WebSocket (/ws/risk).
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/ws/risk';

/**
 * Fetch wrapper handling API errors & standard JSON parsing.
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `API error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.warn(`[SATHI API] Fetch failed for ${url}:`, error.message);
    throw error;
  }
}

export const apiService = {
  // 1. Health & Model Status
  getHealth: () => fetchAPI('/health'),
  getModelStatus: () => fetchAPI('/api/v1/model/status'),

  // 2. Risk Data & Map
  getRiskMap: () => fetchAPI('/api/v1/risk/map'),
  getLatestRisk: () => fetchAPI('/api/v1/risk/latest'),
  getRiskHistory: (limit = 100) => fetchAPI(`/api/v1/risk/history?limit=${limit}`),
  getZones: () => fetchAPI('/api/v1/zones'),

  // 3. Sensor & Weather Data
  getSensors: () => fetchAPI('/api/v1/sensors'),
  getLatestWeather: (lat = 26.15, lon = 91.75) => fetchAPI(`/api/v1/weather/latest?latitude=${lat}&longitude=${lon}`),
  ingestSensorReading: (data) => fetchAPI('/api/v1/sensors/readings', { method: 'POST', body: JSON.stringify(data) }),


  // 4. Citizen Reports & Volunteer Offers
  getReports: (limit = 100) => fetchAPI(`/api/v1/reports?limit=${limit}`),
  submitReport: (data) => fetchAPI('/api/v1/reports', { method: 'POST', body: JSON.stringify(data) }),
  verifyReport: (reportId, data) => fetchAPI(`/api/v1/reports/${reportId}/verify`, { method: 'PUT', body: JSON.stringify(data) }),

  getVolunteers: (limit = 100) => fetchAPI(`/api/v1/volunteers?limit=${limit}`),
  submitVolunteerOffer: (data) => fetchAPI('/api/v1/volunteers', { method: 'POST', body: JSON.stringify(data) }),
  updateVolunteerStatus: (offerId, data) => fetchAPI(`/api/v1/volunteers/${offerId}/status`, { method: 'PUT', body: JSON.stringify(data) }),


  // 5. Landslide Inventory (11,026 SIH26001 Records)
  getInventoryStats: () => fetchAPI('/inventory/stats'),
  getLandslideInventory: (state = null, limit = 200) => fetchAPI(`/inventory/landslides?limit=${limit}${state ? `&state=${encodeURIComponent(state)}` : ''}`),
  getNearbyLandslides: (lat, lon, radius = 25) => fetchAPI(`/inventory/nearby?latitude=${lat}&longitude=${lon}&radius_km=${radius}`),

  // 6. Predict & Dashboard Overview
  predict: (data) => fetchAPI('/api/v1/predictions/predict', { method: 'POST', body: JSON.stringify(data) }),
  getDashboardOverview: () => fetchAPI('/api/v1/dashboard/overview'),
  createAlert: (data) => fetchAPI('/api/v1/dashboard/alerts', { method: 'POST', body: JSON.stringify(data) }),

  // 7. Multi-Hazard Flood & Disaster ML Suite (7 Modules)
  assessFloodSeverity: (data) => fetchAPI('/api/v1/disaster/flood-severity', { method: 'POST', body: JSON.stringify(data) }),
  getRescuePriority: (data) => fetchAPI('/api/v1/disaster/rescue-priority', { method: 'POST', body: JSON.stringify(data) }),
  getResourceAllocation: (data) => fetchAPI('/api/v1/disaster/resource-allocation', { method: 'POST', body: JSON.stringify(data) }),
  clusterDisasterAreas: (data) => fetchAPI('/api/v1/disaster/cluster-areas', { method: 'POST', body: JSON.stringify(data) }),
  classifySOSMessage: (data) => fetchAPI('/api/v1/disaster/classify-sos', { method: 'POST', body: JSON.stringify(data) }),
  assessDamage: (data) => fetchAPI('/api/v1/disaster/damage-assessment', { method: 'POST', body: JSON.stringify(data) }),
  getSafeRoute: (data) => fetchAPI('/api/v1/disaster/safe-route', { method: 'POST', body: JSON.stringify(data) }),
  getUnifiedDisasterReport: (data) => fetchAPI('/api/v1/disaster/unified-pipeline', { method: 'POST', body: JSON.stringify(data) })
};




/**
 * Robust Real-Time WebSocket Client with Exponential Backoff Auto-Reconnect.
 */
export class RiskWebSocketClient {
  constructor(onMessage, onStatusChange) {
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectDelay = 10000;
    this.isClosedManually = false;
  }

  connect() {
    this.isClosedManually = false;
    if (this.onStatusChange) this.onStatusChange('CONNECTING');

    try {
      this.ws = new WebSocket(WS_BASE);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        if (this.onStatusChange) this.onStatusChange('LIVE');
        console.log('[SATHI WS] Real-Time WebSocket Connected to', WS_BASE);
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (this.onMessage) this.onMessage(data);
        } catch (e) {
          console.error('[SATHI WS] Error parsing WebSocket message:', e);
        }
      };

      this.ws.onclose = () => {
        if (!this.isClosedManually) {
          if (this.onStatusChange) this.onStatusChange('RECONNECTING');
          this.scheduleReconnect();
        } else {
          if (this.onStatusChange) this.onStatusChange('DISCONNECTED');
        }
      };

      this.ws.onerror = (err) => {
        console.warn('[SATHI WS] Connection error:', err);
      };
    } catch (err) {
      console.warn('[SATHI WS] Exception initializing connection:', err);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    this.reconnectAttempts += 1;
    const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), this.maxReconnectDelay);
    console.log(`[SATHI WS] Reconnecting in ${Math.round(delay / 1000)}s (Attempt #${this.reconnectAttempts})...`);
    setTimeout(() => {
      if (!this.isClosedManually) this.connect();
    }, delay);
  }

  close() {
    this.isClosedManually = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.onStatusChange) this.onStatusChange('DISCONNECTED');
  }
}
