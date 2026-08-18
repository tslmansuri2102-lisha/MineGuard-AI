import React, { useState } from 'react';
import {
  Gauge,
  Activity,
  CloudRain,
  MoveDiagonal,
  Thermometer,
  ShieldAlert,
  Radio,
  BatteryCharging,
  Wifi,
  Sliders,
  Download,
  Calendar
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import Sparkline from '../components/charts/Sparkline';
import TelemetryMultiChart from '../components/charts/TelemetryMultiChart';
import { RiskBadge, StatusBadge } from '../components/common/StatusBadge';
import { TELEMETRY_METRICS_INFO } from '../data/mockTelemetry';

export function TelemetryView() {
  const { liveTelemetry, telemetryHistory, sensors, lastUpdateTime } = useMineGuard();
  const [timeRange, setTimeRange] = useState('24H');
  const [activeMetric, setActiveMetric] = useState('all');

  const telemetryCards = [
    {
      id: 'vibration',
      info: TELEMETRY_METRICS_INFO.vibration,
      data: liveTelemetry.vibration,
      color: '#F97316',
      icon: Activity
    },
    {
      id: 'rainfall',
      info: TELEMETRY_METRICS_INFO.rainfall,
      data: liveTelemetry.rainfall,
      color: '#38BDF8',
      icon: CloudRain
    },
    {
      id: 'displacement',
      info: TELEMETRY_METRICS_INFO.displacement,
      data: liveTelemetry.displacement,
      color: '#EF4444',
      icon: MoveDiagonal
    },
    {
      id: 'porePressure',
      info: TELEMETRY_METRICS_INFO.porePressure,
      data: liveTelemetry.porePressure,
      color: '#A855F7',
      icon: Gauge
    },
    {
      id: 'temperature',
      info: TELEMETRY_METRICS_INFO.temperature,
      data: liveTelemetry.temperature,
      color: '#F59E0B',
      icon: Thermometer
    },
    {
      id: 'slopeStability',
      info: TELEMETRY_METRICS_INFO.slopeStability,
      data: liveTelemetry.slopeStability,
      color: '#10B981',
      icon: ShieldAlert
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Telemetry Header */}
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
          <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>
            <Gauge size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                Highwall Sensor Telemetry & Geotechnical Analytics
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
                DEMO TELEMETRY
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Multi-channel borehole extensometers, piezometric arrays, and seismographic station feeds.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>
          <span>STREAM: <strong>12 NODES ACTIVE</strong></span>
          <span>•</span>
          <span>LAST PACKET: <strong>{lastUpdateTime}</strong></span>
        </div>
      </div>

      {/* 6 Key Telemetry Instrument Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: '16px' }}>
        {telemetryCards.map(c => {
          const Icon = c.icon;
          const isCritical = c.data.status === 'CRITICAL';
          const isHigh = c.data.status === 'HIGH';

          return (
            <div
              key={c.id}
              className={`command-card ${isCritical ? 'hazard-highlight' : ''}`}
              style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ padding: '6px', borderRadius: '6px', backgroundColor: `${c.color}15`, color: c.color }}>
                      <Icon size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>{c.info.shortName}</div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>{c.info.sensorType}</div>
                    </div>
                  </div>

                  <RiskBadge level={c.data.status || 'LOW'} size="sm" />
                </div>

                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: '6px 0', lineHeight: 1.4 }}>
                  {c.info.description}
                </div>
              </div>

              <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                      <span style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: isCritical ? '#EF4444' : isHigh ? '#F97316' : '#FFFFFF' }}>
                        {c.data.value}
                      </span>
                      <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: 600 }}>
                        {c.info.unit}
                      </span>
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                      Baseline: {c.info.normalRange}
                    </div>
                  </div>

                  <div style={{ paddingBottom: '2px' }}>
                    <Sparkline data={c.data.sparkline} color={c.color} width={120} height={32} />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Large Historical Multi-Parameter Telemetry Chart */}
      <div className="command-card">
        <div style={{ marginBottom: '14px' }}>
          <h3 className="card-title" style={{ marginBottom: '4px' }}>
            Historical Telemetry Trajectory ({timeRange})
          </h3>
          <p className="card-subtitle">
            Synchronized multi-channel sensor correlation over selected historical timeframe.
          </p>
        </div>

        <TelemetryMultiChart
          data={telemetryHistory}
          height={300}
          activeMetric={activeMetric}
          timeRange={timeRange}
          onMetricChange={setActiveMetric}
          onTimeRangeChange={setTimeRange}
        />
      </div>

      {/* Physical Sensor Fleet Hardware Grid */}
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
            <Radio size={16} color="var(--text-accent)" />
            <h3 className="card-title">Geotechnical Sensor Fleet Diagnostics</h3>
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
            {sensors.length} Installed Instruments
          </span>
        </div>

        <div className="command-table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table className="command-table">
            <thead>
              <tr>
                <th>Sensor ID</th>
                <th>Instrument Type</th>
                <th>Pit Location</th>
                <th>Live Reading</th>
                <th>Status</th>
                <th>Battery Level</th>
                <th>Signal (SNR)</th>
                <th>Sampling Interval</th>
                <th style={{ textAlign: 'right' }}>Calibration Date</th>
              </tr>
            </thead>
            <tbody>
              {sensors.map(sensor => (
                <tr key={sensor.id}>
                  <td style={{ fontWeight: 700, color: 'var(--text-accent)', fontFamily: 'var(--font-mono)' }}>
                    {sensor.id}
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: '#FFFFFF' }}>{sensor.type}</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>{sensor.zone}</div>
                  </td>
                  <td style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>{sensor.location}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: sensor.status === 'CRITICAL_ALERT' ? '#EF4444' : '#FFFFFF' }}>
                    {sensor.reading}
                  </td>
                  <td>
                    <StatusBadge status={sensor.status} />
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                    <span style={{ color: '#10B981' }}>{sensor.battery}</span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-secondary)' }}>
                    {sensor.signalStrength}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                    {sensor.samplingInterval}
                  </td>
                  <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                    {sensor.lastCalibrated}
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

export default TelemetryView;
