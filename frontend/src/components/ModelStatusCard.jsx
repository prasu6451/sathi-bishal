import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export default function ModelStatusCard() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await apiService.getModelStatus();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError('Backend model status service unavailable.');
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
  }, []);

  if (loading) {
    return <div style={{ padding: '16px', background: '#F8FAFC', borderRadius: '8px', fontSize: '13px' }}>Loading AI model status...</div>;
  }

  if (error || !status) {
    return (
      <div style={{ padding: '16px', background: '#FEF2F2', border: '1px solid #FCA5A5', borderRadius: '8px', color: '#991B1B', fontSize: '13px' }}>
        <strong>Model Status Unavailable</strong>: {error}
      </div>
    );
  }

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
        <h3 style={{ margin: 0, fontSize: '16px', color: '#0F172A' }}>SATHI AI Model Status</h3>
        <span style={{
          background: status.loaded ? '#DCFCE7' : '#FEE2E2',
          color: status.loaded ? '#166534' : '#991B1B',
          padding: '2px 8px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: '700'
        }}>
          {status.loaded ? 'ONLINE' : 'OFFLINE'}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '12px' }}>
        <div style={{ background: '#F8FAFC', padding: '10px', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#64748B' }}>Model Version</div>
          <div style={{ fontSize: '14px', fontWeight: '700', color: '#1E293B' }}>{status.model_version}</div>
        </div>

        <div style={{ background: '#F8FAFC', padding: '10px', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#64748B' }}>Input Features</div>
          <div style={{ fontSize: '14px', fontWeight: '700', color: '#1E293B' }}>{status.feature_count} Vector Dims</div>
        </div>

        <div style={{ background: '#F8FAFC', padding: '10px', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#64748B' }}>Decision Threshold</div>
          <div style={{ fontSize: '14px', fontWeight: '700', color: '#1E293B' }}>{status.threshold}</div>
        </div>

        <div style={{ background: '#F8FAFC', padding: '10px', borderRadius: '8px' }}>
          <div style={{ fontSize: '11px', color: '#64748B' }}>AlphaEarth Status</div>
          <div style={{
            fontSize: '12px',
            fontWeight: '700',
            color: status.alphaearth_status === 'VERIFIED' ? '#16A34A' : '#D97706'
          }}>
            {status.alphaearth_status === 'VERIFIED' ? '● VERIFIED (Satellite Active)' : (status.alphaearth_status || 'UNVERIFIED')}
          </div>
        </div>

      </div>
    </div>
  );
}
