import React from 'react';
import { X, AlertOctagon, CheckCircle2, ShieldAlert, Radio, Clock, MapPin, CheckSquare, Square, Volume2, ArrowRight } from 'lucide-react';
import { RiskBadge, StatusBadge } from '../common/StatusBadge';
import { useMineGuard } from '../../context/MineGuardContext';

export function AlertModal({ alert, onClose }) {
  const { acknowledgeAlert, resolveAlert, toggleActionPlanStep, setCurrentTab, selectZoneById } = useMineGuard();

  if (!alert) return null;

  return (
    <div className="modal-center-container" onClick={onClose}>
      <div className="modal-content-card" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-medium)',
          backgroundColor: 'var(--bg-topbar)',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '12px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <RiskBadge level={alert.severity} />
              <StatusBadge status={alert.status} />
              <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>
                {alert.id}
              </span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '18px', fontWeight: 700, color: '#FFFFFF' }}>
              {alert.title}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <MapPin size={13} color="var(--text-accent)" />
                <strong>{alert.zoneName}</strong> ({alert.zoneId})
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={13} />
                {alert.timestamp}
              </span>
            </div>
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
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Geotechnical Readings at Trigger */}
          {alert.readings && (
            <div style={{
              padding: '14px',
              backgroundColor: 'var(--bg-card-subtle)',
              borderRadius: '8px',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Radio size={13} color="#38BDF8" />
                Trigger Sensor Readings
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
                {Object.entries(alert.readings).map(([k, val]) => (
                  <div key={k} style={{ padding: '8px 10px', backgroundColor: 'var(--bg-card)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'capitalize' }}>{k}</span>
                    <div style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#FFFFFF', marginTop: '2px' }}>
                      {val}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Description & Root Cause */}
          <div>
            <h4 style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '6px' }}>
              Incident Description & Geological Context
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, backgroundColor: 'var(--bg-card-subtle)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              {alert.description}
            </p>
          </div>

          {/* Recommended Response */}
          <div style={{
            padding: '14px',
            backgroundColor: alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            borderRadius: '8px',
            border: `1px solid ${alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.35)' : 'rgba(245, 158, 11, 0.35)'}`
          }}>
            <h4 style={{
              fontSize: '12px',
              fontWeight: 700,
              color: alert.severity === 'CRITICAL' ? '#EF4444' : '#F59E0B',
              textTransform: 'uppercase',
              marginBottom: '6px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <ShieldAlert size={15} />
              Recommended Safety Protocol
            </h4>
            <p style={{ fontSize: '13px', color: '#FFFFFF', lineHeight: 1.5 }}>
              {alert.recommendedResponse}
            </p>
          </div>

          {/* Action Checklist */}
          {alert.actionPlan && alert.actionPlan.length > 0 && (
            <div>
              <h4 style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', marginBottom: '8px' }}>
                Geotechnical Emergency Mitigation Checklist
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {alert.actionPlan.map((step, idx) => (
                  <div
                    key={idx}
                    onClick={() => toggleActionPlanStep(alert.id, idx)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '8px 12px',
                      backgroundColor: 'var(--bg-card-subtle)',
                      borderRadius: '6px',
                      border: '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                      fontSize: '12px',
                      color: step.completed ? 'var(--text-tertiary)' : '#FFFFFF',
                      textDecoration: step.completed ? 'line-through' : 'none'
                    }}
                  >
                    {step.completed ? (
                      <CheckSquare size={16} color="#10B981" />
                    ) : (
                      <Square size={16} color="var(--text-tertiary)" />
                    )}
                    <span>{step.step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Author & Verification metadata */}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-tertiary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
            <span>Source: <strong>{alert.author || 'AI Detection Engine'}</strong></span>
            <span>Model Confidence: <strong>{alert.confidence || '92%'}</strong></span>
          </div>
        </div>

        {/* Modal Footer Controls */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-topbar)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '10px'
        }}>
          <button
            onClick={() => {
              onClose();
              selectZoneById(alert.zoneId);
              setCurrentTab('mine-map');
            }}
            style={{
              padding: '8px 14px',
              borderRadius: '6px',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-primary)',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span>View {alert.zoneId} on Mine Map</span>
            <ArrowRight size={14} />
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {alert.status === 'ACTIVE' && (
              <button
                onClick={() => acknowledgeAlert(alert.id)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(56, 189, 248, 0.15)',
                  border: '1px solid rgba(56, 189, 248, 0.4)',
                  color: '#38BDF8',
                  fontSize: '12px',
                  fontWeight: 700
                }}
              >
                Acknowledge Alert
              </button>
            )}

            {alert.status !== 'RESOLVED' && (
              <button
                onClick={() => resolveAlert(alert.id)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '6px',
                  backgroundColor: '#10B981',
                  border: 'none',
                  color: '#090D14',
                  fontSize: '12px',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <CheckCircle2 size={14} />
                <span>Mark Resolved</span>
              </button>
            )}

            {alert.status === 'RESOLVED' && (
              <span style={{ fontSize: '12px', color: '#10B981', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={14} />
                Incident Resolved & Shift Logged
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AlertModal;
