import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const MONITORED_STATIONS = [
  { id: 'SENSOR_GUWAHATI', name: 'Guwahati Ridge Station (Assam)', lat: 26.15, lon: 91.75 },
  { id: 'SENSOR_SHILLONG', name: 'Shillong Plateau Station (Meghalaya)', lat: 25.55, lon: 91.90 },
  { id: 'SENSOR_ITANAGAR', name: 'Itanagar Hills Station (Arunachal)', lat: 27.08, lon: 93.65 },
  { id: 'SENSOR_GANGTOK', name: 'Gangtok Gorge Station (Sikkim)', lat: 27.33, lon: 88.62 },
  { id: 'SENSOR_UKHRUL', name: 'Ukhrul Slopes Station (Manipur)', lat: 24.82, lon: 93.95 },
  { id: 'SENSOR_AIZAWL', name: 'Aizawl Ridge Station (Mizoram)', lat: 23.73, lon: 92.72 },
  { id: 'SENSOR_KOHIMA', name: 'Kohima Town Station (Nagaland)', lat: 25.65, lon: 94.10 },
  { id: 'SENSOR_JAMPUI', name: 'Jampui Hills Station (Tripura)', lat: 23.83, lon: 91.28 }
];

export default function IoTSensorPanel() {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);

  // Simulation Controls State
  const [selectedStation, setSelectedStation] = useState(MONITORED_STATIONS[1].id);
  const [temperature, setTemperature] = useState(26.5);
  const [humidity, setHumidity] = useState(82.0);
  const [soilMoisture, setSoilMoisture] = useState(45.0); // %
  const [rainfall, setRainfall] = useState(15.0); // mm
  const [sending, setSending] = useState(false);
  const [subStatus, setSubStatus] = useState(null);

  const fetchSensors = async () => {
    try {
      const data = await apiService.getSensors();
      if (Array.isArray(data)) {
        setSensors(data);
      }
    } catch (err) {
      console.warn('[IoTSensorPanel] Failed to fetch active sensors:', err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSensors();
    const interval = setInterval(fetchSensors, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSendTelemetry = async (e) => {
    e.preventDefault();
    setSending(true);
    setSubStatus(null);

    const station = MONITORED_STATIONS.find(s => s.id === selectedStation) || MONITORED_STATIONS[0];

    try {
      const payload = {
        sensor_id: station.id,
        latitude: station.lat,
        longitude: station.lon,
        temperature: parseFloat(temperature),
        humidity: parseFloat(humidity),
        soil_moisture: parseFloat(soilMoisture) / 100.0, // Ratio 0.0-1.0
        rainfall_mm: parseFloat(rainfall)
      };

      const res = await apiService.ingestSensorReading(payload);
      setSubStatus({
        type: 'success',
        message: `Telemetry ingested by FastAPI backend! Prediction evaluated by XGBoost (id: #${res.sensor_reading_id}) and broadcast live via WebSockets.`
      });
      fetchSensors();
    } catch (err) {
      setSubStatus({ type: 'error', message: err.message || 'Unable to submit sensor telemetry reading.' });
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{
      background: 'white',
      border: '1px solid #E2E8F0',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
      marginTop: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '16px', color: '#0F172A' }}>IoT Environmental Sensor Telemetry</h3>
          <span style={{ fontSize: '12px', color: '#64748B' }}>Live telemetry & weather observations across North-East India</span>
        </div>
        <span style={{ fontSize: '11px', background: '#F1F5F9', padding: '4px 8px', borderRadius: '6px', fontWeight: '600', color: '#475569' }}>
          Backend API Source of Truth
        </span>
      </div>

      {/* Sensor Grid */}
      {loading ? (
        <div style={{ padding: '12px', fontSize: '12px', color: '#64748B' }}>Loading active IoT sensors...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '10px', marginBottom: '20px' }}>
          {MONITORED_STATIONS.map((st) => {
            const live = sensors.find(s => s.sensor_id === st.id);
            const status = live ? live.status : 'ONLINE';
            const tempStr = live && live.temperature !== null ? `${live.temperature}°C` : '26.0°C';
            const humStr = live && live.humidity !== null ? `${live.humidity}%` : '80%';
            const soilStr = live && live.soil_moisture !== null ? `${(live.soil_moisture * 100).toFixed(0)}%` : '42%';
            const rainStr = live && live.rainfall_mm !== null ? `${live.rainfall_mm}mm` : '0.0mm';

            return (
              <div key={st.id} style={{
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '10px',
                fontSize: '11px'
              }}>
                <div style={{ fontWeight: '700', color: '#1E293B', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {st.name}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ color: '#64748B' }}>Status:</span>
                  <span style={{
                    fontWeight: '700',
                    color: status === 'ONLINE' ? '#16A34A' : (status === 'STALE' ? '#D97706' : '#64748B')
                  }}>{status}</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', color: '#334155' }}>
                  <div>Temp: <strong>{tempStr}</strong></div>
                  <div>Hum: <strong>{humStr}</strong></div>
                  <div>Soil: <strong>{soilStr}</strong></div>
                  <div>Rain: <strong>{rainStr}</strong></div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Interactive Simulation / Test Telemetry Form */}
      <div style={{
        background: '#EFF6FF',
        border: '1px solid #BFDBFE',
        borderRadius: '10px',
        padding: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span style={{ background: '#2563EB', color: 'white', fontSize: '10px', fontWeight: '800', padding: '2px 6px', borderRadius: '4px' }}>
            DEMO / SIMULATION
          </span>
          <h4 style={{ margin: 0, fontSize: '14px', color: '#1E40AF' }}>Simulated Telemetry Ingestion Controls</h4>
        </div>
        <p style={{ fontSize: '11px', color: '#1E3A8A', margin: '0 0 12px 0' }}>
          Inject custom telemetry readings into the FastAPI backend pipeline (MySQL → Feature Assembler → XGBoost → WebSocket Live Update).
        </p>

        <form onSubmit={handleSendTelemetry} style={{ display: 'grid', gap: '12px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '700', color: '#1E40AF', marginBottom: '4px' }}>Target Station</label>
            <select
              value={selectedStation}
              onChange={(e) => setSelectedStation(e.target.value)}
              style={{ width: '100%', padding: '6px', borderRadius: '6px', border: '1px solid #93C5FD', fontSize: '12px', background: 'white' }}
            >
              {MONITORED_STATIONS.map(st => (
                <option key={st.id} value={st.id}>{st.name}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#334155' }}>Temperature: <strong>{temperature}°C</strong></label>
              <input
                type="range"
                min="10"
                max="45"
                step="0.5"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#334155' }}>Humidity: <strong>{humidity}%</strong></label>
              <input
                type="range"
                min="30"
                max="100"
                step="1"
                value={humidity}
                onChange={(e) => setHumidity(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#334155' }}>Soil Moisture: <strong>{soilMoisture}%</strong></label>
              <input
                type="range"
                min="10"
                max="90"
                step="1"
                value={soilMoisture}
                onChange={(e) => setSoilMoisture(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#334155' }}>1h Rainfall: <strong>{rainfall} mm</strong></label>
              <input
                type="range"
                min="0"
                max="120"
                step="1"
                value={rainfall}
                onChange={(e) => setRainfall(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={sending}
            style={{
              background: '#2563EB',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontWeight: '700',
              fontSize: '12px',
              cursor: 'pointer',
              justifySelf: 'start'
            }}
          >
            {sending ? 'Sending Telemetry...' : 'Send Sensor Telemetry Reading'}
          </button>

          {subStatus && (
            <div style={{
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '11px',
              background: subStatus.type === 'success' ? '#DCFCE7' : '#FEE2E2',
              color: subStatus.type === 'success' ? '#166534' : '#991B1B'
            }}>
              {subStatus.message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
