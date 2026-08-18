import React from 'react';
import { AlertOctagon, Wrench, ShieldAlert } from 'lucide-react';
import { PredictionStatus } from '../../types/telemetry';

interface DegradedStateBannerProps {
  status: PredictionStatus;
  confidence: number;
}

export const DegradedStateBanner: React.FC<DegradedStateBannerProps> = ({ status, confidence }) => {
  if (status !== 'DEGRADED') return null;

  return (
    <div
      style={{
        background: 'linear-gradient(90deg, rgba(239, 68, 68, 0.25) 0%, rgba(245, 158, 11, 0.2) 100%)',
        border: '1px solid #ef4444',
        borderRadius: 'var(--radius-md)',
        padding: '12px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        boxShadow: '0 0 15px rgba(239, 68, 68, 0.3)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#f87171',
        }}>
          <AlertOctagon size={22} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <strong style={{ fontSize: '0.92rem', color: '#fecaca', letterSpacing: '0.04em' }}>
              DATA DEGRADED — HARDWARE SENSOR FAULT DETECTED
            </strong>
            <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>
              FAULT
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: '#fca5a5', marginTop: '2px' }}>
            Telemetry stream is currently flatlined or reporting anomalous zero-variance signals. Model confidence dropped to{' '}
            <strong>{(confidence * 100).toFixed(0)}%</strong>. Operators must perform on-site sensor inspection.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid #ef4444',
          color: '#f87171',
          padding: '6px 12px',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.75rem',
          fontFamily: 'var(--font-mono)',
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <Wrench size={13} />
          ACTION: VERIFY HARDWARE
        </span>
      </div>
    </div>
  );
};
