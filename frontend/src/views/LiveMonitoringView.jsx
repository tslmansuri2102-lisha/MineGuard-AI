import React, { useState } from 'react';
import {
  Activity,
  Play,
  Pause,
  FastForward,
  Zap,
  CloudRain,
  MoveDiagonal,
  Gauge,
  Thermometer,
  ShieldAlert,
  Radio,
  RefreshCw,
  Sliders,
  AlertOctagon,
  ArrowUpRight
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import Sparkline from '../components/charts/Sparkline';
import TelemetryMultiChart from '../components/charts/TelemetryMultiChart';
import { RiskBadge, StatusBadge } from '../components/common/StatusBadge';

export function LiveMonitoringView() {
  const {
    liveTelemetry,
    telemetryHistory,
    isStreaming,
    setIsStreaming,
    streamSpeed,
    setStreamSpeed,
    isDemoMode,
    setIsDemoMode,
    activeScenario,
    applyScenario,
    lastUpdateTime,
    sensors
  } = useMineGuard();

  const [activeChartMetric, setActiveChartMetric] = useState('all');
  const [activeRange, setActiveRange] = useState('1H');

  const streamMetrics = [
    {
      key: 'vibration',
      title: 'Peak Particle Velocity (PPV)',
      sensor: 'Triaxial Geophone VIB-E04',
      value: liveTelemetry.vibration.value,
      unit: 'mm/s',
      status: liveTelemetry.vibration.status,
      sparkline: liveTelemetry.vibration.sparkline,
      color: '#F97316',
      icon: Activity,
      sampling: '100 Hz',
      threshold: 'Critical > 15.0 mm/s',
      desc: 'High-frequency seismographic waveform measuring blast vibration & rock joint crack propagation.'
    },
    {
      key: 'rainfall',
      title: 'Precipitation Inflow Rate',
      sensor: 'Pluviometer RAIN-01',
      value: liveTelemetry.rainfall.value,
      unit: 'mm/h',
      status: liveTelemetry.rainfall.status,
      sparkline: liveTelemetry.rainfall.sparkline,
      color: '#38BDF8',
      icon: CloudRain,
      sampling: '0.1 Hz',
      threshold: 'Warning > 18.0 mm/h',
      desc: 'Optical pulse rain gauge measuring surface runoff intensity and slope saturation risks.'
    },
    {
      key: 'displacement',
      title: 'Subsurface Shear Strain',
      sensor: 'Borehole MPBX DISP-E01',
      value: liveTelemetry.displacement.value,
      unit: 'mm',
      status: liveTelemetry.displacement.status,
      sparkline: liveTelemetry.displacement.sparkline,
      color: '#EF4444',
      icon: MoveDiagonal,
      sampling: '1 Hz',
      threshold: 'Critical > 5.0 mm',
      desc: 'Subsurface multipoint borehole extensometer anchoring through shear failure plane at 35m depth.'
    },
    {
      key: 'porePressure',
      title: 'Piezometric Hydraulic Head',
      sensor: 'Vibrating Piezometer PIEZ-E02',
      value: liveTelemetry.porePressure.value,
      unit: 'kPa',
      status: liveTelemetry.porePressure.status,
      sparkline: liveTelemetry.porePressure.sparkline,
      color: '#A855F7',
      icon: Gauge,
      sampling: '0.2 Hz',
      threshold: 'Critical > 220 kPa',
      desc: 'Monitors groundwater pressure weakening the effective cohesion of highwall bench joints.'
    },
    {
      key: 'temperature',
      title: 'Cliff Face Temperature',
      sensor: 'IR Pyrometer TEMP-01',
      value: liveTelemetry.temperature.value,
      unit: '°C',
      status: 'NORMAL',
      sparkline: liveTelemetry.temperature.sparkline,
      color: '#F59E0B',
      icon: Thermometer,
      sampling: '0.1 Hz',
      threshold: 'Safe range: 10 - 45°C',
      desc: 'Exposed surface rock thermal expansion tracking for solar thermal fracture fatigue.'
    },
    {
      key: 'slopeStability',
      title: 'Real-time Factor of Safety',
      sensor: 'Inclinometer + Radar FoS',
      value: liveTelemetry.slopeStability.value,
      unit: 'FoS',
      status: liveTelemetry.slopeStability.status,
      sparkline: liveTelemetry.slopeStability.sparkline,
      color: '#10B981',
      icon: ShieldAlert,
      sampling: 'Composite Calc',
      threshold: 'Critical < 1.05 FoS',
      desc: 'Continuous limit equilibrium calculation. FoS < 1.0 indicates active slope displacement.'
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Stream Control Header */}
      <div className="command-card" style={{ padding: '16px 20px', backgroundColor: 'var(--bg-topbar)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
          {/* Live Status Indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: '20px',
              backgroundColor: isStreaming ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              border: `1px solid ${isStreaming ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
              color: isStreaming ? '#10B981' : '#EF4444',
              fontFamily: 'var(--font-mono)',
              fontWeight: 700,
              fontSize: '12px'
            }}>
              <span className="pulse-dot" />
              <span>{isStreaming ? '● LIVE SIMULATION ACTIVE' : 'STREAM PAUSED'}</span>
            </div>

            <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
              Last Packet: <strong>{lastUpdateTime}</strong>
            </span>
          </div>

          {/* Mode Toggle: Live Data / Demo Data */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', backgroundColor: 'var(--bg-card)', padding: '3px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <button
                onClick={() => setIsDemoMode(false)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                  backgroundColor: !isDemoMode ? '#38BDF8' : 'transparent',
                  color: !isDemoMode ? '#090D14' : 'var(--text-tertiary)'
                }}
              >
                LIVE DATA
              </button>
              <button
                onClick={() => setIsDemoMode(true)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                  backgroundColor: isDemoMode ? '#F59E0B' : 'transparent',
                  color: isDemoMode ? '#090D14' : 'var(--text-tertiary)'
                }}
              >
                DEMO DATA
              </button>
            </div>

            {/* Play/Pause Button */}
            <button
              onClick={() => setIsStreaming(!isStreaming)}
              className="topbar-btn"
              style={{ color: isStreaming ? '#EF4444' : '#10B981', fontWeight: 700 }}
            >
              {isStreaming ? <Pause size={14} /> : <Play size={14} />}
              <span>{isStreaming ? 'Pause Stream' : 'Resume'}</span>
            </button>

            {/* Speed Multiplier */}
            <button
              onClick={() => setStreamSpeed(streamSpeed === 1 ? 2 : streamSpeed === 2 ? 5 : 1)}
              className="topbar-btn"
              style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}
            >
              <FastForward size={14} />
              <span>{streamSpeed}x</span>
            </button>
          </div>
        </div>

        {/* Hazard Anomaly Injection Bar */}
        <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-secondary)' }}>
            <Zap size={14} color="#F59E0B" />
            <span>Simulate Anomaly Injection:</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            {[
              { id: 'normal', label: 'Nominal Baseline', color: '#10B981' },
              { id: 'storm', label: 'Torrential Rainfall Inflow', color: '#38BDF8' },
              { id: 'microseismic', label: 'Micro-Seismic PPV Spike', color: '#F97316' },
              { id: 'rockfall_hazard', label: 'Critical Planar Shear Creep', color: '#EF4444' }
            ].map(sc => (
              <button
                key={sc.id}
                onClick={() => applyScenario(sc.id)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: 600,
                  fontFamily: 'var(--font-mono)',
                  backgroundColor: activeScenario === sc.id ? `${sc.color}25` : 'var(--bg-card)',
                  color: activeScenario === sc.id ? sc.color : 'var(--text-tertiary)',
                  border: `1px solid ${activeScenario === sc.id ? sc.color : 'var(--border-subtle)'}`
                }}
              >
                {sc.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 6 Real-time Telemetry Monitor Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {streamMetrics.map(metric => {
          const Icon = metric.icon;
          const isCritical = metric.status === 'CRITICAL';
          const isHigh = metric.status === 'HIGH';

          return (
            <div
              key={metric.key}
              className={`command-card ${isCritical ? 'hazard-highlight' : ''}`}
              style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
            >
              {/* Header */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ padding: '6px', borderRadius: '6px', backgroundColor: `${metric.color}18`, color: metric.color }}>
                      <Icon size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>{metric.title}</div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>{metric.sensor}</div>
                    </div>
                  </div>

                  <RiskBadge level={metric.status} size="sm" />
                </div>

                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4, margin: '8px 0' }}>
                  {metric.desc}
                </p>
              </div>

              {/* Large Value & Live Sparkline */}
              <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                      <span style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: isCritical ? '#EF4444' : isHigh ? '#F97316' : '#FFFFFF' }}>
                        {metric.value}
                      </span>
                      <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: 600 }}>
                        {metric.unit}
                      </span>
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
                      {metric.threshold}
                    </div>
                  </div>

                  <div>
                    <Sparkline data={metric.sparkline} color={metric.color} width={130} height={36} />
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
                  <span>Rate: {metric.sampling}</span>
                  <span style={{ color: '#10B981' }}>● TRANSMITTING</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Multi-Stream Dynamic Comparison Chart */}
      <div className="command-card">
        <div style={{ marginBottom: '14px' }}>
          <h3 className="card-title" style={{ marginBottom: '4px' }}>
            Multi-Sensor Real-Time Waveform & Correlation Stream
          </h3>
          <p className="card-subtitle">
            Synchronized highwall geotechnical sensor channels. Values auto-refresh as virtual packets arrive.
          </p>
        </div>

        <TelemetryMultiChart
          data={telemetryHistory}
          height={280}
          activeMetric={activeChartMetric}
          timeRange={activeRange}
          onMetricChange={setActiveChartMetric}
          onTimeRangeChange={setActiveRange}
        />
      </div>
    </div>
  );
}

export default LiveMonitoringView;
