import { useState, useEffect } from 'react';
import {
  FaHandHoldingHeart,
  FaLocationDot,
  FaPhone,
  FaUser,
  FaEnvelope,
  FaPaperPlane,
  FaTriangleExclamation,
  FaCircleCheck,
  FaMapPin,
  FaHandshakeAngle,
  FaFilter,
  FaCircleInfo,
  FaHeartPulse,
  FaListCheck
} from 'react-icons/fa6';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { apiService } from '../services/api';
import 'leaflet/dist/leaflet.css';
import './sathi.css';

// Leaflet default asset fix
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom Icon Generator for Leaflet
const createCustomPinIcon = (color, svgPath) => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="34" height="34" stroke="#ffffff" stroke-width="1.5">
    ${svgPath}
  </svg>`;
  return L.divIcon({
    className: 'custom-sathi-marker',
    html: svg,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34]
  });
};

// 🔴 RED MARKER: Citizen Ground Report Needing Assistance
const citizenHelpIcon = createCustomPinIcon(
  '#E5484D',
  `<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>`
);

// 🟢 GREEN MARKER: Volunteer Help Offered Location
const volunteerHelpIcon = createCustomPinIcon(
  '#0DAFAB',
  `<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm-1 11.5l-3.5-3.5 1.41-1.41L11 10.67l5.09-5.09 1.41 1.41L11 13.5z"/>`
);

// 🔵 BLUE MARKER: Selected Location Pin
const selectedLocationIcon = createCustomPinIcon(
  '#159BD7',
  `<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>`
);

// Map Click Listener Component
function MapClickListener({ onLocationSelected }) {
  useMapEvents({
    click(e) {
      onLocationSelected({
        lat: parseFloat(e.latlng.lat.toFixed(5)),
        lng: parseFloat(e.latlng.lng.toFixed(5))
      });
    }
  });
  return null;
}

