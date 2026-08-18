import React from 'react';
import {
  Server,
  Activity,
  Cpu,
  Database,
  Radio,
  Wifi,
  ShieldAlert,
  CheckCircle2,
  Clock,
  Layers,
  HardDrive,
  RefreshCw
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import { StatusBadge } from '../components/common/StatusBadge';

export function SystemStatusView() {
  const { systemStatus, lastUpdateTime } = useMineGuard();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Banner */}
      <div style={{
        padding: '16px 20px',
        backgroundColor: 'var(--bg-topbar)',
        borderRadius: '8px',
        border: '1px solid rgba(56, 189, 248, 0.3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>
            <Server size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                MineGuard AI Architecture Health & Services
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
                DEMO ENVIRONMENT
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Standalone browser application with client-side telemetry simulation and mock intelligence services.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>
          <span>UPTIME: <strong>{systemStatus.uptime}</strong></span>
          <span>•</span>
          <span>LAST SYNC: <strong>{lastUpdateTime}</strong></span>
        </div>
      </div>

      {/* 4 Infrastructure Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="command-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-tertiary)', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-heading)', textTransform: 'uppercase' }}>
            <Server size={14} color="#10B981" />
            <span>Frontend Runtime</span>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#FFFFFF', marginTop: '6px', fontFamily: 'var(--font-mono)' }}>
            ONLINE (Active)
          </div>
          <div style={{ fontSize: '11px', color: '#10B981', marginTop: '2px' }}>
            React 18 + Vite SPA Localhost
          </div>
        </div>

        <div className="command-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-tertiary)', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-heading)', textTransform: 'uppercase' }}>
            <Database size={14} color="#38BDF8" />
            <span>Backend Integration</span>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#38BDF8', marginTop: '6px', fontFamily: 'var(--font-mono)' }}>
            DEMO LAYER
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Ready for VITE_API_BASE_URL
          </div>
        </div>

        <div className="command-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-tertiary)', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-heading)', textTransform: 'uppercase' }}>
            <Radio size={14} color="#F59E0B" />
            <span>Virtual Sensor Broker</span>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#FFFFFF', marginTop: '6px', fontFamily: 'var(--font-mono)' }}>
            12 Instruments
          </div>
          <div style={{ fontSize: '11px', color: '#F59E0B', marginTop: '2px' }}>
            High-frequency simulation feed
          </div>
        </div>

        <div className="command-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-tertiary)', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-heading)', textTransform: 'uppercase' }}>
            <Cpu size={14} color="#10B981" />
            <span>Client Memory & CPU</span>
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#FFFFFF', marginTop: '6px', fontFamily: 'var(--font-mono)' }}>
            14.2 MB / &lt;1% CPU
          </div>
          <div style={{ fontSize: '11px', color: '#10B981', marginTop: '2px' }}>
            High efficiency vector render
          </div>
        </div>
      </div>

      {/* Services Grid (8 Core Components) */}
      <div className="command-card" style={{ padding: 0 }}>
        <div style={{
          padding: '14px 18px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-topbar)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div className="card-title-group">
            <Layers size={16} color="var(--text-accent)" />
            <h3 className="card-title">System Module Diagnostics & Status</h3>
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
            8 Core Modules
          </span>
        </div>

        <div className="command-table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table className="command-table">
            <thead>
              <tr>
                <th>Service / Node</th>
                <th>Subsystem Type</th>
                <th>Version / Profile</th>
                <th>Execution Mode</th>
                <th>Latency</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Description</th>
              </tr>
            </thead>
            <tbody>
              {systemStatus.systemComponents.map(comp => (
                <tr key={comp.id}>
                  <td style={{ fontWeight: 700, color: '#FFFFFF' }}>
                    {comp.name}
                  </td>
                  <td style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    {comp.type}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-accent)' }}>
                    {comp.version}
                  </td>
                  <td>
                    <span style={{
                      fontSize: '10px',
                      fontFamily: 'var(--font-mono)',
                      padding: '2px 6px',
                      borderRadius: '3px',
                      backgroundColor: 'rgba(255,255,255,0.06)',
                      color: 'var(--text-secondary)'
                    }}>
                      {comp.mode}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#10B981' }}>
                    {comp.latency}
                  </td>
                  <td>
                    <StatusBadge status={comp.status} />
                  </td>
                  <td style={{ textAlign: 'right', fontSize: '11px', color: 'var(--text-tertiary)', maxWidth: '300px' }}>
                    {comp.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default SystemStatusView;
