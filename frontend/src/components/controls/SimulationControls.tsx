import React, { useState } from 'react';
import { Sliders, Play, Square, RefreshCw, Zap, AlertTriangle, CheckCircle2, Shield } from 'lucide-react';
import { ScenarioType, SimulationStatus } from '../../types/telemetry';
import { SCENARIOS } from '../../utils/constants';

interface SimulationControlsProps {
  status: SimulationStatus | null;
  loading?: boolean;
  onStart: (scenario: ScenarioType | string, interval: number, seed: number | null) => Promise<any>;
  onStop: () => Promise<any>;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  status,
  loading = false,
  onStart,
  onStop,
}) => {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioType>(
    (status?.scenario as ScenarioType) || 'NORMAL'
  );
  const [intervalSec, setIntervalSec] = useState<number>(status?.interval_seconds ?? 1.0);
  const [seed, setSeed] = useState<number | null>(42);
  const [actionError, setActionError] = useState<string | null>(null);

  const isRunning = status?.is_running ?? true;
  const currentScenarioMeta = SCENARIOS.find((s) => s.id === selectedScenario) || SCENARIOS[0];

  const handleStart = async (scenarioToStart = selectedScenario) => {
    setActionError(null);
    try {
      await onStart(scenarioToStart, intervalSec, seed);
    } catch (err: any) {
      setActionError(err?.message || 'Failed to start scenario');
    }
  };

  const handleStop = async () => {
    setActionError(null);
    try {
      await onStop();
    } catch (err: any) {
      setActionError(err?.message || 'Failed to stop simulation');
    }
  };

  const handleQuickPreset = async (sc: ScenarioType) => {
    setSelectedScenario(sc);
    await handleStart(sc);
  };

  return (
    <div className="cmd-panel">
      <div className="cmd-panel-header">
        <div className="cmd-panel-title">
          <Sliders size={16} color="#38bdf8" />
          <span>Physics Simulation & Scenario Orchestration</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            Readings Generated: <strong style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{status?.reading_count ?? 0}</strong>
          </span>
        </div>
      </div>

      <div className="cmd-panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {/* Main Controls Row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr 1fr auto',
            gap: '12px',
            alignItems: 'end',
          }}
        >
          {/* Scenario Selector */}
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Select Scenario Profile (All 8 Available)
            </label>
            <select
              className="select-input"
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value as ScenarioType)}
              disabled={loading}
              style={{ fontWeight: 600 }}
            >
              {SCENARIOS.map((sc) => (
                <option key={sc.id} value={sc.id}>
                  {sc.label} — {sc.expectedRisk}
                </option>
              ))}
            </select>
          </div>

          {/* Interval Control */}
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Interval: <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{intervalSec}s</span>
            </label>
            <input
              type="range"
              min="0.1"
              max="3.0"
              step="0.1"
              value={intervalSec}
              onChange={(e) => setIntervalSec(parseFloat(e.target.value))}
              disabled={loading}
              style={{ width: '100%', accentColor: '#38bdf8', cursor: 'pointer' }}
            />
          </div>

          {/* Seed Input */}
          <div>
            <label style={{ display: 'block', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '4px', textTransform: 'uppercase' }}>
              Random Seed (0-9999)
            </label>
            <input
              type="number"
              className="text-input"
              value={seed ?? ''}
              placeholder="Random"
              onChange={(e) => setSeed(e.target.value ? parseInt(e.target.value, 10) : null)}
              disabled={loading}
              style={{ fontFamily: 'var(--font-mono)' }}
            />
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              className="btn btn-primary"
              onClick={() => handleStart()}
              disabled={loading}
              style={{ minWidth: '110px' }}
            >
              <Play size={14} />
              {isRunning && status?.scenario === selectedScenario ? 'Reconfigure' : 'Start'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleStop}
              disabled={loading || !isRunning}
            >
              <Square size={14} color="#ef4444" />
              Stop
            </button>
          </div>
        </div>

        {/* Selected Scenario Description Card */}
        <div
          style={{
            padding: '10px 14px',
            background: 'var(--bg-panel-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.75rem',
            gap: '12px',
          }}
        >
          <div>
            <strong style={{ color: '#38bdf8' }}>{currentScenarioMeta.label}:</strong>{' '}
            <span style={{ color: 'var(--text-secondary)' }}>{currentScenarioMeta.description}</span>
          </div>
          <span className="badge" style={{ background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', flexShrink: 0 }}>
            Target: {currentScenarioMeta.expectedRisk}
          </span>
        </div>

        {/* Error message */}
        {actionError && (
          <div style={{ color: '#f87171', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={14} />
            <span>{actionError}</span>
          </div>
        )}

        {/* Quick Demo Workflow Presets */}
        <div>
          <span style={{ display: 'block', fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            SIH Demonstration Quick Scenario Presets
          </span>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(135px, 1fr))',
              gap: '6px',
            }}
          >
            <button
              className="btn btn-secondary"
              onClick={() => handleQuickPreset('NORMAL')}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '6px 8px' }}
            >
              🟢 1. Normal
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleQuickPreset('HEAVY_RAIN')}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '6px 8px' }}
            >
              🌧️ 2. Heavy Rain
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleQuickPreset('PROGRESSIVE_INSTABILITY')}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '6px 8px' }}
            >
              📈 3. Instability
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleQuickPreset('CRITICAL_COMBINED')}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '6px 8px', borderColor: 'rgba(239, 68, 68, 0.5)', color: '#f87171' }}
            >
              🔴 4. Critical (Alert)
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleQuickPreset('SENSOR_FAILURE')}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '6px 8px', borderColor: 'rgba(245, 158, 11, 0.5)', color: '#fbbf24' }}
            >
              ⚠️ 5. Fault
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleQuickPreset('RECOVERY')}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '6px 8px', borderColor: 'rgba(16, 185, 129, 0.5)', color: '#34d399' }}
            >
              🔄 6. Recovery
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
