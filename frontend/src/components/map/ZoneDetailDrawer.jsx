import React from 'react';
import { X, ShieldAlert, AlertTriangle, Layers, Radio, Thermometer, ArrowRight, CheckCircle2 } from 'lucide-react';
import { RiskBadge } from '../common/StatusBadge';
import { useMineGuard } from '../../context/MineGuardContext';

export function ZoneDetailDrawer({ zone, onClose }) {
  const { setCurrentTab, setSelectedAlert, alerts } = useMineGuard();

  if (!zone) return null;

  const zoneAlerts = alerts.filter(a => a.zoneId === zone.id);

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="zone-drawer-panel" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={{
          padding: '18px 22px',
          borderBottom: '1px solid var(--border-medium)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-topbar)'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-accent)', fontWeight: 700 }}>
                {zone.id}
              </span>
              <RiskBadge level={zone.riskLevel} score={zone.riskScore} />
            </div>
            <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '16px', fontWeight: 700, color: '#FFFFFF' }}>
              {zone.name}
            </h3>
          </div>

          <button
            onClick={onClose}
            style={{
              padding: '6px',
              borderRadius: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
              color: 'var(--text-secondary)'
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '20px', flex: 1, overflowY: 'auto' }}>
          {/* Top Metric Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div style={{ padding: '12px', backgroundColor: 'var(--bg-card)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Current Risk Score</span>
              <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#FFFFFF', marginTop: '2px' }}>
                {zone.riskScore}<span style={{ fontSize: '14px', color: 'var(--text-tertiary)' }}>/100</span>
              </div>
            </div>

            <div style={{ padding: '12px', backgroundColor: 'var(--bg-card)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>Status</span>
              <div style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: zone.riskLevel === 'CRITICAL' ? 'var(--risk-critical)' : '#F59E0B', marginTop: '6px' }}>
                {zone.status}
              </div>
            </div>
          </div>

          {/* Geotechnical Characteristics */}
          <div style={{ padding: '14px', backgroundColor: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Layers size={14} color="var(--text-accent)" />
              Geotechnical Profile
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-tertiary)' }}>Sector / Benches</span>
                <span style={{ color: '#FFFFFF', fontWeight: 600 }}>{zone.sector} ({zone.benchLevels})</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-tertiary)' }}>Elevation (RL)</span>
                <span style={{ color: '#FFFFFF', fontFamily: 'var(--font-mono)' }}>{zone.elevation}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-tertiary)' }}>Slope Face Angle</span>
                <span style={{ color: '#FFFFFF', fontFamily: 'var(--font-mono)' }}>{zone.slopeAngle}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-tertiary)' }}>Lithology</span>
                <span style={{ color: '#FFFFFF' }}>{zone.lithology}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-tertiary)' }}>Last Sync</span>
                <span style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>{zone.lastUpdate}</span>
              </div>
            </div>

            <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)', fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {zone.description}
            </div>
          </div>

          {/* Active Geotechnical Sensors */}
          <div style={{ padding: '14px', backgroundColor: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Radio size={14} color="#10B981" />
              Active Field Instruments ({zone.sensors?.length || 0})
            </h4>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {zone.sensors?.map((sId, i) => (
                <span key={i} style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  backgroundColor: 'rgba(56, 189, 248, 0.1)',
                  border: '1px solid rgba(56, 189, 248, 0.25)',
                  color: '#38BDF8',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 600
                }}>
                  {sId}
                </span>
              ))}
            </div>
          </div>

          {/* Active Alerts in this Zone */}
          {zoneAlerts.length > 0 ? (
            <div style={{ padding: '14px', backgroundColor: 'rgba(239, 68, 68, 0.08)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
              <h4 style={{ fontSize: '12px', fontWeight: 700, color: '#EF4444', textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={14} />
                Active Alerts in {zone.id} ({zoneAlerts.length})
              </h4>
              {zoneAlerts.map(alt => (
                <div 
                  key={alt.id}
                  style={{
                    padding: '10px',
                    backgroundColor: 'var(--bg-card)',
                    borderRadius: '6px',
                    border: '1px solid var(--border-subtle)',
                    marginBottom: '8px',
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    setSelectedAlert(alt);
                    setCurrentTab('alerts');
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, fontSize: '12px', color: '#FFFFFF' }}>{alt.title}</span>
                    <RiskBadge level={alt.severity} size="sm" />
                  </div>
                  <p style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{alt.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '12px', backgroundColor: 'var(--bg-card)', borderRadius: '6px', border: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', fontSize: '12px' }}>
              <CheckCircle2 size={16} />
              <span>No active critical alerts in this sector.</span>
            </div>
          )}

          {/* Geotechnical Recommendation Action Box */}
          <div style={{ padding: '14px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '6px' }}>
              RECOMMENDED GEOTECHNICAL RESPONSE
            </h4>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {zone.riskLevel === 'CRITICAL' 
                ? 'Issue immediate evacuation order for Bench L4-L6. Prohibit haul vehicle transit along East Ramp. Dispatch automated UAV lidar inspection flight.' 
                : zone.riskLevel === 'HIGH' 
                ? 'Limit transit speeds on Bench L3 to 15 km/h. Increase piezometer and seismograph sampling frequency to 0.5s.' 
                : 'Maintain routine automated monitoring cycle. Drainage and catch berms clear.'}
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div style={{
          padding: '14px 22px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-topbar)',
          display: 'flex',
          gap: '10px'
        }}>
          <button
            onClick={() => {
              onClose();
              setCurrentTab('telemetry');
            }}
            style={{
              flex: 1,
              padding: '9px 14px',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              color: 'var(--text-primary)',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <span>View Telemetry</span>
            <ArrowRight size={14} />
          </button>

          <button
            onClick={() => {
              onClose();
              setCurrentTab('alerts');
            }}
            style={{
              flex: 1,
              padding: '9px 14px',
              backgroundColor: zone.riskLevel === 'CRITICAL' ? '#EF4444' : '#F59E0B',
              border: 'none',
              borderRadius: '6px',
              color: '#090D14',
              fontSize: '12px',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            <span>Manage Alerts</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ZoneDetailDrawer;
