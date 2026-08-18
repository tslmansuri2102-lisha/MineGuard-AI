import React from 'react';

export function MineLegend() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      padding: '8px 14px',
      backgroundColor: 'var(--bg-card-subtle)',
      borderRadius: '6px',
      border: '1px solid var(--border-subtle)',
      flexWrap: 'wrap',
      fontSize: '11px',
      fontFamily: 'var(--font-mono)'
    }}>
      <span style={{ color: 'var(--text-tertiary)', fontWeight: 700, textTransform: 'uppercase' }}>
        RISK LEGEND:
      </span>
      <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--risk-low)' }}>
        <span style={{ width: '10px', height: '10px', borderRadius: '2px', backgroundColor: 'var(--risk-low)' }} />
        LOW (0-35%)
      </span>
      <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--risk-moderate)' }}>
        <span style={{ width: '10px', height: '10px', borderRadius: '2px', backgroundColor: 'var(--risk-moderate)' }} />
        MODERATE (36-60%)
      </span>
      <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--risk-high)' }}>
        <span style={{ width: '10px', height: '10px', borderRadius: '2px', backgroundColor: 'var(--risk-high)' }} />
        HIGH (61-80%)
      </span>
      <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--risk-critical)' }}>
        <span style={{ width: '10px', height: '10px', borderRadius: '2px', backgroundColor: 'var(--risk-critical)' }} />
        CRITICAL (81-100%)
      </span>

      <span style={{ height: '12px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />

      <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#F59E0B' }}>
        <span style={{ width: '14px', height: '2px', borderTop: '2px dashed #F59E0B' }} />
        Haul Road
      </span>
      <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#38BDF8' }}>
        <span style={{ width: '7px', height: '7px', borderRadius: '50%', border: '1.5px solid #38BDF8' }} />
        Sensor Node
      </span>
    </div>
  );
}

export default MineLegend;