export default function Sathi() {
  const [citizenReports, setCitizenReports] = useState([]);
  const [volunteerOffers, setVolunteerOffers] = useState([]);
  const [inventoryLocations, setInventoryLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [volunteerName, setVolunteerName] = useState('');
  const [volunteerPhone, setVolunteerPhone] = useState('');
  const [volunteerEmail, setVolunteerEmail] = useState('');
  const [helpType, setHelpType] = useState('Food & Water Distribution');
  const [locationName, setLocationName] = useState('');
  const [latitude, setLatitude] = useState(26.1445);
  const [longitude, setLongitude] = useState(91.7362);
  const [targetReportId, setTargetReportId] = useState('');
  const [message, setMessage] = useState('');
  
  // Selection pin on map
  const [selectedPin, setSelectedPin] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  // Filter for feed
  const [filterHelpType, setFilterHelpType] = useState('ALL');

  useEffect(() => {
    fetchLiveDatabaseData();
  }, []);

  const fetchLiveDatabaseData = async () => {
    setLoading(true);
    try {
      // 1. Fetch live citizen reports from backend API
      const reports = await apiService.getReports(100).catch(() => []);
      if (Array.isArray(reports)) {
        setCitizenReports(reports);
      }

      // 2. Fetch live volunteer offers from backend API
      const volunteers = await apiService.getVolunteers(100).catch(() => []);
      if (Array.isArray(volunteers)) {
        setVolunteerOffers(volunteers);
      }

      // 3. Fetch original SIH26001 dataset inventory locations for real reference
      const inventory = await apiService.getLandslideInventory(null, 50).catch(() => []);
      if (Array.isArray(inventory)) {
        setInventoryLocations(inventory);
      }
    } catch (err) {
      console.warn('[Sathi] Error fetching live database data:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMapClickLocation = (coords) => {
    setLatitude(coords.lat);
    setLongitude(coords.lng);
    setSelectedPin(coords);
    if (!locationName) {
      setLocationName(`Selected GPS (${coords.lat}, ${coords.lng})`);
    }
    triggerToast(`📍 Location selected on map: Lat ${coords.lat}, Lon ${coords.lng}`);
  };

  const handleSelectCitizenReport = (report) => {
    setTargetReportId(report.id);
    setLatitude(report.latitude);
    setLongitude(report.longitude);
    setLocationName(report.location_name || `Citizen Report #${report.id}`);
    setSelectedPin({ lat: report.latitude, lng: report.longitude });
    triggerToast(`Selected Citizen Report #${report.id} at ${report.location_name || 'specified location'}`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!volunteerName || !volunteerPhone || !locationName) {
      alert('Please fill in all required fields (Name, Phone, and Location)');
      return;
    }

    setSubmitting(true);
    const payload = {
      volunteer_name: volunteerName,
      volunteer_phone: volunteerPhone,
      volunteer_email: volunteerEmail || null,
      help_type: helpType,
      location_name: locationName,
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      target_report_id: targetReportId ? parseInt(targetReportId) : null,
      message: message || ''
    };

    try {
      const response = await apiService.submitVolunteerOffer(payload);
      triggerToast('🟢 Volunteer Help Application recorded in database! Green marker placed on map.');
      
      // Update local state cleanly
      setVolunteerOffers((prev) => [response, ...prev]);

      // Reset form
      setVolunteerName('');
      setVolunteerPhone('');
      setVolunteerEmail('');
      setMessage('');
      setTargetReportId('');
      setSelectedPin(null);
    } catch (err) {
      triggerToast(`⚠️ Submission error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const triggerToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(''), 5000);
  };

  // Filtered feed calculation
  const filteredOffers = volunteerOffers.filter((off) => {
    if (filterHelpType === 'ALL') return true;
    return (off.help_type || '').toLowerCase().includes(filterHelpType.toLowerCase());
  });

  return (
    <div className="sathi-page">
      {/* Toast Alert */}
      {toastMsg && (
        <div className="sathi-toast-banner">
          <FaCircleCheck style={{ color: '#0dafab' }} /> {toastMsg}
        </div>
      )}

      {/* Intro Header */}
      <section className="sathi-intro">
        <div className="sathi-badge-tag">
          <FaHandshakeAngle /> SATHI Disaster Relief & Volunteer Network
        </div>
        <h1>Volunteer Assistance Portal</h1>
        <p>
          Connect directly with citizens requiring emergency relief during landslide and flood hazards. Red markers highlight citizen help requests, and Green markers show registered volunteer assistance points. Select any location on the map to pinpoint your relief base!
        </p>
      </section>

      {/* Analytics Stats Bar */}
      <section className="sathi-stats-row">
        <div className="sathi-stat-pill pill--red">
          <div className="sathi-stat-icon">
            <FaTriangleExclamation />
          </div>
          <div>
            <span className="sathi-stat-label">Citizen Help Needed</span>
            <strong className="sathi-stat-value">{citizenReports.length} Reports</strong>
          </div>
        </div>

        <div className="sathi-stat-pill pill--green">
          <div className="sathi-stat-icon">
            <FaHandHoldingHeart />
          </div>
          <div>
            <span className="sathi-stat-label">Volunteer Responders</span>
            <strong className="sathi-stat-value">{volunteerOffers.length} Registered</strong>
          </div>
        </div>

        <div className="sathi-stat-pill pill--purple">
          <div className="sathi-stat-icon">
            <FaHeartPulse />
          </div>
          <div>
            <span className="sathi-stat-label">Dataset Locations</span>
            <strong className="sathi-stat-value">{inventoryLocations.length > 0 ? '11,026 Incidents' : 'Live DB'}</strong>
          </div>
        </div>
      </section>

      {/* Main Grid Shell */}
      <div className="sathi-shell">
        {/* Left Column: Interactive Leaflet Map */}
        <div className="sathi-map-card">
          <div className="sathi-map-card__header">
            <h3>
              <FaMapPin style={{ color: '#4b3ac2' }} /> Interactive Relief Location Map
            </h3>

            <div className="sathi-legend-group">
              <span className="sathi-legend-badge badge--red-help">🔴 Citizen Need (Red)</span>
              <span className="sathi-legend-badge badge--green-volunteer">🟢 Volunteer Offer (Green)</span>
              {selectedPin && <span className="sathi-legend-badge badge--blue-selected">🔵 Selected Location</span>}
            </div>
          </div>

          <div className="sathi-map-click-hint">
            <FaCircleInfo style={{ color: '#159bd7' }} /> Click anywhere on the map to select a pin for your volunteer offer coordinates!
          </div>

          <div className="sathi-leaflet-wrapper">
            <MapContainer
              center={[26.1445, 91.7362]}
              zoom={11}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {/* Map Click Event Listener */}
              <MapClickListener onLocationSelected={handleMapClickLocation} />

              {/* 🔴 RED MARKERS: Live Citizen Ground Reports */}
              {citizenReports.map((report) => (
                <Marker
                  key={`citizen-${report.id}`}
                  position={[report.latitude, report.longitude]}
                  icon={citizenHelpIcon}
                >
                  <Popup>
                    <div style={{ minWidth: '220px', padding: '2px' }}>
                      <div style={{
                        background: '#FEE2E2',
                        color: '#991B1B',
                        fontWeight: '800',
                        fontSize: '10px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        display: 'inline-block',
                        marginBottom: '4px'
                      }}>
                        🔴 CITIZEN HELP REQUEST
                      </div>
                      <h4 style={{ fontSize: '13px', margin: '0 0 4px 0', color: '#222558' }}>
                        📍 {report.location_name || `Location (${report.latitude}, ${report.longitude})`}
                      </h4>
                      <p style={{ fontSize: '11px', color: '#6B7280', margin: '0 0 6px 0' }}>
                        {report.description || 'No detailed description.'}
                      </p>
                      <div style={{ fontSize: '10px', color: '#4B3AC2', borderTop: '1px solid #E5E7EB', paddingTop: '4px' }}>
                        <strong>Reporter:</strong> {report.reporter_name || 'Citizen'} ({report.reporter_phone || 'N/A'})
                      </div>

                      <button
                        onClick={() => handleSelectCitizenReport(report)}
                        style={{
                          marginTop: '8px',
                          width: '100%',
                          background: 'linear-gradient(135deg, #4B3AC2, #8A3FD1)',
                          color: '#ffffff',
                          border: 'none',
                          padding: '6px 10px',
                          borderRadius: '6px',
                          fontSize: '11px',
                          fontWeight: '700',
                          cursor: 'pointer'
                        }}
                      >
                        🤝 Volunteer to Help This Citizen
                      </button>
                    </div>
                  </Popup>
                </Marker>
              ))}

              {/* 🟢 GREEN MARKERS: Volunteer Help Offers */}
              {volunteerOffers.map((offer) => (
                <Marker
                  key={`volunteer-${offer.id}`}
                  position={[offer.latitude, offer.longitude]}
                  icon={volunteerHelpIcon}
                >
                  <Popup>
                    <div style={{ minWidth: '220px', padding: '2px' }}>
                      <div style={{
                        background: '#E6FFFA',
                        color: '#0DAFAB',
                        fontWeight: '800',
                        fontSize: '10px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        display: 'inline-block',
                        marginBottom: '4px'
                      }}>
                        🟢 VOLUNTEER HELP OFFERED
                      </div>
                      <h4 style={{ fontSize: '13px', margin: '0 0 4px 0', color: '#222558' }}>
                        🙋 {offer.volunteer_name}
                      </h4>
                      <div style={{ fontSize: '11px', fontWeight: '700', color: '#0DAFAB', marginBottom: '4px' }}>
                        Assistance: {offer.help_type}
                      </div>
                      <p style={{ fontSize: '11px', color: '#6B7280', margin: '0 0 6px 0' }}>
                        📍 Base: {offer.location_name}
                      </p>
                      {offer.message && (
                        <p style={{ fontSize: '11px', fontStyle: 'italic', color: '#222558', background: '#F8FAFC', padding: '4px', borderRadius: '4px' }}>
                          "{offer.message}"
                        </p>
                      )}
                      <div style={{ fontSize: '10px', color: '#6B7280', borderTop: '1px solid #E5E7EB', paddingTop: '4px' }}>
                        <strong>Contact:</strong> {offer.volunteer_phone} | <strong>Status:</strong> {offer.status || 'OFFERED'}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}

              {/* 🔵 BLUE MARKER: Draft Selected Pin */}
              {selectedPin && (
                <Marker
                  position={[selectedPin.lat, selectedPin.lng]}
                  icon={selectedLocationIcon}
                >
                  <Popup>
                    <div style={{ fontSize: '11px', fontWeight: '700', color: '#159BD7' }}>
                      🔵 Selected Location Pin<br />
                      Lat: {selectedPin.lat}, Lon: {selectedPin.lng}
                    </div>
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          </div>
        </div>

        {/* Right Column: Volunteer Form Card */}
        <div className="sathi-form-container">
          <h3>
            <FaHandHoldingHeart style={{ color: '#0dafab' }} /> Volunteer Application Form
          </h3>
          <p className="sathi-form-desc">
            Submit your offer to provide food, medical aid, search & rescue, or transport assistance for disaster management.
          </p>

          <form onSubmit={handleSubmit}>
            {/* Volunteer Name */}
            <div className="sathi-field-group">
              <label className="sathi-field-label">
                <FaUser /> Volunteer / Squad Name <span className="required">*</span>
              </label>
              <input
                type="text"
                className="sathi-form-input"
                placeholder="e.g. Rahul Sharma / Guwahati Relief Squad"
                value={volunteerName}
                onChange={(e) => setVolunteerName(e.target.value)}
                required
              />
            </div>

            {/* Phone & Email */}
            <div className="sathi-form-grid-2">
              <div className="sathi-field-group">
                <label className="sathi-field-label">
                  <FaPhone /> Phone <span className="required">*</span>
                </label>
                <input
                  type="tel"
                  className="sathi-form-input"
                  placeholder="+91 98765 43210"
                  value={volunteerPhone}
                  onChange={(e) => setVolunteerPhone(e.target.value)}
                  required
                />
              </div>

              <div className="sathi-field-group">
                <label className="sathi-field-label">
                  <FaEnvelope /> Email
                </label>
                <input
                  type="email"
                  className="sathi-form-input"
                  placeholder="volunteer@sathi.org"
                  value={volunteerEmail}
                  onChange={(e) => setVolunteerEmail(e.target.value)}
                />
              </div>
            </div>

            {/* Assistance Type */}
            <div className="sathi-field-group">
              <label className="sathi-field-label">
                Type of Assistance Offered <span className="required">*</span>
              </label>
              <select
                className="sathi-form-select"
                value={helpType}
                onChange={(e) => setHelpType(e.target.value)}
              >
                <option value="Food & Water Distribution">🍲 Food & Drinking Water Distribution</option>
                <option value="Emergency Rescue & First Aid">🚨 Emergency Search & Rescue</option>
                <option value="Medical Assistance">🩺 Medical & Trauma Support</option>
                <option value="Shelter & Transport">⛺ Temporary Shelter & Transport</option>
                <option value="Clearing Debris & Road Relief">🚜 Clearing Debris & Road Relief</option>
                <option value="General Relief Support">📦 General Relief Support</option>
              </select>
            </div>

            {/* Target Citizen Report Link Dropdown */}
            <div className="sathi-field-group">
              <label className="sathi-field-label">
                <FaTriangleExclamation /> Target Citizen Report (Optional)
              </label>
              <select
                className="sathi-form-select"
                value={targetReportId}
                onChange={(e) => {
                  const val = e.target.value;
                  setTargetReportId(val);
                  if (val) {
                    const found = citizenReports.find((r) => String(r.id) === String(val));
                    if (found) {
                      setLatitude(found.latitude);
                      setLongitude(found.longitude);
                      setLocationName(found.location_name || `Citizen Report #${found.id}`);
                      setSelectedPin({ lat: found.latitude, lng: found.longitude });
                    }
                  }
                }}
              >
                <option value="">General Area Support (No specific report selected)</option>
                {citizenReports.map((r) => (
                  <option key={r.id} value={r.id}>
                    Report #{r.id}: {r.location_name || `Location (${r.latitude}, ${r.longitude})`} ({r.disaster_type?.toUpperCase() || 'LANDSLIDE'})
                  </option>
                ))}
              </select>
            </div>

            {/* Location Name */}
            <div className="sathi-field-group">
              <label className="sathi-field-label">
                <FaLocationDot /> Relief Base / Location Name <span className="required">*</span>
              </label>
              <input
                type="text"
                className="sathi-form-input"
                placeholder="e.g. Khanapara Hill Relief Post"
                value={locationName}
                onChange={(e) => setLocationName(e.target.value)}
                required
              />
            </div>

            {/* Coordinates Display Banner */}
            <div className="sathi-coords-banner">
              <strong>📍 GPS Coordinates: Lat {latitude}° N, Lon {longitude}° E</strong>
              <p>Auto-populated by map click or selecting a citizen report.</p>
            </div>

            {/* Message / Available Resources */}
            <div className="sathi-field-group">
              <label className="sathi-field-label">Message & Available Resources / Equipment</label>
              <textarea
                className="sathi-form-textarea"
                rows={3}
                placeholder="Describe available resources (e.g. 2 relief vans, 300 food packets, first aid kit, emergency ropes)..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
            </div>

            <button
              type="submit"
              className="sathi-btn-submit"
              disabled={submitting}
            >
              <FaPaperPlane /> {submitting ? 'Submitting Application...' : 'Submit Volunteer Help Application'}
            </button>
          </form>
        </div>
      </div>

      {/* Live Registered Volunteers Feed */}
      <section className="sathi-feed-section">
        <div className="sathi-feed-header">
          <h3>
            <FaListCheck style={{ color: '#4b3ac2' }} /> Active Registered Volunteer Applications ({filteredOffers.length})
          </h3>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--color-navy)' }}>
              <FaFilter /> Filter Help Type:
            </label>
            <select
              className="sathi-form-select"
              style={{ width: 'auto', padding: '6px 12px', fontSize: '0.85rem' }}
              value={filterHelpType}
              onChange={(e) => setFilterHelpType(e.target.value)}
            >
              <option value="ALL">All Relief Types</option>
              <option value="Food">Food & Water</option>
              <option value="Rescue">Rescue & First Aid</option>
              <option value="Medical">Medical Support</option>
              <option value="Shelter">Shelter & Transport</option>
            </select>
          </div>
        </div>

        {filteredOffers.length === 0 ? (
          <p style={{ color: 'var(--color-muted)', fontStyle: 'italic' }}>
            No volunteer applications found matching the selected filter in the database.
          </p>
        ) : (
          <div className="sathi-volunteers-grid">
            {filteredOffers.map((offer) => (
              <div key={offer.id} className="sathi-volunteer-card">
                <div className="sathi-card-head">
                  <div>
                    <h4 className="sathi-card-title">{offer.volunteer_name}</h4>
                    <span className="sathi-tag-type">{offer.help_type}</span>
                  </div>
                  <span className={`status-badge status-badge--${(offer.status || 'offered').toLowerCase()}`}>
                    {offer.status || 'OFFERED'}
                  </span>
                </div>

                <div className="sathi-card-location">
                  <FaLocationDot /> {offer.location_name} (GPS: {offer.latitude}, {offer.longitude})
                </div>

                {offer.message && (
                  <div className="sathi-card-msg">"{offer.message}"</div>
                )}

                <div className="sathi-card-meta">
                  <span><FaPhone /> {offer.volunteer_phone}</span>
                  <span>{new Date(offer.created_at || Date.now()).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
