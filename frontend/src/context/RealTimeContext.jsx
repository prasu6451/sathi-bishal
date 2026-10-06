import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { RiskWebSocketClient, apiService } from '../services/api';

const RealTimeContext = createContext(null);

export function RealTimeProvider({ children }) {
  const [wsStatus, setWsStatus] = useState('CONNECTING'); // 'LIVE' | 'CONNECTING' | 'RECONNECTING' | 'DISCONNECTED'
  const [liveRiskMap, setLiveRiskMap] = useState({});
  const [liveTelemetryMap, setLiveTelemetryMap] = useState({});
  const [realtimeAlerts, setRealtimeAlerts] = useState([]);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const simIntervalRef = useRef(null);
  const wsClientRef = useRef(null);

  // Handle incoming real-time messages from WebSocket
  const handleWsMessage = useCallback((msg) => {
    if (!msg || !msg.type) return;

    setLastUpdateTime(new Date());

    if (msg.type === 'initial_risk_state' && Array.isArray(msg.data)) {
      const initialMap = {};
      msg.data.forEach((item) => {
        const key = `${Number(item.latitude).toFixed(2)}_${Number(item.longitude).toFixed(2)}`;
        initialMap[key] = item;
      });
      setLiveRiskMap((prev) => ({ ...prev, ...initialMap }));
    } else if (msg.type === 'risk_update' && msg.data) {
      const item = msg.data;
      const key = `${Number(item.latitude).toFixed(2)}_${Number(item.longitude).toFixed(2)}`;
      
      setLiveRiskMap((prev) => ({
        ...prev,
        [key]: {
          ...prev[key],
          ...item,
          lastUpdated: new Date().toISOString()
        }
      }));

      if (item.telemetry) {
        setLiveTelemetryMap((prev) => ({
          ...prev,
          [key]: item.telemetry
        }));
      }

      // Add to live alerts feed if HIGH or CRITICAL
      const riskLvl = (item.risk_level || '').toUpperCase();
      if (riskLvl === 'CRITICAL' || riskLvl === 'HIGH') {
        const newAlert = {
          id: `rt-alert-${Date.now()}`,
          type: item.landslide_probability >= 0.75 ? 'Landslide Alert' : 'Slope Instability',
          title: `Real-Time Risk Spike: ${(item.risk_level || 'HIGH')} at [${Number(item.latitude).toFixed(2)}, ${Number(item.longitude).toFixed(2)}]`,
          severity: item.risk_level || 'High',
          probability: Math.round((item.landslide_probability || 0.8) * 100),
          time: 'Just now',
          description: `Telemetry update triggered XGBoost prediction (Score: ${item.risk_score || Math.round((item.landslide_probability || 0.8) * 100)}/100). Live broadcast via WebSocket.`
        };

        setRealtimeAlerts((prev) => [newAlert, ...prev.slice(0, 19)]);
      }
    }
  }, []);

  // Initialize and connect WebSocket
  useEffect(() => {
    const client = new RiskWebSocketClient(
      handleWsMessage,
      (status) => setWsStatus(status)
    );
    wsClientRef.current = client;
    client.connect();

    return () => {
      if (client) client.close();
    };
  }, [handleWsMessage]);

  // Client-side auto simulation loop (optional live telemetry generator)
  const toggleSimulation = useCallback((active) => {
    const shouldRun = active !== undefined ? active : !isSimulating;
    setIsSimulating(shouldRun);

    if (simIntervalRef.current) {
      clearInterval(simIntervalRef.current);
      simIntervalRef.current = null;
    }

    if (shouldRun) {
      const stations = [
        { id: 'SENSOR_GUWAHATI', lat: 26.15, lon: 91.75 },
        { id: 'SENSOR_SHILLONG', lat: 25.55, lon: 91.90 },
        { id: 'SENSOR_ITANAGAR', lat: 27.08, lon: 93.65 },
        { id: 'SENSOR_GANGTOK', lat: 27.33, lon: 88.62 },
        { id: 'SENSOR_UKHRUL', lat: 24.82, lon: 93.95 },
        { id: 'SENSOR_AIZAWL', lat: 23.73, lon: 92.72 },
        { id: 'SENSOR_KOHIMA', lat: 25.65, lon: 94.10 },
        { id: 'SENSOR_JAMPUI', lat: 23.83, lon: 91.28 }
      ];

      // Stream a reading every 4 seconds across rotating stations
      let idx = 0;
      simIntervalRef.current = setInterval(async () => {
        const st = stations[idx % stations.length];
        idx += 1;

        const rain = Number((Math.random() * 45 + 5).toFixed(1));
        const soil = Number((Math.random() * 0.40 + 0.35).toFixed(2));
        const temp = Number((Math.random() * 8 + 22).toFixed(1));
        const hum = Number((Math.random() * 20 + 75).toFixed(1));

        try {
          await apiService.ingestSensorReading({
            sensor_id: st.id,
            latitude: st.lat,
            longitude: st.lon,
            temperature: temp,
            humidity: hum,
            soil_moisture: soil,
            rainfall_mm: rain
          });
        } catch (e) {
          console.warn('[RealTime Sim] Error sending simulated telemetry:', e.message);
        }
      }, 4000);
    }
  }, [isSimulating]);

  // Clean up interval on unmount
  useEffect(() => {
    return () => {
      if (simIntervalRef.current) {
        clearInterval(simIntervalRef.current);
      }
    };
  }, []);

  return (
    <RealTimeContext.Provider
      value={{
        wsStatus,
        liveRiskMap,
        liveTelemetryMap,
        realtimeAlerts,
        lastUpdateTime,
        isSimulating,
        toggleSimulation,
        reconnect: () => wsClientRef.current?.connect()
      }}
    >
      {children}
    </RealTimeContext.Provider>
  );
}

export function useRealTimeRisk() {
  const context = useContext(RealTimeContext);
  if (!context) {
    throw new Error('useRealTimeRisk must be used within a RealTimeProvider');
  }
  return context;
}
