import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Radio,
  Server,
  Activity,
  Clock,
  Play,
  Square,
  AlertTriangle,
} from 'lucide-react';
import { ConnectionState, ScenarioType, SimulationStatus } from '../../types/telemetry';
import { formatTimestamp } from '../../utils/formatting';

interface HeaderProps {
  backendOnline: boolean;
  wsState: ConnectionState;
  simStatus: SimulationStatus | null;
  activeScenario: ScenarioType | string;
  lastTimestamp?: string;
}

export const Header: React.FC<HeaderProps> = ({
  backendOnline,
  wsState,
  simStatus,
  activeScenario,
  lastTimestamp,
}) => {
  const [currentTime, setCurrentTime] = useState<string>(new Date().toISOString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toISOString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const isRunning = simStatus?.is_running ?? true;

  return (
    <header className="cmd-header" style={{
      background: 'linear-gradient(180deg, #0f172a 0%, #090d16 100%)',
      borderBottom: '1px solid var(--border-medium)',
      padding: '14px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px',
    }}>
      {/* Brand & Subtitle */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '8px',
          background: 'rgba(56, 189, 248, 0.12)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#38bdf8',
        }}>
          <ShieldAlert size={26} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{
              fontSize: '1.25rem',
              fontWeight: 800,
              letterSpacing: '0.06em',
              color: '#f8fafc',
              textTransform: 'uppercase',
            }}>
              MineGuard AI
            </h1>
            <span className="badge" style={{
              background: 'rgba(56, 189, 248, 0.15)',
              color: '#38bdf8',
              border: '1px solid rgba(56, 189, 248, 0.35)',
              fontSize: '0.65rem',
              fontWeight: 700,
            }}>
              SIH 2026
            </span>
          </div>
          <p style={{
            fontSize: '0.75rem',
            letterSpacing: '0.08em',
            color: 'var(--text-secondary)',
            fontWeight: 600,
            textTransform: 'uppercase',
            marginTop: '1px',
          }}>
            Intelligent Mine Safety Command Center
          </p>
        </div>
      </div>

      {/* System Status Indicators */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        flexWrap: 'wrap',
      }}>
        {/* Backend Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-panel)',
          padding: '6px 12px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
        }}>
          <Server size={14} color="var(--text-muted)" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>BACKEND:</span>
          <span className={`badge ${backendOnline ? 'badge-online' : 'badge-offline'}`}>
            <span className={`ping-indicator ${backendOnline ? '' : 'ping-indicator-critical'}`} style={{ width: '6px', height: '6px' }} />
            {backendOnline ? 'ONLINE' : 'OFFLINE'}
          </span>
        </div>

        {/* WebSocket Stream Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-panel)',
          padding: '6px 12px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
        }}>
          <Radio size={14} color="var(--text-muted)" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>WEBSOCKET:</span>
          <span className={`badge ${
            wsState === 'CONNECTED' ? 'badge-online' : wsState === 'RECONNECTING' ? 'badge-reconnecting' : 'badge-offline'
          }`}>
            <span className={`ping-indicator ${
              wsState === 'CONNECTED' ? '' : wsState === 'RECONNECTING' ? 'ping-indicator-warning' : 'ping-indicator-critical'
            }`} style={{ width: '6px', height: '6px' }} />
            {wsState}
          </span>
        </div>

        {/* Current Scenario */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-panel)',
          padding: '6px 12px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
        }}>
          <Activity size={14} color="var(--text-muted)" />
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SCENARIO:</span>
          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            color: '#38bdf8',
            fontFamily: 'var(--font-mono)',
          }}>
            {activeScenario}
          </span>
        </div>

        {/* Simulation State */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-panel)',
          padding: '6px 12px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
        }}>
          {isRunning ? <Play size={13} color="#10b981" /> : <Square size={13} color="#ef4444" />}
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SIMULATION:</span>
          <span className={`badge ${isRunning ? 'badge-online' : 'badge-offline'}`}>
            {isRunning ? 'RUNNING' : 'STOPPED'}
          </span>
        </div>

        {/* UTC Clock */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: 'var(--bg-panel-elevated)',
          padding: '6px 12px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-medium)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.75rem',
          color: 'var(--text-primary)',
        }}>
          <Clock size={14} color="#38bdf8" />
          <span>{formatTimestamp(currentTime)}</span>
        </div>
      </div>
    </header>
  );
};
