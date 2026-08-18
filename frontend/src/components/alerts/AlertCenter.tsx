import React from 'react';
import { Bell, AlertTriangle, ShieldAlert, CheckCircle2, Clock } from 'lucide-react';
import { AlertEvent } from '../../types/telemetry';
import { formatTimestamp } from '../../utils/formatting';

interface AlertCenterProps {
  alerts: AlertEvent[];
  loading?: boolean;
  onRefresh?: () => void;
}

export const AlertCenter: React.FC<AlertCenterProps> = ({ alerts, loading, onRefresh }) => {
  return (
    <div className="cmd-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="cmd-panel-header">
        <div className="cmd-panel-title">
          <Bell size={16} color="#f87171" />
          <span>Geotechnical Safety Alert Center</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge" style={{
            background: alerts.length > 0 ? 'rgba(239, 68, 68, 0.18)' : 'rgba(16, 185, 129, 0.12)',
            color: alerts.length > 0 ? '#f87171' : '#34d399',
            border: alerts.length > 0 ? '1px solid rgba(239, 68, 68, 0.4)' : '1px solid rgba(16, 185, 129, 0.3)',
          }}>
            {alerts.length} Events Dispatched
          </span>
        </div>
      </div>

      <div
        className="cmd-panel-body"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
          maxHeight: '340px',
          overflowY: 'auto',
        }}
      >
        {alerts.length === 0 ? (
          <div
            style={{
              padding: '36px 16px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              gap: '8px',
            }}
          >
            <CheckCircle2 size={32} color="#10b981" />
            <strong style={{ color: 'var(--text-secondary)' }}>No Safety Alerts Triggered</strong>
            <p style={{ fontSize: '0.75rem', maxWidth: '320px' }}>
              Slope kinematics are within stable baseline operational bounds. Automated alerts trigger upon detection of HIGH or CRITICAL risk scores.
            </p>
          </div>
        ) : (
          alerts.map((alert, idx) => {
            const isCrit = alert.risk_level === 'CRITICAL';
            return (
              <div
                key={alert.alert_id || idx}
                style={{
                  background: isCrit ? 'rgba(239, 68, 68, 0.08)' : 'var(--bg-panel-elevated)',
                  border: `1px solid ${isCrit ? 'rgba(239, 68, 68, 0.45)' : 'rgba(249, 115, 22, 0.35)'}`,
                  borderRadius: 'var(--radius-sm)',
                  padding: '12px 14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  boxShadow: isCrit ? '0 0 10px rgba(239, 68, 68, 0.15)' : 'none',
                }}
              >
                {/* Alert Top Row */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {isCrit ? <ShieldAlert size={16} color="#ef4444" /> : <AlertTriangle size={16} color="#f97316" />}
                    <strong style={{
                      fontSize: '0.8rem',
                      color: isCrit ? '#f87171' : '#fb923c',
                      fontFamily: 'var(--font-mono)',
                    }}>
                      [{alert.alert_id}]
                    </strong>
                    <span className={`badge ${isCrit ? 'badge-critical' : 'badge-high'}`} style={{ fontSize: '0.65rem' }}>
                      {alert.risk_level} ({alert.risk_score.toFixed(1)})
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.68rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    <Clock size={11} />
                    <span>{formatTimestamp(alert.timestamp)}</span>
                  </div>
                </div>

                {/* Alert Message */}
                <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', lineHeight: 1.3 }}>
                  {alert.message}
                </div>

                {/* Target & Action Summary */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '6px',
                  paddingTop: '4px',
                  borderTop: '1px solid var(--border-subtle)',
                  fontSize: '0.7rem',
                }}>
                  <div style={{ color: 'var(--text-muted)' }}>
                    Zone: <strong style={{ color: 'var(--text-secondary)' }}>{alert.zone_id}</strong> | Mine: <strong style={{ color: 'var(--text-secondary)' }}>{alert.mine_id}</strong>
                  </div>
                  {alert.recommended_action && (
                    <div style={{ color: '#fbbf24', fontStyle: 'italic' }}>
                      Action: {alert.recommended_action}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
