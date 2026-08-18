import React from 'react';
import { Activity } from 'lucide-react';
import { PredictionStatus, SensorValues } from '../../types/telemetry';
import { SensorCard } from './SensorCard';

interface SensorGridProps {
  sensors: SensorValues;
  status: PredictionStatus;
}

export const SensorGrid: React.FC<SensorGridProps> = ({ sensors, status }) => {
  const isDegraded = status === 'DEGRADED';

  const sensorKeys: Array<keyof SensorValues> = [
    'displacement_mm',
    'strain',
    'pore_pressure_kpa',
    'rainfall_mm',
    'temperature_c',
    'vibration_g',
  ];

  return (
    <div className="cmd-panel">
      <div className="cmd-panel-header">
        <div className="cmd-panel-title">
          <Activity size={16} color="#38bdf8" />
          <span>Live In-Situ Sensor Telemetry Grid (6 Channels)</span>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Direct Ingestion Stream
        </span>
      </div>

      <div
        className="cmd-panel-body"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '12px',
        }}
      >
        {sensorKeys.map((key) => (
          <SensorCard
            key={key}
            sensorKey={key}
            value={sensors[key] ?? 0.0}
            isDegraded={isDegraded}
          />
        ))}
      </div>
    </div>
  );
};
