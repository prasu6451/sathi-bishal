import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { apiService } from '../services/api';
import './Pages.css';

// Fix leaflet icon default asset paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const DEFAULT_SECTORS = [
  { id: 'SEC-01', name: 'Majuli Island (Brahmaputra Basin)', pop: 4200, sos: 32, depth: 2.8, access: 15, rain: 165, soil: 0.92, elev: 48, slope: 2.1, lat: 26.95, lon: 94.22 },
  { id: 'SEC-02', name: 'Silchar Urban Lowlands (Barak Valley)', pop: 8500, sos: 48, depth: 3.2, access: 10, rain: 190, soil: 0.95, elev: 35, slope: 1.8, lat: 24.83, lon: 92.80 },
  { id: 'SEC-03', name: 'Guwahati Deepor Beel Catchment', pop: 3100, sos: 14, depth: 1.4, access: 45, rain: 95, soil: 0.78, elev: 65, slope: 4.5, lat: 26.12, lon: 91.68 },
  { id: 'SEC-04', name: 'Kaziranga Buffer Zone (Golaghat)', pop: 1800, sos: 8, depth: 1.9, access: 30, rain: 110, soil: 0.82, elev: 52, slope: 2.0, lat: 26.65, lon: 93.35 },
  { id: 'SEC-05', name: 'Aizawl Tlawng River Valley (Mizoram)', pop: 2200, sos: 19, depth: 1.6, access: 25, rain: 140, soil: 0.88, elev: 450, slope: 28.0, lat: 23.72, lon: 92.71 }
];

