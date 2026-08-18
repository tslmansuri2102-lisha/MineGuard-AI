import React from 'react';
import {
  Bell,
  Radio,
  Clock,
  User,
  ShieldAlert,
  Wifi,
  ChevronDown,
  Volume2,
  VolumeX,
  Sparkles
} from 'lucide-react';
import { useMineGuard } from '../../context/MineGuardContext';

export function Topbar() {
  const {
    isDemoMode,
    isStreaming,
    lastUpdateTime,
    alerts,
    activeAlarmTriggered,
    setActiveAlarmTriggered,
    setCurrentTab,
    setSelectedAlert
  } = useMineGuard();

  const activeAlerts = alerts.filter(a => a.status === 'ACTIVE');
  const criticalAlert = activeAlerts.find(a => a.severity === 'CRITICAL');

  return (
    <header className="command-topbar">
      {/* Left: Site Selector & Sector Status */}
      <div className="topbar-left">
        <div className="mine-site-tag">
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10B981' }} />
          <div>
            <div className="mine-site-name">KADAPA OPEN-PIT COMPLEX</div>
            <div className="mine-site-id">SECTOR 04 — EAST HIGHWALL PIT</div>
          </div>
        </div>

        {/* Live / Demo Mode Indicator */}
        <div className={`live-indicator ${isStreaming ? 'live' : 'demo'}`}>
          <span className="pulse-dot" />
          <span>{isDemoMode ? 'LIVE DEMO' : 'CONNECTED API'}</span>
        </div>
      </div>

      {/* Center: Live Hazard Alarm Banner if active */}
      <div className="topbar-center">
        {criticalAlert && (
          <div
            onClick={() => {
              setSelectedAlert(criticalAlert);
              setCurrentTab('alerts');
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              backgroundColor: 'rgba(239, 68, 68, 0.18)',
              border: '1px solid rgba(239, 68, 68, 0.5)',
              borderRadius: '20px',
              color: '#EF4444',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              animation: 'pulse-critical 1.8s infinite'
            }}
          >
            <ShieldAlert size={15} />
            <span>CRITICAL ALERT: {criticalAlert.title} ({criticalAlert.zoneId})</span>
          </div>
        )}
      </div>

      {/* Right: Telemetry Time, Audio, Notification and Profile */}
      <div className="topbar-right">
        {/* Live sync clock */}
        <div className="topbar-time-chip" title="Last telemetry packet sync timestamp">
          <Clock size={13} color="var(--text-tertiary)" />
          <span>{lastUpdateTime}</span>
        </div>

        {/* Connection status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#10B981', fontFamily: 'var(--font-mono)' }} title="Telemetry Stream Heartbeat: 100% Signal">
          <Wifi size={14} />
          <span>SYNCED</span>
        </div>

        {/* Audio Mute/Unmute toggle for Siren */}
        <button
          className="topbar-btn"
          onClick={() => setActiveAlarmTriggered(!activeAlarmTriggered)}
          title={activeAlarmTriggered ? "Mute Siren & Audio Warnings" : "Enable Siren Audio Warnings"}
        >
          {activeAlarmTriggered ? <Volume2 size={15} color="#F59E0B" /> : <VolumeX size={15} />}
        </button>

        {/* Notifications Icon with active badge */}
        <button
          className="topbar-btn"
          onClick={() => setCurrentTab('alerts')}
          style={{ position: 'relative' }}
          title="Open Alert Center"
        >
          <Bell size={15} />
          {activeAlerts.length > 0 && (
            <span style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              backgroundColor: '#EF4444',
              color: '#FFFFFF',
              fontSize: '9px',
              fontWeight: 800,
              fontFamily: 'var(--font-mono)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {activeAlerts.length}
            </span>
          )}
        </button>

        {/* User / Operator profile */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '4px 10px',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px'
        }}>
          <div style={{
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            backgroundColor: '#38BDF8',
            color: '#090D14',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '11px'
          }}>
            MG
          </div>
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontSize: '11px', fontWeight: 600, color: '#FFFFFF' }}>Eng. Sharma</div>
            <div style={{ fontSize: '9px', color: 'var(--text-tertiary)' }}>Geotech Lead</div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Topbar;
