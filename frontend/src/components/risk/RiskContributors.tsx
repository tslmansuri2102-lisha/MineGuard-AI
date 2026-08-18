import React from 'react';
import { Layers, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { RiskFactor } from '../../types/telemetry';
import { formatFeatureName, getImpactColor } from '../../utils/formatting';

interface RiskContributorsProps {
  factors: RiskFactor[];
}

export const RiskContributors: React.FC<RiskContributorsProps> = ({ factors }) => {
  const displayFactors = factors && factors.length > 0
    ? factors
    : [{ feature: 'baseline_stability', impact: 'LOW' }];

  return (
    <div className="cmd-panel">
      <div className="cmd-panel-header">
        <div className="cmd-panel-title">
          <Layers size={16} color="#38bdf8" />
          <span>Root-Cause Threat Attribution</span>
        </div>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {displayFactors.length} Factors Identified
        </span>
      </div>

      <div className="cmd-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {displayFactors.map((factor, index) => {
          const colors = getImpactColor(factor.impact);
          const isBaseline = factor.feature === 'baseline_stability';

          return (
            <div
              key={`${factor.feature}-${index}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 12px',
                background: 'var(--bg-panel-elevated)',
                borderRadius: 'var(--radius-sm)',
                border: `1px solid ${colors.border}`,
                transition: 'transform 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{
                  width: '22px',
                  height: '22px',
                  borderRadius: '50%',
                  background: colors.bg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: colors.text,
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                }}>
                  {index + 1}
                </span>
                <div>
                  <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {formatFeatureName(factor.feature)}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    feature: {factor.feature}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span
                  className="badge"
                  style={{
                    background: colors.bg,
                    color: colors.text,
                    border: `1px solid ${colors.border}`,
                    fontSize: '0.7rem',
                    fontWeight: 700,
                  }}
                >
                  {isBaseline ? <CheckCircle2 size={11} /> : <ArrowUpRight size={11} />}
                  {factor.impact.toUpperCase()} IMPACT
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
