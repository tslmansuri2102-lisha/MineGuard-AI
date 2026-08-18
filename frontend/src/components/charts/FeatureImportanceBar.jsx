import React from 'react';
import { RiskBadge } from '../common/StatusBadge';

export function FeatureImportanceBar({ factors = [] }) {
  if (!factors || factors.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {factors.map((factor, index) => (
        <div 
          key={index}
          style={{
            padding: '12px 14px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            transition: 'all 0.15s ease'
          }}
        >
          {/* Top row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '13px', color: '#FFFFFF' }}>
                {factor.factor}
              </span>
              <span style={{
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                color: factor.color,
                backgroundColor: `${factor.color}15`,
                border: `1px solid ${factor.color}40`,
                padding: '1px 6px',
                borderRadius: '3px'
              }}>
                {factor.impact}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>
                {factor.metric}
              </span>
              <span style={{ fontSize: '13px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#FFFFFF' }}>
                {factor.weight}%
              </span>
            </div>
          </div>

          {/* Progress bar */}
          <div style={{ height: '6px', width: '100%', backgroundColor: 'rgba(255, 255, 255, 0.06)', borderRadius: '3px', overflow: 'hidden', marginBottom: '6px' }}>
            <div 
              style={{
                height: '100%',
                width: `${factor.weight}%`,
                backgroundColor: factor.color,
                borderRadius: '3px',
                transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            />
          </div>

          {/* Geotechnical explanation text */}
          <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            {factor.contributionText}
          </p>
        </div>
      ))}
    </div>
  );
}

export default FeatureImportanceBar;
