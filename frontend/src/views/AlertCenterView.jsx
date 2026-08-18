import React, { useState } from 'react';
import {
  Bell,
  AlertTriangle,
  Volume2,
  VolumeX,
  Radio,
  FileSpreadsheet,
  Download,
  Filter
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import AlertSummaryCard from '../components/alerts/AlertSummaryCard';
import AlertTable from '../components/alerts/AlertTable';
import AlertModal from '../components/alerts/AlertModal';

export function AlertCenterView() {
  const {
    alerts,
    selectedAlert,
    setSelectedAlert,
    activeAlarmTriggered,
    setActiveAlarmTriggered
  } = useMineGuard();

  const [activeFilter, setActiveFilter] = useState('ALL');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Banner & Siren Control */}
      <div style={{
        padding: '16px 20px',
        backgroundColor: 'var(--bg-topbar)',
        borderRadius: '8px',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#EF4444' }}>
            <Bell size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                Geotechnical Early Warning & Incident Command
              </h2>
              <span style={{
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 800,
                color: '#38BDF8',
                backgroundColor: 'rgba(56, 189, 248, 0.15)',
                border: '1px solid rgba(56, 189, 248, 0.35)',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                DEMO ALERTS
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Automated hazard triage, acoustic siren triggers, and safety evacuation action plans.
            </p>
          </div>
        </div>

        {/* Audio Siren Broadcast toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            onClick={() => setActiveAlarmTriggered(!activeAlarmTriggered)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '6px',
              backgroundColor: activeAlarmTriggered ? 'rgba(245, 158, 11, 0.18)' : 'var(--bg-card)',
              color: activeAlarmTriggered ? '#F59E0B' : 'var(--text-secondary)',
              border: `1px solid ${activeAlarmTriggered ? 'rgba(245, 158, 11, 0.4)' : 'var(--border-subtle)'}`,
              fontSize: '12px',
              fontWeight: 600
            }}
          >
            {activeAlarmTriggered ? <Volume2 size={15} /> : <VolumeX size={15} />}
            <span>{activeAlarmTriggered ? 'Siren Audio Active' : 'Siren Silenced'}</span>
          </button>
        </div>
      </div>

      {/* Top 5 Summary Cards */}
      <AlertSummaryCard
        alerts={alerts}
        currentFilter={activeFilter}
        onFilterSelect={setActiveFilter}
      />

      {/* Main Alert List Table */}
      <AlertTable
        alerts={alerts}
        initialFilter={activeFilter}
        onSelectAlert={alert => setSelectedAlert(alert)}
      />

      {/* Interactive Geotechnical Emergency Action Modal */}
      {selectedAlert && (
        <AlertModal
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
        />
      )}
    </div>
  );
}

export default AlertCenterView;
