import React from 'react';
import { Info, Play, Pause, FastForward, Activity, Zap } from 'lucide-react';
import { useMineGuard } from '../../context/MineGuardContext';

export function DemoBanner() {
  const { isDemoMode, isStreaming, setIsStreaming, streamSpeed, setStreamSpeed, activeScenario, applyScenario } = useMineGuard();

  if (!isDemoMode) return null;

  return (
    <div style={{
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderBottom: '1px solid rgba(56, 189, 248, 0.25)',
      padding: '8px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: '12px',
      color: 'var(--text-secondary)',
      flexWrap: 'wrap',
      gap: '12px'
    }}>
      {/* Left notice */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          fontWeight: 800,
          backgroundColor: '#38BDF8',
          color: '#090D14',
          padding: '2px 6px',
          borderRadius: '3px',
          letterSpacing: '0.6px'
        }}>
          DEMO MODE
        </span>
        <span>
          Geotechnical sensors & AI predictions are running in <strong>Simulated Live Sandbox</strong>. Data feeds are synthesized for SIH demonstration.
        </span>
      </div>

      {/* Right controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Play/Pause */}
        <button 
          onClick={() => setIsStreaming(!isStreaming)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            fontSize: '11px',
            padding: '3px 8px',
            borderRadius: '4px',
            backgroundColor: isStreaming ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            color: isStreaming ? '#10B981' : '#EF4444',
            border: `1px solid ${isStreaming ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
          }}
          title={isStreaming ? 'Pause Telemetry Simulation Stream' : 'Resume Telemetry Stream'}
        >
          {isStreaming ? <Pause size={12} /> : <Play size={12} />}
          <span>{isStreaming ? 'STREAMING' : 'PAUSED'}</span>
        </button>

        {/* Speed Toggle */}
        <button
          onClick={() => setStreamSpeed(streamSpeed === 1 ? 2 : streamSpeed === 2 ? 5 : 1)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)',
            padding: '3px 8px',
            borderRadius: '4px',
            backgroundColor: 'var(--bg-card)',
            color: 'var(--text-secondary)',
            border: '1px solid var(--border-subtle)'
          }}
          title="Adjust Live Simulation Speed"
        >
          <FastForward size={12} />
          <span>{streamSpeed}x SPEED</span>
        </button>
      </div>
    </div>
  );
}

export default DemoBanner;
