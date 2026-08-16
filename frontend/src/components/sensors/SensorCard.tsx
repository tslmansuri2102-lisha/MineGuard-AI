import React from 'react';
import {
  MoveHorizontal,
  Layers,
  Droplets,
  CloudRain,
  Thermometer,
  Zap,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import { SENSOR_METADATA } from '../../utils/constants';
import { formatNumber } from '../../utils/formatting';

interface SensorCardProps {
  sensorKey: string;
  value: number;
  isDegraded?: boolean;
}

const ICONS_MAP: Record<string, React.ReactNode> = {
  displacement_mm: <MoveHorizontal size={18} />,
  strain: <Layers size={18} />,
  pore_pressure_kpa: <Droplets size={18} />,
  rainfall_mm: <CloudRain size={18} />,
  temperature_c: <Thermometer size={18} />,
  vibration_g: <Zap size={18} />,
};

export const SensorCard: React.FC<SensorCardProps> = ({ sensorKey, value, isDegraded }) => {
  const meta = SENSOR_METADATA[sensorKey] || {
    name: sensorKey,
    unit: '',
    normalMin: 0,
    normalMax: 100,
    description: '',
  };

  const isElevated = value > meta.normalMax && !isDegraded;
  const isHighAlert = value > meta.normalMax * 1.6 && !isDegraded;

  // Percentage for mini progress bar
  const range = meta.normalMax - meta.normalMin || 1;
  const clampedPercent = Math.min(100, Math.max(0, ((value - meta.normalMin) / (range * 1.5)) * 100));

  const icon = ICONS_MAP[sensorKey] || <TrendingUp size={18} />;

  return (
    <div
      className="cmd-panel"
      style={{
        padding: '14px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        border: `1px solid ${
          isDegraded
            ? 'rgba(245, 158, 11, 0.4)'
            : isHighAlert
            ? 'rgba(239, 68, 68, 0.6)'
            : isElevated
            ? 'rgba(249, 115, 22, 0.5)'
            : 'var(--border-subtle)'
        }`,
        background: isHighAlert
          ? 'linear-gradient(180deg, rgba(239, 68, 68, 0.08) 0%, var(--bg-panel) 100%)'
          : 'var(--bg-panel)',
      }}
    >
      {/* Card Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-sm)',
              background: isHighAlert ? 'rgba(239, 68, 68, 0.2)' : 'var(--bg-panel-elevated)',
              color: isHighAlert ? '#f87171' : isElevated ? '#fb923c' : '#38bdf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid var(--border-subtle)',
            }}
          >
            {icon}
          </div>
          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              {meta.name}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {sensorKey}
            </div>
          </div>
        </div>

        {/* Status pill */}
        {isDegraded ? (
          <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', fontSize: '0.65rem' }}>
            FAULT
          </span>
        ) : isHighAlert ? (
          <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>
            SURGE
          </span>
        ) : isElevated ? (
          <span className="badge badge-high" style={{ fontSize: '0.65rem' }}>
            ELEVATED
          </span>
        ) : (
          <span className="badge badge-low" style={{ fontSize: '0.65rem' }}>
            STABLE
          </span>
        )}
      </div>

      {/* Main Numerical Value */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', margin: '4px 0' }}>
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '1.75rem',
            fontWeight: 800,
            color: isDegraded
              ? '#94a3b8'
              : isHighAlert
              ? '#f87171'
              : isElevated
              ? '#fb923c'
              : '#f8fafc',
            lineHeight: 1,
          }}
        >
          {formatNumber(value, sensorKey === 'strain' || sensorKey === 'vibration_g' ? 2 : 1)}
        </span>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
          {meta.unit}
        </span>
      </div>

      {/* Mini Gauge Indicator */}
      <div>
        <div
          style={{
            width: '100%',
            height: '4px',
            background: 'var(--bg-panel-elevated)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${clampedPercent}%`,
              height: '100%',
              background: isDegraded
                ? '#f59e0b'
                : isHighAlert
                ? '#ef4444'
                : isElevated
                ? '#f97316'
                : '#10b981',
              transition: 'width 0.3s ease, background-color 0.3s ease',
            }}
          />
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '0.65rem',
          color: 'var(--text-muted)',
          marginTop: '4px',
          fontFamily: 'var(--font-mono)',
        }}>
          <span>0.0</span>
          <span>Max: {meta.normalMax} {meta.unit}</span>
        </div>
      </div>
    </div>
  );
};
