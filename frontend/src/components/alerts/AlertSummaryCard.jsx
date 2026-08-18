import React from 'react';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export function AlertSummaryCard({ alerts = [], onFilterSelect = null, currentFilter = 'ALL' }) {
  const counts = {
    CRITICAL: alerts.filter(a => a.severity === 'CRITICAL' && a.status !== 'RESOLVED').length,
    HIGH: alerts.filter(a => a.severity === 'HIGH' && a.status !== 'RESOLVED').length,
    MODERATE: alerts.filter(a => a.severity === 'MODERATE' && a.status !== 'RESOLVED').length,
    LOW: alerts.filter(a => a.severity === 'LOW' && a.status !== 'RESOLVED').length,
    RESOLVED: alerts.filter(a => a.status === 'RESOLVED').length
  };

  const cards = [
    { key: 'CRITICAL', label: 'CRITICAL HAZARDS', count: counts.CRITICAL, color: '#EF4444', icon: AlertOctagon },
    { key: 'HIGH', label: 'HIGH RISK ALERTS', count: counts.HIGH, color: '#F97316', icon: AlertTriangle },
    { key: 'MODERATE', label: 'MODERATE WARNINGS', count: counts.MODERATE, color: '#F59E0B', icon: AlertTriangle },
    { key: 'LOW', label: 'LOW / ADVISORIES', count: counts.LOW, color: '#38BDF8', icon: Info },
    { key: 'RESOLVED', label: 'RESOLVED LOGS', count: counts.RESOLVED, color: '#10B981', icon: CheckCircle2 }
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '12px', marginBottom: '20px' }}>
      {cards.map(c => {
        const Icon = c.icon;
        const isSelected = currentFilter === c.key;
        return (
          <div
            key={c.key}
            onClick={() => onFilterSelect && onFilterSelect(c.key)}
            style={{
              padding: '14px 16px',
              backgroundColor: 'var(--bg-card)',
              border: `1px solid ${isSelected ? c.color : 'var(--border-subtle)'}`,
              borderRadius: '8px',
              cursor: onFilterSelect ? 'pointer' : 'default',
              transition: 'all 0.15s ease',
              boxShadow: isSelected ? `0 0 12px ${c.color}33` : 'none'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-tertiary)', letterSpacing: '0.6px', fontFamily: 'var(--font-heading)' }}>
                {c.label}
              </span>
              <Icon size={15} color={c.color} />
            </div>

            <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: c.count > 0 && c.key === 'CRITICAL' ? '#EF4444' : '#FFFFFF' }}>
              {c.count}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default AlertSummaryCard;
