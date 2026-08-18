import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, Info } from 'lucide-react';

export function RiskBadge({ level = 'LOW', score = null, size = 'md' }) {
  const normalized = (level || 'LOW').toUpperCase();
  
  const getIcon = () => {
    switch (normalized) {
      case 'CRITICAL':
        return <AlertOctagon size={size === 'sm' ? 12 : 14} />;
      case 'HIGH':
        return <AlertTriangle size={size === 'sm' ? 12 : 14} />;
      case 'MODERATE':
        return <AlertTriangle size={size === 'sm' ? 12 : 14} />;
      default:
        return <ShieldCheck size={size === 'sm' ? 12 : 14} />;
    }
  };

  return (
    <span className={`risk-badge ${normalized}`} style={{ fontSize: size === 'sm' ? '10px' : '11px', padding: size === 'sm' ? '2px 6px' : '3px 8px' }}>
      {getIcon()}
      <span>{normalized}</span>
      {score !== null && <span style={{ opacity: 0.85, fontWeight: 500 }}>({score}%)</span>}
    </span>
  );
}

export function StatusBadge({ status = 'ONLINE', type = 'status' }) {
  const norm = (status || '').toUpperCase();
  let bg = 'rgba(255, 255, 255, 0.05)';
  let color = '#9CA3AF';
  let border = 'rgba(255, 255, 255, 0.1)';

  if (norm === 'ONLINE' || norm === 'STABLE' || norm === 'RESOLVED' || norm === 'ACTIVE') {
    bg = 'rgba(16, 185, 129, 0.12)';
    color = '#10B981';
    border = 'rgba(16, 185, 129, 0.3)';
  } else if (norm === 'DEMO' || norm === 'SIMULATED' || norm === 'ACKNOWLEDGED') {
    bg = 'rgba(56, 189, 248, 0.12)';
    color = '#38BDF8';
    border = 'rgba(56, 189, 248, 0.3)';
  } else if (norm === 'WARNING' || norm === 'ELEVATED' || norm === 'DEGRADED') {
    bg = 'rgba(245, 158, 11, 0.12)';
    color = '#F59E0B';
    border = 'rgba(245, 158, 11, 0.3)';
  } else if (norm === 'CRITICAL' || norm === 'OFFLINE' || norm === 'CRITICAL_ALERT') {
    bg = 'rgba(239, 68, 68, 0.15)';
    color = '#EF4444';
    border = 'rgba(239, 68, 68, 0.4)';
  }

  return (
    <span 
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '10px',
        fontWeight: 600,
        fontFamily: 'var(--font-mono)',
        backgroundColor: bg,
        color: color,
        border: `1px solid ${border}`,
        letterSpacing: '0.5px'
      }}
    >
      <span style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: color }} />
      {status}
    </span>
  );
}

export default { RiskBadge, StatusBadge };