export default function DisasterManagement() {
  const [activeTab, setActiveTab] = useState('sos'); // 'sos' | 'priority' | 'resources' | 'route' | 'damage' | 'unified'

  // Module 1 & 2: Rescue Priority & Flood Severity
  const [sectors, setSectors] = useState(DEFAULT_SECTORS);
  const [priorityResults, setPriorityResults] = useState([]);
  const [loadingPriority, setLoadingPriority] = useState(false);

  // Module 3: Resource Allocation
  const [popInput, setPopInput] = useState(3500);
  const [severityInput, setSeverityInput] = useState(0.75);
  const [daysInput, setDaysInput] = useState(3);
  const [medCountInput, setMedCountInput] = useState(8);
  const [resourceResults, setResourceResults] = useState(null);

  // Module 5: SOS NLP Classifier
  const [sosText, setSosText] = useState("Help! Water level reached 2nd floor, pregnant woman and 3 elderly trapped on rooftop without food or dry clothes!");
  const [sosResult, setSosResult] = useState(null);
  const [sosLoading, setSosLoading] = useState(false);

  // Module 6: Damage Assessment
  const [structureType, setStructureType] = useState("BRIDGE");
  const [floodDepth, setFloodDepth] = useState(3.4);
  const [waterVelocity, setWaterVelocity] = useState(2.8);
  const [structMaterial, setStructMaterial] = useState("CONCRETE");
  const [damageResult, setDamageResult] = useState(null);

  // Module 7: Safe Route
  const [originLat, setOriginLat] = useState(26.15);
  const [originLon, setOriginLon] = useState(91.75);
  const [destLat, setDestLat] = useState(26.26);
  const [destLon, setDestLon] = useState(91.92);
  const [routeResult, setRouteResult] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);

  // 1. Initial Evaluation of Priority Queue
  useEffect(() => {
    async function evaluateSectors() {
      setLoadingPriority(true);
      try {
        const results = await Promise.all(
          sectors.map(async (sec) => {
            const res = await apiService.getRescuePriority({
              area_name: sec.name,
              population_density_sqkm: sec.pop / 2.0,
              sos_count: sec.sos,
              vulnerability_index: 0.65,
              flood_depth_m: sec.depth,
              road_accessibility_pct: sec.access
            });
            return { ...sec, ...res };
          })
        );
        // Sort by urgency descending
        results.sort((a, b) => b.urgency_score - a.urgency_score);
        setPriorityResults(results);
      } catch (err) {
        console.warn('Failed to fetch priority ranking:', err);
      } finally {
        setLoadingPriority(false);
      }
    }
    evaluateSectors();
  }, [sectors]);

  // 2. Classify SOS message
  const handleClassifySOS = async (sampleText) => {
    const textToClassify = sampleText || sosText;
    if (!textToClassify.trim()) return;
    setSosLoading(true);
    try {
      const res = await apiService.classifySOSMessage({ message: textToClassify });
      setSosResult(res);
      if (sampleText) setSosText(sampleText);
    } catch (err) {
      console.warn('SOS Classification error:', err);
    } finally {
      setSosLoading(false);
    }
  };

  // Run initial SOS classification
  useEffect(() => {
    handleClassifySOS(sosText);
  }, []);

  // 3. Resource Allocation Calculation
  const handleCalculateResources = async () => {
    try {
      const res = await apiService.getResourceAllocation({
        affected_population: parseInt(popInput) || 1000,
        severity_index: parseFloat(severityInput),
        duration_days: parseInt(daysInput) || 3,
        medical_incident_count: parseInt(medCountInput) || 0
      });
      setResourceResults(res);
    } catch (err) {
      console.warn('Resource calculation error:', err);
    }
  };

  useEffect(() => {
    handleCalculateResources();
  }, [popInput, severityInput, daysInput, medCountInput]);

  // 4. Damage Assessment Calculation
  const handleCalculateDamage = async () => {
    try {
      const res = await apiService.assessDamage({
        structure_type: structureType,
        flood_depth_m: parseFloat(floodDepth),
        water_flow_velocity_mps: parseFloat(waterVelocity),
        construction_material: structMaterial
      });
      setDamageResult(res);
    } catch (err) {
      console.warn('Damage assessment error:', err);
    }
  };

  useEffect(() => {
    handleCalculateDamage();
  }, [structureType, floodDepth, waterVelocity, structMaterial]);

  // 5. Safe Route Calculation
  const handleCalculateRoute = async () => {
    setRouteLoading(true);
    try {
      const res = await apiService.getSafeRoute({
        origin: { latitude: parseFloat(originLat), longitude: parseFloat(originLon) },
        destination: { latitude: parseFloat(destLat), longitude: parseFloat(destLon) },
        hazard_zones: [
          { latitude: 26.20, longitude: 91.82, severity: 0.95, hazard_type: 'FLOOD' },
          { latitude: 26.18, longitude: 91.86, severity: 0.85, hazard_type: 'LANDSLIDE' }
        ]
      });
      setRouteResult(res);
    } catch (err) {
      console.warn('Safe route error:', err);
    } finally {
      setRouteLoading(false);
    }
  };

  useEffect(() => {
    handleCalculateRoute();
  }, []);

  return (
    <div className="page-container" style={{ padding: '24px', maxWidth: '1280px', margin: '0 auto', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      
      {/* Hero Header */}
      <div style={{
        background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
        color: 'white',
        borderRadius: '16px',
        padding: '32px',
        marginBottom: '24px',
        boxShadow: '0 10px 25px -5px rgba(15, 23, 42, 0.3)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#38BDF820', border: '1px solid #38BDF860', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: '600', color: '#38BDF8', marginBottom: '12px' }}>
              <span>●</span> MULTI-HAZARD ML DISASTER MANAGEMENT SUITE
            </div>
            <h1 style={{ margin: '0 0 8px 0', fontSize: '28px', fontWeight: '800' }}>SATHI Emergency Decision Support System</h1>
            <p style={{ margin: 0, color: '#94A3B8', fontSize: '15px', maxWidth: '720px' }}>
              Integrating 7 specialized Machine Learning modules (CNN Severity, Random Forest Rescue Priority, XGBoost Logistics Optimizer, K-Means Clustering, NLP SOS Classifier, Structural Damage, and Safe Route Planning).
            </p>
          </div>
          <div style={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '12px', padding: '16px 20px', textAlign: 'right' }}>
            <div style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>ML Pipeline Engine</div>
            <div style={{ fontSize: '18px', fontWeight: '800', color: '#38BDF8' }}>7 Connected Models</div>
            <div style={{ fontSize: '12px', color: '#22C55E', marginTop: '4px' }}>● All Systems Operational</div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '28px', flexWrap: 'wrap', borderTop: '1px solid #334155', paddingTop: '20px' }}>
          {[
            { id: 'sos', label: '1. SOS NLP Classifier' },
            { id: 'priority', label: '2. Rescue Priority Queue (RF)' },
            { id: 'resources', label: '3. Resource Optimizer (XGB)' },
            { id: 'route', label: '4. Safe Evacuation Routing' },
            { id: 'damage', label: '5. Damage Assessment' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? '#38BDF8' : '#1E293B',
                color: activeTab === tab.id ? '#0F172A' : '#E2E8F0',
                border: activeTab === tab.id ? 'none' : '1px solid #334155',
                padding: '8px 16px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '700',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* TAB 1: SOS NLP CLASSIFIER */}
      {activeTab === 'sos' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>🚨 Citizen SOS Message Intake</h2>
            <p style={{ fontSize: '13px', color: '#64748B', marginBottom: '16px' }}>
              Test NLP message categorization across Medical Emergency, Evacuation/Trapped, Food/Water, and Missing Person requests.
            </p>

            <textarea
              rows={4}
              value={sosText}
              onChange={(e) => setSosText(e.target.value)}
              placeholder="Paste emergency message, tweet, or citizen distress call..."
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '14px',
                boxSizing: 'border-box',
                fontFamily: 'inherit'
              }}
            />

            <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
              <button
                onClick={() => handleClassifySOS()}
                disabled={sosLoading}
                style={{
                  background: '#2563EB',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  fontWeight: '700',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                {sosLoading ? 'Classifying...' : '⚡ Classify Message'}
              </button>
            </div>

            <div style={{ marginTop: '20px' }}>
              <div style={{ fontSize: '12px', fontWeight: '700', color: '#475569', marginBottom: '8px' }}>Or click a realistic scenario:</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {[
                  "Urgent medical help needed: elderly man having cardiac pain on 2nd floor, ambulance cannot cross flooded road!",
                  "Water reaching chest level in Sector 3, 5 family members stranded on roof waiting for rescue boat!",
                  "We have 15 children here with no drinking water or food rations for 48 hours.",
                  "My 8-year-old nephew got separated near Silchar Bridge when the embankment broke, please help find him!"
                ].map((preset, i) => (
                  <button
                    key={i}
                    onClick={() => handleClassifySOS(preset)}
                    style={{
                      background: '#F8FAFC',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '12px',
                      textAlign: 'left',
                      color: '#334155',
                      cursor: 'pointer'
                    }}
                  >
                    "{preset.slice(0, 75)}..."
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Result Card */}
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>📊 NLP Classification Analysis</h2>
            {sosResult ? (
              <div>
                <div style={{
                  background: sosResult.is_critical ? '#FEF2F2' : '#FFFBEB',
                  border: `1px solid ${sosResult.is_critical ? '#FCA5A5' : '#FDE68A'}`,
                  borderRadius: '12px',
                  padding: '16px',
                  marginBottom: '20px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{
                      background: sosResult.is_critical ? '#DC2626' : '#EA580C',
                      color: 'white',
                      padding: '3px 10px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: '800'
                    }}>
                      URGENCY: {sosResult.urgency}
                    </span>
                    <span style={{ fontSize: '13px', fontWeight: '700', color: '#1E293B' }}>
                      Confidence: {Math.round(sosResult.confidence * 100)}%
                    </span>
                  </div>
                  <h3 style={{ margin: '10px 0 4px 0', fontSize: '18px', color: '#0F172A' }}>{sosResult.category_display}</h3>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '12px', color: '#64748B', fontWeight: '700', marginBottom: '8px' }}>Extracted Critical Keywords:</div>
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {sosResult.extracted_keywords?.map((kw, i) => (
                      <span key={i} style={{ background: '#EEF2F6', color: '#1E293B', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: '600' }}>
                        #{kw}
                      </span>
                    ))}
                  </div>
                </div>

                <div style={{ marginTop: '20px' }}>
                  <div style={{ fontSize: '12px', color: '#64748B', fontWeight: '700', marginBottom: '8px' }}>Multi-Class Probability Distribution:</div>
                  {Object.entries(sosResult.probabilities || {}).map(([cat, prob]) => (
                    <div key={cat} style={{ marginBottom: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#334155', marginBottom: '2px' }}>
                        <span>{cat.replace(/_/g, ' ')}</span>
                        <span>{Math.round(prob * 100)}%</span>
                      </div>
                      <div style={{ background: '#F1F5F9', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
                        <div style={{ background: prob > 0.3 ? '#2563EB' : '#94A3B8', height: '100%', width: `${prob * 100}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ color: '#94A3B8', textAlign: 'center', padding: '40px 0' }}>Click "Classify Message" to evaluate.</div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: RESCUE PRIORITY RANKING QUEUE */}
      {activeTab === 'priority' && (
        <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', margin: 0 }}>🚨 Real-Time Rescue Priority Queue (Random Forest Model)</h2>
              <p style={{ fontSize: '13px', color: '#64748B', margin: '4px 0 0 0' }}>
                Continuously ranks affected zones by urgency score based on active SOS count, inundation depth, and demographic vulnerability.
              </p>
            </div>
            <span style={{ background: '#DCFCE7', color: '#166534', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: '700' }}>
              ● Live Model Inference Active
            </span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475569' }}>
                  <th style={{ padding: '12px' }}>Rank & Sector</th>
                  <th style={{ padding: '12px' }}>Priority Level</th>
                  <th style={{ padding: '12px' }}>Urgency Score</th>
                  <th style={{ padding: '12px' }}>Water Depth</th>
                  <th style={{ padding: '12px' }}>SOS Calls</th>
                  <th style={{ padding: '12px' }}>Road Access</th>
                  <th style={{ padding: '12px' }}>Recommended Operational Action</th>
                </tr>
              </thead>
              <tbody>
                {priorityResults.map((sec, idx) => (
                  <tr key={sec.id} style={{ borderBottom: '1px solid #F1F5F9', background: idx === 0 ? '#FEF2F220' : 'transparent' }}>
                    <td style={{ padding: '12px', fontWeight: '700', color: '#0F172A' }}>
                      <span style={{ display: 'inline-block', width: '24px', height: '24px', borderRadius: '50%', background: idx === 0 ? '#DC2626' : '#64748B', color: 'white', textAlign: 'center', lineHeight: '24px', fontSize: '11px', marginRight: '8px' }}>
                        {idx + 1}
                      </span>
                      {sec.name}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span style={{
                        background: sec.badge_color ? `${sec.badge_color}20` : '#F1F5F9',
                        color: sec.badge_color || '#334155',
                        border: `1px solid ${sec.badge_color || '#CBD5E1'}`,
                        padding: '3px 8px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '800'
                      }}>
                        {sec.priority_tier?.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '12px', fontWeight: '700', color: '#1E293B' }}>
                      {sec.urgency_score ? (sec.urgency_score * 100).toFixed(1) + '%' : '—'}
                    </td>
                    <td style={{ padding: '12px', color: '#2563EB', fontWeight: '700' }}>
                      {sec.depth} m
                    </td>
                    <td style={{ padding: '12px', color: '#DC2626', fontWeight: '700' }}>
                      {sec.sos} Alerts
                    </td>
                    <td style={{ padding: '12px', color: sec.access < 20 ? '#DC2626' : '#16A34A', fontWeight: '700' }}>
                      {sec.access}%
                    </td>
                    <td style={{ padding: '12px', color: '#334155' }}>
                      {sec.recommended_action}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: RESOURCE ALLOCATION OPTIMIZER */}
      {activeTab === 'resources' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>⚙️ Relief Logistics Inputs</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Affected Population Count:</label>
                <input
                  type="number"
                  value={popInput}
                  onChange={(e) => setPopInput(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Disaster Severity Index: {severityInput}</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={severityInput}
                  onChange={(e) => setSeverityInput(e.target.value)}
                  style={{ width: '100%', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Operational Duration (Days):</label>
                <input
                  type="number"
                  value={daysInput}
                  onChange={(e) => setDaysInput(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', marginTop: '4px' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Critical Medical Emergencies:</label>
                <input
                  type="number"
                  value={medCountInput}
                  onChange={(e) => setMedCountInput(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #CBD5E1', marginTop: '4px' }}
                />
              </div>
            </div>
          </div>

          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>📦 XGBoost Optimized Relief Allocation</h2>
            {resourceResults && resourceResults.allocations ? (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '20px' }}>
                  <div style={{ background: '#EFF6FF', border: '1px solid #BFDBFE', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#1E40AF', fontWeight: '700' }}>💧 Clean Drinking Water</div>
                    <div style={{ fontSize: '24px', fontWeight: '800', color: '#1E3A8A', marginTop: '4px' }}>
                      {resourceResults.allocations.clean_water_litres?.toLocaleString()} L
                    </div>
                    <div style={{ fontSize: '11px', color: '#60A5FA', marginTop: '2px' }}>Sphere Standard: 3.5L/person/day</div>
                  </div>

                  <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#166534', fontWeight: '700' }}>🍞 Food Ration Packs</div>
                    <div style={{ fontSize: '24px', fontWeight: '800', color: '#14532D', marginTop: '4px' }}>
                      {resourceResults.allocations.food_ration_packs?.toLocaleString()} Packs
                    </div>
                    <div style={{ fontSize: '11px', color: '#4ADE80', marginTop: '2px' }}>Daily fortified caloric intake</div>
                  </div>

                  <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#991B1B', fontWeight: '700' }}>🩺 Medical Trauma Kits</div>
                    <div style={{ fontSize: '24px', fontWeight: '800', color: '#7F1D1D', marginTop: '4px' }}>
                      {resourceResults.allocations.medical_trauma_kits} Kits
                    </div>
                    <div style={{ fontSize: '11px', color: '#F87171', marginTop: '2px' }}>Triage & wound care supplies</div>
                  </div>

                  <div style={{ background: '#FAF5FF', border: '1px solid #E9D5FF', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#6B21A8', fontWeight: '700' }}>🚤 Motorized Rescue Boats</div>
                    <div style={{ fontSize: '24px', fontWeight: '800', color: '#581C87', marginTop: '4px' }}>
                      {resourceResults.allocations.rescue_boats} Boats
                    </div>
                    <div style={{ fontSize: '11px', color: '#C084FC', marginTop: '2px' }}>Inflatable swift-water crafts</div>
                  </div>

                  <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#92400E', fontWeight: '700' }}>👷 Rescue Personnel Teams</div>
                    <div style={{ fontSize: '24px', fontWeight: '800', color: '#78350F', marginTop: '4px' }}>
                      {resourceResults.allocations.personnel_rescue_teams} Teams
                    </div>
                    <div style={{ fontSize: '11px', color: '#FBBF24', marginTop: '2px' }}>NDRF / SDRF Strike Teams</div>
                  </div>

                  <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: '12px', color: '#334155', fontWeight: '700' }}>⛺ Emergency Tarpaulins</div>
                    <div style={{ fontSize: '24px', fontWeight: '800', color: '#0F172A', marginTop: '4px' }}>
                      {resourceResults.allocations.emergency_tarpaulins?.toLocaleString()} Tarps
                    </div>
                    <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>Waterproof shelter kits</div>
                  </div>
                </div>

                <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '12px', fontSize: '13px', color: '#334155' }}>
                  <strong>Logistical Dispatch Note:</strong> {resourceResults.logistical_summary}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* TAB 4: SAFE EVACUATION ROUTE RECOMMENDATION */}
      {activeTab === 'route' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>🗺️ Evacuation Coordinates</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Origin GPS (Affected Community):</label>
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                  <input type="number" step="0.01" value={originLat} onChange={(e) => setOriginLat(e.target.value)} style={{ width: '50%', padding: '6px', borderRadius: '6px', border: '1px solid #CBD5E1' }} />
                  <input type="number" step="0.01" value={originLon} onChange={(e) => setOriginLon(e.target.value)} style={{ width: '50%', padding: '6px', borderRadius: '6px', border: '1px solid #CBD5E1' }} />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Destination GPS (Emergency Shelter):</label>
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                  <input type="number" step="0.01" value={destLat} onChange={(e) => setDestLat(e.target.value)} style={{ width: '50%', padding: '6px', borderRadius: '6px', border: '1px solid #CBD5E1' }} />
                  <input type="number" step="0.01" value={destLon} onChange={(e) => setDestLon(e.target.value)} style={{ width: '50%', padding: '6px', borderRadius: '6px', border: '1px solid #CBD5E1' }} />
                </div>
              </div>

              <button
                onClick={handleCalculateRoute}
                disabled={routeLoading}
                style={{
                  background: '#16A34A',
                  color: 'white',
                  border: 'none',
                  padding: '10px',
                  borderRadius: '8px',
                  fontWeight: '700',
                  fontSize: '14px',
                  cursor: 'pointer',
                  marginTop: '8px'
                }}
              >
                {routeLoading ? 'Computing...' : '🧭 Calculate Safe Route'}
              </button>
            </div>

            {routeResult && (
              <div style={{ marginTop: '20px', borderTop: '1px solid #E2E8F0', paddingTop: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', color: '#64748B' }}>Safe Route Distance:</span>
                  <span style={{ fontSize: '14px', fontWeight: '800', color: '#16A34A' }}>{routeResult.safe_distance_km} km</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', color: '#64748B' }}>Est. Transit Time:</span>
                  <span style={{ fontSize: '14px', fontWeight: '800', color: '#0F172A' }}>{routeResult.estimated_travel_time_mins} mins</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '13px', color: '#64748B' }}>Safety Score:</span>
                  <span style={{ fontSize: '14px', fontWeight: '800', color: '#16A34A' }}>{routeResult.safety_score_pct}%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '13px', color: '#64748B' }}>Hazard Zones Avoided:</span>
                  <span style={{ fontSize: '14px', fontWeight: '800', color: '#DC2626' }}>{routeResult.hazard_zones_avoided} Zones</span>
                </div>
              </div>
            )}
          </div>

          {/* Leaflet Route Map */}
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', overflow: 'hidden', height: '420px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <MapContainer center={[originLat, originLon]} zoom={11} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
              
              {/* Origin Marker */}
              <Marker position={[originLat, originLon]}>
                <Popup>Origin: Affected Area</Popup>
              </Marker>

              {/* Destination Marker */}
              <Marker position={[destLat, destLon]}>
                <Popup>Destination: Safe Shelter</Popup>
              </Marker>

              {/* Simulated Hazard Zones */}
              <Circle center={[26.20, 91.82]} radius={2200} pathOptions={{ color: '#DC2626', fillColor: '#DC2626', fillOpacity: 0.4 }}>
                <Popup>FLOOD HAZARD ZONE (Avoided)</Popup>
              </Circle>
              <Circle center={[26.18, 91.86]} radius={1800} pathOptions={{ color: '#EA580C', fillColor: '#EA580C', fillOpacity: 0.4 }}>
                <Popup>LANDSLIDE VULNERABLE CORRIDOR (Avoided)</Popup>
              </Circle>

              {/* Direct Unsafe Route (Red Dashed) */}
              {routeResult?.direct_hazard_waypoints && (
                <Polyline positions={routeResult.direct_hazard_waypoints} pathOptions={{ color: '#DC2626', dashArray: '5, 10', weight: 3 }} />
              )}

              {/* Safe Detour Route (Green Solid) */}
              {routeResult?.safe_route_waypoints && (
                <Polyline positions={routeResult.safe_route_waypoints} pathOptions={{ color: '#16A34A', weight: 5 }} />
              )}
            </MapContainer>
          </div>
        </div>
      )}

      {/* TAB 5: DAMAGE ASSESSMENT */}
      {activeTab === 'damage' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>🏗️ Structural Inspection Inputs</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Structure Type:</label>
                <select value={structureType} onChange={(e) => setStructureType(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #CBD5E1', marginTop: '4px' }}>
                  <option value="BRIDGE">Bridge / Culvert</option>
                  <option value="BUILDING">Residential / Commercial Building</option>
                  <option value="ROAD">National / State Highway Roadway</option>
                  <option value="POWER_GRID">Electrical Substation / Grid</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Construction Material:</label>
                <select value={structMaterial} onChange={(e) => setStructMaterial(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #CBD5E1', marginTop: '4px' }}>
                  <option value="CONCRETE">Reinforced Concrete</option>
                  <option value="STEEL">Steel Girder</option>
                  <option value="MASONRY">Brick & Mortar Masonry</option>
                  <option value="TIMBER">Timber / Bamboo</option>
                  <option value="MUD_BRICK">Mud / Adobe</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Flood Water Depth: {floodDepth} m</label>
                <input type="range" min="0.1" max="6.0" step="0.1" value={floodDepth} onChange={(e) => setFloodDepth(e.target.value)} style={{ width: '100%', marginTop: '4px' }} />
              </div>

              <div>
                <label style={{ fontSize: '12px', fontWeight: '700', color: '#475569' }}>Flow Velocity: {waterVelocity} m/s</label>
                <input type="range" min="0.5" max="6.0" step="0.1" value={waterVelocity} onChange={(e) => setWaterVelocity(e.target.value)} style={{ width: '100%', marginTop: '4px' }} />
              </div>
            </div>
          </div>

          <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '16px', padding: '24px', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#0F172A', marginTop: 0 }}>📊 Structural Integrity Assessment</h2>
            {damageResult ? (
              <div>
                <div style={{
                  background: damageResult.color_badge ? `${damageResult.color_badge}15` : '#F8FAFC',
                  border: `1px solid ${damageResult.color_badge || '#E2E8F0'}`,
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '20px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: '#475569' }}>Damage Percentage:</span>
                    <span style={{ fontSize: '28px', fontWeight: '900', color: damageResult.color_badge || '#0F172A' }}>
                      {damageResult.damage_percentage}%
                    </span>
                  </div>
                  <h3 style={{ margin: '12px 0 4px 0', fontSize: '18px', color: '#0F172A' }}>
                    Status: {damageResult.functional_status?.replace(/_/g, ' ')}
                  </h3>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: damageResult.color_badge || '#334155', marginTop: '4px' }}>
                    {damageResult.safety_assessment}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#64748B' }}>Hydrodynamic Pressure Index</div>
                    <div style={{ fontSize: '16px', fontWeight: '800', color: '#1E293B', marginTop: '2px' }}>{damageResult.damage_index}</div>
                  </div>

                  <div style={{ background: '#F8FAFC', padding: '12px', borderRadius: '8px' }}>
                    <div style={{ fontSize: '11px', color: '#64748B' }}>Reconstruction Multiplier</div>
                    <div style={{ fontSize: '16px', fontWeight: '800', color: '#1E293B', marginTop: '2px' }}>{damageResult.reconstruction_cost_index}x Base</div>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

    </div>
  );
}
