import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import MapView from '../components/MapView';
import ModelStatusCard from '../components/ModelStatusCard';
import IoTSensorPanel from '../components/IoTSensorPanel';
import './dashboard.css';

const DEFAULT_STAT_CARDS = [
  { label: 'Flood alerts', value: '14', delta: '+4 since yesterday', tone: 'flood' },
  { label: 'Landslide watch', value: '11,026', delta: 'SIH26001 dataset incidents', tone: 'landslide' },
  { label: 'People at risk', value: '5.8K', delta: 'Across 8 NE districts', tone: 'risk' },
  { label: 'Rainfall forecast', value: '84 mm', delta: '24h cumulative forecast', tone: 'rain' },
];

const DEFAULT_ZONE_SUMMARY = [
  { district: 'Aizawl (1,317 Dataset Incidents)', flood: 35, landslide: 94, status: 'Critical' },
  { district: 'Lunglei (669 Dataset Incidents)', flood: 28, landslide: 89, status: 'Critical' },
  { district: 'East Khasi Hills (405 Dataset Incidents)', flood: 42, landslide: 92, status: 'Critical' },
  { district: 'Dima Hasao (387 Dataset Incidents)', flood: 62, landslide: 87, status: 'Critical' },
  { district: 'Kohima (487 Dataset Incidents)', flood: 30, landslide: 84, status: 'High' },
  { district: 'Ukhrul (315 Dataset Incidents)', flood: 24, landslide: 78, status: 'High' },
  { district: 'Kamrup / Guwahati Basin', flood: 85, landslide: 48, status: 'High' },
  { district: 'Goalpara', flood: 90, landslide: 52, status: 'High' },
  { district: 'Sivasagar (Nepali Kuti Flood Plain)', flood: 88, landslide: 32, status: 'High' },
];

const DEFAULT_ALERTS = [
  { type: 'Landslide', title: 'Aizawl Slopes Failure Watch (1,317 Historical Slides Logged)', time: '8 mins ago', severity: 'Critical', description: 'Extreme soil saturation on steep hill cuts along Aizawl-Lunglei highway corridor.' },
  { type: 'Landslide', title: 'Shillong & Cherrapunji Slope Instability Alert (405 Historical Slides Logged)', time: '22 mins ago', severity: 'Critical', description: 'Torrential rainfall causing active soil creep and rockfalls across East Khasi Hills.' },
  { type: 'Flood', title: 'Brahmaputra Basin Surge near Kamrup & Goalpara', time: '45 mins ago', severity: 'High', description: 'Water level exceeding warning marks along lower river basin; lowlands flooded.' },
  { type: 'Landslide', title: 'Kohima NH-29 Debris Slide Watch (487 Historical Slides Logged)', time: '1 hr ago', severity: 'High', description: 'Road excavation and monsoon runoff causing slope mass movement near Kohima town.' },
  { type: 'Landslide', title: 'Dima Hasao Hill Sector Cut Failure (387 Historical Slides Logged)', time: '2 hrs ago', severity: 'High', description: 'Railway embankment and hill slope displacement reported in Dima Hasao district.' },
];

const DEFAULT_RECOMMENDATIONS = [
  'Deploy emergency slope monitoring teams to high-density slide zones in Aizawl and Lunglei.',
  'Activate river-level monitoring and flood shelters in Goalpara and Kamrup embankments.',
  'Issue local SMS alerts to vulnerable hillside settlements in East Khasi Hills & Dima Hasao.',
  'Position heavy earthmoving clearing machinery along NH-29 Kohima corridor.',
];


const DEFAULT_TREND_DATA = [
  { label: 'Mon', value: 42 },
  { label: 'Tue', value: 56 },
  { label: 'Wed', value: 60 },
  { label: 'Thu', value: 74 },
  { label: 'Fri', value: 68 },
  { label: 'Sat', value: 86 },
  { label: 'Sun', value: 91 },
];

