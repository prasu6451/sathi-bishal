import { useState } from 'react';
import { apiService } from '../services/api';

export default function CitizenReportCard() {
  const [lat, setLat] = useState('26.15');
  const [lon, setLon] = useState('91.75');
  const [severity, setSeverity] = useState(3);
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setStatus(null);

    try {
      const res = await apiService.submitReport({
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        severity: parseInt(severity, 10),
        description
      });

      setStatus({ type: 'success', message: `Report #${res.id} submitted successfully! Stored for monitoring/confirmation (excluded from AI input to prevent leakage).` });
      setDescription('');
    } catch (err) {
      setStatus({ type: 'error', message: err.message || 'Failed to submit report.' });
    } finally {
      setSubmitting(false);
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
      <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#0F172A' }}>Submit Citizen Landslide Report</h3>
      <p style={{ fontSize: '12px', color: '#64748B', margin: '0 0 16px 0' }}>
        Report visible hillside cracks or slope movements. Citizen observations are stored for ground-truth confirmation and monitoring.
      </p>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '12px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: '#475569', marginBottom: '4px' }}>Latitude</label>
            <input
              type="number"
              step="any"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '13px' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: '#475569', marginBottom: '4px' }}>Longitude</label>
            <input
              type="number"
              step="any"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '13px' }}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: '#475569', marginBottom: '4px' }}>Severity (1-5)</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '13px' }}
            >
              <option value={1}>1 - Minor Soil Creep</option>
              <option value={2}>2 - Small Cracks</option>
              <option value={3}>3 - Moderate Movement</option>
              <option value={4}>4 - Major Debris Slide</option>
              <option value={5}>5 - Catastrophic Landslide</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '600', color: '#475569', marginBottom: '4px' }}>Observation Description</label>
            <input
              type="text"
              placeholder="e.g. Visible 2cm wide cracks near road slope..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '13px' }}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={submitting}
          style={{
            background: '#2563EB',
            color: 'white',
            border: 'none',
            padding: '10px 16px',
            borderRadius: '6px',
            fontWeight: '600',
            fontSize: '13px',
            cursor: 'pointer',
            justifySelf: 'start',
            marginTop: '4px'
          }}
        >
          {submitting ? 'Submitting...' : 'Submit Observation Report'}
        </button>

        {status && (
          <div style={{
            padding: '10px',
            borderRadius: '6px',
            fontSize: '12px',
            background: status.type === 'success' ? '#DCFCE7' : '#FEE2E2',
            color: status.type === 'success' ? '#166534' : '#991B1B'
          }}>
            {status.message}
          </div>
        )}
      </form>
    </div>
  );
}
