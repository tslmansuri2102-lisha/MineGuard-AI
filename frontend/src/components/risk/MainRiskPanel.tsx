import React from 'react';
import {
  AlertOctagon,
  Shield,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
} from 'lucide-react';
import { NormalizedRiskAssessment, SensorTelemetryPayload } from '../../types/telemetry';
import { RISK_LEVEL_CONFIG } from '../../utils/constants';
import { formatNumber, formatTimeOnly } from '../../utils/formatting';

interface MainRiskPanelProps {
  risk: NormalizedRiskAssessment;
  telemetry: SensorTelemetryPayload;
}

export const MainRiskPanel: React.FC<MainRiskPanelProps> = ({ risk, telemetry }) => {
  const config = RISK_LEVEL_CONFIG[risk.level] || RISK_LEVEL_CONFIG.LOW;
  const isDegraded = risk.status === 'DEGRADED';
  const confidencePercent = Math.round(risk.confidence * 100);

  // SVG Gauge calculations (semi-circle arc)
  const radius = 68;
  const strokeWidth = 12;
  const circumference = Math.PI * radius; // 180 deg arc
  const scorePercent = Math.min(100, Math.max(0, risk.score)) / 100;
  const strokeDashoffset = circumference * (1 - scorePercent);

  return (
    <div className="cmd-panel" style={{
      borderColor: isDegraded ? '#f59e0b' : config.borderColor,
      boxShadow: risk.level === 'CRITICAL' && !isDegraded ? `0 0 25px ${config.glowColor}, var(--shadow-panel)` : 'var(--shadow-panel)',
    }}>
      {/* Panel Header */}
      <div className="cmd-panel-header" style={{
        background: isDegraded ? 'rgba(245, 158, 11, 0.08)' : config.bgColor,
        borderBottomColor: config.borderColor,
      }}>
        <div className="cmd-panel-title" style={{ color: config.textColor }}>
          <AlertOctagon size={16} />
          <span>Real-Time Geotechnical Risk Assessment</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${
            risk.level === 'CRITICAL'
              ? 'badge-critical'
              : risk.level === 'HIGH'
              ? 'badge-high'
              : risk.level === 'MODERATE'
              ? 'badge-moderate'
              : 'badge-low'
          }`}>
            {config.badgeText}
          </span>
        </div>
      </div>

      {/* Panel Body */}
      <div className="cmd-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Gauge & Main Score Grid */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}>
          {/* Circular / Arc Gauge Visual */}
          <div style={{ position: 'relative', width: '160px', height: '100px', flexShrink: 0 }}>
            <svg width="160" height="100" viewBox="0 0 160 100">
              {/* Background Arc */}
              <path
                d="M 12 85 A 68 68 0 0 1 148 85"
                fill="none"
                stroke="var(--bg-panel-subtle)"
                strokeWidth={strokeWidth}
                strokeLinecap="round"
              />
              {/* Active Value Arc */}
              <path
                d="M 12 85 A 68 68 0 0 1 148 85"
                fill="none"
                stroke={isDegraded ? '#f59e0b' : config.color}
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                style={{ transition: 'stroke-dashoffset 0.5s ease-out, stroke 0.3s ease' }}
              />
            </svg>
            {/* Center Gauge Readout */}
            <div style={{
              position: 'absolute',
              bottom: '4px',
              left: 0,
              right: 0,
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '1.85rem',
                fontWeight: 800,
                color: isDegraded ? '#fbbf24' : config.textColor,
                lineHeight: 1,
              }}>
                {formatNumber(risk.score, 1)}
              </span>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                / 100 Score
              </span>
            </div>
          </div>

          {/* Risk Level & Target Sensor Info */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
            <div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.06em' }}>
                Geotechnical Threat Level
              </span>
              <div style={{
                fontSize: '1.25rem',
                fontWeight: 800,
                color: config.textColor,
                letterSpacing: '0.04em',
                lineHeight: 1.2,
              }}>
                {config.label}
              </div>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '6px',
              background: 'var(--bg-panel-elevated)',
              padding: '8px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.72rem',
            }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Target Mine:</span>{' '}
                <strong style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{telemetry.mine_id}</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Zone:</span>{' '}
                <strong style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{telemetry.zone_id}</strong>
              </div>
              <div style={{ gridColumn: 'span 2' }}>
                <span style={{ color: 'var(--text-muted)' }}>Sensor Node:</span>{' '}
                <strong style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{telemetry.sensor_id}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Quality & Confidence Status Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '10px',
          paddingTop: '10px',
          borderTop: '1px solid var(--border-subtle)',
        }}>
          {/* Confidence Meter */}
          <div style={{
            background: 'var(--bg-panel-elevated)',
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600 }}>MODEL CONFIDENCE</span>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: confidencePercent < 50 ? '#f87171' : '#34d399',
              }}>
                {confidencePercent}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '5px',
              background: 'var(--bg-panel-subtle)',
              borderRadius: '3px',
              overflow: 'hidden',
            }}>
              <div style={{
                width: `${confidencePercent}%`,
                height: '100%',
                background: confidencePercent < 50 ? '#ef4444' : '#10b981',
                transition: 'width 0.4s ease',
              }} />
            </div>
          </div>

          {/* Data Quality Status */}
          <div style={{
            background: 'var(--bg-panel-elevated)',
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '2px' }}>
              DATA QUALITY STATUS
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {isDegraded ? (
                <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.4)' }}>
                  <AlertTriangle size={12} />
                  DEGRADED
                </span>
              ) : risk.status === 'INSUFFICIENT_DATA' ? (
                <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.4)' }}>
                  <Info size={12} />
                  WARMING UP
                </span>
              ) : (
                <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}>
                  <CheckCircle2 size={12} />
                  NORMAL
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Telemetry Last Updated */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.7rem',
          color: 'var(--text-muted)',
          paddingTop: '4px',
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={12} />
            Last Telemetry Received:
          </span>
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            {formatTimeOnly(telemetry.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
};