export default function Dashboard() {
  const [statCards, setStatCards] = useState(DEFAULT_STAT_CARDS);
  const [zoneSummary, setZoneSummary] = useState(DEFAULT_ZONE_SUMMARY);
  const [alerts, setAlerts] = useState(DEFAULT_ALERTS);
  const [recommendations, setRecommendations] = useState(DEFAULT_RECOMMENDATIONS);
  const [trendData, setTrendData] = useState(DEFAULT_TREND_DATA);
  const [loading, setLoading] = useState(true);
  const [isLiveBackend, setIsLiveBackend] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // Add Alert Form State
  const [showAddAlert, setShowAddAlert] = useState(false);
  const [alertType, setAlertType] = useState('Landslide');
  const [alertTitle, setAlertTitle] = useState('');
  const [alertSeverity, setAlertSeverity] = useState('High');
  const [alertDesc, setAlertDesc] = useState('');
  const [submittingAlert, setSubmittingAlert] = useState(false);

  const loadDashboardData = async () => {
    try {
      const data = await apiService.getDashboardOverview();
      if (data) {
        if (data.stat_cards?.length) setStatCards(data.stat_cards);
        if (data.zone_summary?.length) setZoneSummary(data.zone_summary);
        if (data.alerts?.length) setAlerts(data.alerts);
        if (data.recommendations?.length) setRecommendations(data.recommendations);
        if (data.trend_data?.length) setTrendData(data.trend_data);
        setIsLiveBackend(true);
      }
    } catch (err) {
      console.warn('[Dashboard] Live backend data fetch fallback:', err.message);
      setIsLiveBackend(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateAlertSubmit = async (e) => {
    e.preventDefault();
    setSubmittingAlert(true);
    try {
      await apiService.createAlert({
        type: alertType,
        title: alertTitle,
        severity: alertSeverity,
        description: alertDesc,
        time_ago: 'Just now'
      });
      setAlertTitle('');
      setAlertDesc('');
      setShowAddAlert(false);
      await loadDashboardData();
    } catch (err) {
      alert('Failed to submit alert to SQL database: ' + err.message);
    } finally {
      setSubmittingAlert(false);
    }
  };

  const handleExportReport = () => {
    const reportObj = {
      timestamp: new Date().toISOString(),
      statCards,
      zoneSummary,
      alerts,
      recommendations,
      trendData
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportObj, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `SATHI_Operations_Report_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <span className="section-kicker">
            Operations overview {isLiveBackend ? '● Live SQL & AI Connected' : '○ Offline Mode'}
          </span>
          <h1>Flood & landslide risk dashboard</h1>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="button"
            className="dashboard-action"
            style={{ background: '#2563EB', color: 'white', border: 'none' }}
            onClick={() => setShowAddAlert(!showAddAlert)}
          >
            {showAddAlert ? 'Cancel' : '+ Issue SQL Alert'}
          </button>
          <button type="button" className="dashboard-action" onClick={handleExportReport}>
            Export report
          </button>
        </div>
      </div>

      {/* AI Model Status Overview */}
      <ModelStatusCard />

      {/* New SQL Alert Submission Panel */}
      {showAddAlert && (
        <form onSubmit={handleCreateAlertSubmit} style={{
          background: '#EFF6FF',
          border: '1px solid #93C5FD',
          borderRadius: '12px',
          padding: '16px',
          marginTop: '16px',
          display: 'grid',
          gap: '12px'
        }}>
          <h3 style={{ margin: 0, fontSize: '15px', color: '#1E40AF' }}>Publish New Operational Disaster Alert to SQL</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr', gap: '10px' }}>
            <div>
              <label style={{ fontSize: '11px', fontWeight: '700', color: '#1E3A8A' }}>Hazard Type</label>
              <select
                value={alertType}
                onChange={(e) => setAlertType(e.target.value)}
                style={{ width: '100%', padding: '6px', borderRadius: '6px', border: '1px solid #BFDBFE' }}
              >
                <option value="Landslide">Landslide</option>
                <option value="Flood">Flood</option>
                <option value="Rainfall">Rainfall</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: '11px', fontWeight: '700', color: '#1E3A8A' }}>Alert Headline Title</label>
              <input
                type="text"
                placeholder="e.g. Sudden slope creep detected near NH-27"
                value={alertTitle}
                onChange={(e) => setAlertTitle(e.target.value)}
                required
                style={{ width: '100%', padding: '6px', borderRadius: '6px', border: '1px solid #BFDBFE' }}
              />
            </div>
            <div>
              <label style={{ fontSize: '11px', fontWeight: '700', color: '#1E3A8A' }}>Severity Level</label>
              <select
                value={alertSeverity}
                onChange={(e) => setAlertSeverity(e.target.value)}
                style={{ width: '100%', padding: '6px', borderRadius: '6px', border: '1px solid #BFDBFE' }}
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Moderate">Moderate</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
          <div>
            <label style={{ fontSize: '11px', fontWeight: '700', color: '#1E3A8A' }}>Detailed Alert Description</label>
            <input
              type="text"
              placeholder="e.g. Saturated soil and 45mm/h rainfall increasing slope failure risk..."
              value={alertDesc}
              onChange={(e) => setAlertDesc(e.target.value)}
              required
              style={{ width: '100%', padding: '6px', borderRadius: '6px', border: '1px solid #BFDBFE' }}
            />
          </div>
          <button
            type="submit"
            disabled={submittingAlert}
            style={{
              background: '#2563EB',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              fontWeight: '700',
              cursor: 'pointer',
              justifySelf: 'start'
            }}
          >
            {submittingAlert ? 'Publishing to SQL...' : 'Save Alert in SQL Database'}
          </button>
        </form>
      )}

      {/* Navigation Tabs */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginTop: '20px',
        marginBottom: '10px',
        borderBottom: '1px solid #E2E8F0',
        paddingBottom: '8px'
      }}>
        <button
          onClick={() => setActiveTab('overview')}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: 'none',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            background: activeTab === 'overview' ? '#0F172A' : '#F1F5F9',
            color: activeTab === 'overview' ? 'white' : '#475569'
          }}
        >
          Operations Risk Grid
        </button>
        <button
          onClick={() => setActiveTab('map')}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: 'none',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            background: activeTab === 'map' ? '#0F172A' : '#F1F5F9',
            color: activeTab === 'map' ? 'white' : '#475569'
          }}
        >
          Live Spatial Risk Map
        </button>
        <button
          onClick={() => setActiveTab('iot')}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: 'none',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            background: activeTab === 'iot' ? '#0F172A' : '#F1F5F9',
            color: activeTab === 'iot' ? 'white' : '#475569'
          }}
        >
          IoT Sensor Telemetry & Simulation
        </button>
      </div>

      {/* TAB 1: Operations Risk Grid */}
      {activeTab === 'overview' && (
        <>

          <section className="dashboard-grid">
            <article className="panel risk-panel">
              <div className="panel__header">
                <h2>Regional risk summary</h2>
                <span className="panel__tag">{isLiveBackend ? 'SQL Live' : 'Live'}</span>
              </div>

              <div className="risk-table">
                <div className="risk-table__head">
                  <span>District</span>
                  <span>Flood</span>
                  <span>Landslide</span>
                  <span>Status</span>
                </div>

                {zoneSummary.map((zone) => (
                  <div key={zone.district} className="risk-table__row">
                    <span>{zone.district}</span>
                    <span>
                      <div className="mini-bar">
                        <span style={{ width: `${zone.flood}%` }} className="mini-bar__fill mini-bar__fill--flood" />
                      </div>
                    </span>
                    <span>
                      <div className="mini-bar">
                        <span style={{ width: `${zone.landslide}%` }} className="mini-bar__fill mini-bar__fill--landslide" />
                      </div>
                    </span>
                    <span className={`risk-pill risk-pill--${zone.status.toLowerCase()}`}>{zone.status}</span>
                  </div>
                ))}
              </div>
            </article>

            <article className="panel alert-panel">
              <div className="panel__header">
                <h2>Critical Alerts</h2>
                <span className="panel__tag panel__tag--alert">{alerts.length} active</span>
              </div>

              <div className="alert-list">
                {alerts.map((alert) => (
                  <div key={`${alert.type}-${alert.title}-${alert.time}`} className="alert-item">
                    <div className="alert-item__topline">
                      <span className={`alert-pill alert-pill--${alert.type.toLowerCase()}`}>{alert.type}</span>
                      <span className="alert-time">{alert.time}</span>
                    </div>
                    <h3>{alert.title}</h3>
                    <p>{alert.description}</p>
                    <div className="alert-item__footer">
                      <span className={`severity severity--${alert.severity.toLowerCase()}`}>{alert.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <section className="bottom-grid">
            <article className="panel trend-panel">
              <div className="panel__header">
                <h2>7-day risk trend</h2>
                <span className="panel__tag">Forecast</span>
              </div>

              <div className="trend-chart">
                {trendData.map((point) => (
                  <div key={point.label} className="trend-column">
                    <div className="trend-column__value" style={{ height: `${point.value}%` }} />
                    <span>{point.label}</span>
                  </div>
                ))}
              </div>
            </article>

            <article className="panel action-panel">
              <div className="panel__header">
                <h2>Recommended action</h2>
              </div>

              <ul className="recommendation-list">
                {recommendations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          </section>
        </>
      )}

      {/* TAB 2: Live Spatial Risk Map */}
      {activeTab === 'map' && (
        <div style={{ marginTop: '16px', height: '650px' }}>
          <MapView version="liveMap" />
        </div>
      )}

      {/* TAB 3: IoT Sensor Telemetry Panel */}
      {activeTab === 'iot' && (
        <IoTSensorPanel />
      )}
    </div>
  );
}
