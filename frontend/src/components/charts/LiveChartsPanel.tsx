import React from 'react';
import { LineChart, Activity } from 'lucide-react';
import { HistoricalTelemetryPoint } from '../../types/telemetry';
import { RollingMetricChart } from './RollingMetricChart';

interface LiveChartsPanelProps {
  history: HistoricalTelemetryPoint[];
}

export const LiveChartsPanel: React.FC<LiveChartsPanelProps> = ({ history }) => {
  return (
    <div className="cmd-panel">
      <div className="cmd-panel-header">
        <div className="cmd-panel-title">
          <LineChart size={16} color="#38bdf8" />
          <span>Real-Time Rolling Telemetry & Risk Kinematics</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          <span className="ping-indicator" />
          <span>Live Stream (Last {history.length} Readings)</span>
        </div>
      </div>

      <div
        className="cmd-panel-body"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '12px',
        }}
      >
        {/* 1. Risk Score History */}
        <RollingMetricChart
          title="AI Risk Score Evolution"
          metricKey="riskScore"
          unit="/ 100"
          history={history}
          strokeColor="#f87171"
          fillColor="#ef4444"
          fixedMin={0}
          fixedMax={100}
        />

        {/* 2. Displacement Magnitude */}
        <RollingMetricChart
          title="Displacement Creep"
          metricKey="displacement_mm"
          unit="mm"
          history={history}
          strokeColor="#38bdf8"
          fillColor="#0284c7"
          fixedMin={0}
        />

        {/* 3. Pore Water Pressure */}
        <RollingMetricChart
          title="Pore Water Pressure"
          metricKey="pore_pressure_kpa"
          unit="kPa"
          history={history}
          strokeColor="#60a5fa"
          fillColor="#3b82f6"
          fixedMin={0}
        />

        {/* 4. Rainfall Accumulation */}
        <RollingMetricChart
          title="Precipitation Infiltration"
          metricKey="rainfall_mm"
          unit="mm"
          history={history}
          strokeColor="#34d399"
          fillColor="#10b981"
          fixedMin={0}
        />

        {/* 5. Dynamic Vibration */}
        <RollingMetricChart
          title="Dynamic Seismic / Blast Vibration"
          metricKey="vibration_g"
          unit="g"
          history={history}
          strokeColor="#fbbf24"
          fillColor="#f59e0b"
          fixedMin={0}
        />
      </div>
    </div>
  );
};
