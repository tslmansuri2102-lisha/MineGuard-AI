import React from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  Activity,
  Layers,
  Clock,
  Radio,
  ExternalLink,
  ArrowRight,
  TrendingUp,
  CloudRain,
  MoveDiagonal,
  Gauge,
  Thermometer,
  ShieldCheck,
  MapPin
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import KPICard from '../components/common/KPICard';
import RiskGauge from '../components/common/RiskGauge';
import RiskTrendChart from '../components/charts/RiskTrendChart';
import ScenarioRunner from '../components/common/ScenarioRunner';
import { RiskBadge, StatusBadge } from '../components/common/StatusBadge';
import MineMap from '../components/map/MineMap';

export function OverviewView() {
  const {
    currentRisk,
    liveTelemetry,
    telemetryHistory,
    zones,
    alerts,
    lastUpdateTime,
    setCurrentTab,
    setSelectedAlert,
    selectZoneById
  } = useMineGuard();

  const activeAlerts = alerts.filter(a => a.status === 'ACTIVE');
  const criticalZones = zones.filter(z => z.riskLevel === 'CRITICAL' || z.riskLevel === 'HIGH');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* SIH Hackathon Scenario Controller */}
      <ScenarioRunner />

      {/* Top 6 KPI Cards */}
      <div className="grid-kpi-row">
        <KPICard
          title="Current Mine Risk"
          value={`${currentRisk.riskScore}%`}
          status={currentRisk.currentRisk}
          statusColor={
            currentRisk.currentRisk === 'CRITICAL' ? '#EF4444' :
            currentRisk.currentRisk === 'HIGH' ? '#F97316' :
            currentRisk.currentRisk === 'MODERATE' ? '#F59E0B' : '#10B981'
          }
          subtitle="Rockfall probability"
          icon={ShieldAlert}
          sparklineData={telemetryHistory.slice(-12).map(h => h.riskScore)}
          sparklineColor={currentRisk.riskScore > 60 ? '#EF4444' : '#10B981'}
          highlight={currentRisk.currentRisk === 'CRITICAL'}
          onClick={() => setCurrentTab('risk-analysis')}
        />

        <KPICard
          title="Active Alerts"
          value={activeAlerts.length}
          unit="active"
          status={activeAlerts.filter(a => a.severity === 'CRITICAL').length > 0 ? 'CRITICAL TRIGGER' : 'MONITORING'}
          statusColor={activeAlerts.some(a => a.severity === 'CRITICAL') ? '#EF4444' : '#38BDF8'}
          subtitle={`${alerts.filter(a => a.status === 'RESOLVED').length} resolved this shift`}
          icon={AlertTriangle}
          onClick={() => setCurrentTab('alerts')}
        />

        <KPICard
          title="Critical Zones"
          value={criticalZones.length}
          unit={`of ${zones.length}`}
          status={criticalZones.length > 0 ? 'ACTION REQUIRED' : 'NOMINAL'}
          statusColor={criticalZones.length > 0 ? '#F97316' : '#10B981'}
          subtitle={criticalZones.map(z => z.id).join(', ') || 'None'}
          icon={Layers}
          onClick={() => setCurrentTab('mine-map')}
        />

        <KPICard
          title="Live Telemetry"
          value="12 / 12"
          unit="nodes"
          status="100% SIGNAL"
          statusColor="#10B981"
          subtitle="All sensors transmitting"
          icon={Radio}
          onClick={() => setCurrentTab('telemetry')}
        />

        <KPICard
          title="Prediction Status"
          value={currentRisk.confidence}
          unit="conf."
          status={currentRisk.predictionStatus}
          statusColor={currentRisk.currentRisk === 'CRITICAL' ? '#EF4444' : '#38BDF8'}
          subtitle="GNN-XGB Model v2.4"
          icon={Activity}
          onClick={() => setCurrentTab('risk-analysis')}
        />

        <KPICard
          title="Last Sensor Sync"
          value={lastUpdateTime}
          status="LIVE FEED"
          statusColor="#10B981"
          subtitle="Sync rate: 1.0 sec"
          icon={Clock}
        />
      </div>

      {/* Main Core Section: Large Risk Gauge & 24H Risk Trend Area Chart */}
      <div className="grid-two-column">
        {/* Large Current Risk Section */}
        <RiskGauge
          score={currentRisk.riskScore}
          riskLevel={currentRisk.currentRisk}
          confidence={currentRisk.confidence}
          status={currentRisk.predictionStatus}
          hazardType={currentRisk.hazardType}
          timeToCritical={currentRisk.projectedTimeToCritical}
          primaryZone={currentRisk.affectedPrimaryZone}
        />

        {/* 24-Hour Risk Trend Chart */}
        <div className="command-card">
          <RiskTrendChart data={telemetryHistory} height={230} title="24-Hour AI Rockfall Risk Trajectory" />
        </div>
      </div>

      {/* Live Telemetry Real-time Quick Cards */}
      <div>
        <div className="card-header-row">
          <div className="card-title-group">
            <Radio size={16} color="var(--text-accent)" />
            <h3 className="card-title">Live Geotechnical Telemetry Pulse</h3>
            <span style={{ fontSize: '10px', color: '#38BDF8', fontFamily: 'var(--font-mono)' }}>(DEMO DATA)</span>
          </div>
          <button
            onClick={() => setCurrentTab('telemetry')}
            style={{ fontSize: '11px', color: 'var(--text-accent)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}
          >
            <span>Telemetry Deep Dive</span>
            <ArrowRight size={13} />
          </button>
        </div>

        <div className="grid-telemetry-grid">
          <KPICard
            title="Ground Vibration"
            value={liveTelemetry.vibration.value}
            unit="mm/s"
            status={liveTelemetry.vibration.status}
            statusColor={liveTelemetry.vibration.status === 'CRITICAL' ? '#EF4444' : liveTelemetry.vibration.status === 'HIGH' ? '#F97316' : '#10B981'}
            delta={liveTelemetry.vibration.delta}
            trend={liveTelemetry.vibration.trend}
            subtitle="PPV Triaxial Seismograph"
            sparklineData={liveTelemetry.vibration.sparkline}
            sparklineColor="#F97316"
            onClick={() => setCurrentTab('telemetry')}
          />

          <KPICard
            title="Precipitation"
            value={liveTelemetry.rainfall.value}
            unit="mm/h"
            status={liveTelemetry.rainfall.status}
            statusColor={liveTelemetry.rainfall.status === 'CRITICAL' ? '#EF4444' : liveTelemetry.rainfall.status === 'HIGH' ? '#F97316' : '#10B981'}
            delta={liveTelemetry.rainfall.delta}
            trend={liveTelemetry.rainfall.trend}
            subtitle="Optical Rain Gauge"
            sparklineData={liveTelemetry.rainfall.sparkline}
            sparklineColor="#38BDF8"
            onClick={() => setCurrentTab('telemetry')}
          />

          <KPICard
            title="Rock Displacement"
            value={liveTelemetry.displacement.value}
            unit="mm"
            status={liveTelemetry.displacement.status}
            statusColor={liveTelemetry.displacement.status === 'CRITICAL' ? '#EF4444' : liveTelemetry.displacement.status === 'HIGH' ? '#F97316' : '#10B981'}
            delta={liveTelemetry.displacement.delta}
            trend={liveTelemetry.displacement.trend}
            subtitle="Borehole Extensometer"
            sparklineData={liveTelemetry.displacement.sparkline}
            sparklineColor="#EF4444"
            highlight={liveTelemetry.displacement.status === 'CRITICAL'}
            onClick={() => setCurrentTab('telemetry')}
          />

          <KPICard
            title="Pore Water Pressure"
            value={liveTelemetry.porePressure.value}
            unit="kPa"
            status={liveTelemetry.porePressure.status}
            statusColor={liveTelemetry.porePressure.status === 'CRITICAL' ? '#EF4444' : liveTelemetry.porePressure.status === 'HIGH' ? '#F97316' : '#F59E0B'}
            delta={liveTelemetry.porePressure.delta}
            trend={liveTelemetry.porePressure.trend}
            subtitle="Vibrating Piezometer"
            sparklineData={liveTelemetry.porePressure.sparkline}
            sparklineColor="#A855F7"
            onClick={() => setCurrentTab('telemetry')}
          />

          <KPICard
            title="Slope Factor of Safety"
            value={liveTelemetry.slopeStability.value}
            unit="FoS"
            status={liveTelemetry.slopeStability.status}
            statusColor={liveTelemetry.slopeStability.status === 'CRITICAL' ? '#EF4444' : liveTelemetry.slopeStability.status === 'HIGH' ? '#F97316' : '#10B981'}
            delta={liveTelemetry.slopeStability.delta}
            trend={liveTelemetry.slopeStability.trend}
            subtitle="Equilibrium Radar FoS"
            sparklineData={liveTelemetry.slopeStability.sparkline}
            sparklineColor="#10B981"
            highlight={liveTelemetry.slopeStability.status === 'CRITICAL'}
            onClick={() => setCurrentTab('telemetry')}
          />
        </div>
      </div>

      {/* Interactive Mine Map Preview & Active Alerts Grid */}
      <div className="grid-two-column">
        {/* Mine Map Compact Workbench */}
        <div>
          <div className="card-header-row">
            <div className="card-title-group">
              <MapPin size={16} color="#38BDF8" />
              <h3 className="card-title">Mine Map Overview</h3>
            </div>
            <button
              onClick={() => setCurrentTab('mine-map')}
              style={{ fontSize: '11px', color: 'var(--text-accent)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}
            >
              <span>Full Screen GIS</span>
              <ArrowRight size={13} />
            </button>
          </div>
          <MineMap height={380} />
        </div>

        {/* Active Geotechnical Alerts Feed */}
        <div className="command-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-header-row">
            <div className="card-title-group">
              <AlertTriangle size={16} color="#F97316" />
              <h3 className="card-title">Active Alert Stream</h3>
              <span style={{ fontSize: '10px', color: '#EF4444', fontFamily: 'var(--font-mono)' }}>
                ({activeAlerts.length} ACTIVE)
              </span>
            </div>
            <button
              onClick={() => setCurrentTab('alerts')}
              style={{ fontSize: '11px', color: 'var(--text-accent)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}
            >
              <span>Alert Center</span>
              <ArrowRight size={13} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', flex: 1, maxHeight: '340px' }}>
            {activeAlerts.map(alert => (
              <div
                key={alert.id}
                onClick={() => {
                  setSelectedAlert(alert);
                }}
                style={{
                  padding: '12px 14px',
                  backgroundColor: alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.08)' : 'var(--bg-card-subtle)',
                  borderRadius: '6px',
                  border: `1px solid ${alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.35)' : 'var(--border-subtle)'}`,
                  cursor: 'pointer',
                  transition: 'border-color 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <RiskBadge level={alert.severity} size="sm" />
                    <span style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF' }}>{alert.title}</span>
                  </div>
                  <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>{alert.time}</span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-accent)', fontWeight: 600, marginBottom: '4px' }}>
                  {alert.zoneId} — {alert.zoneName}
                </div>
                <p style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {alert.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Mine Zone Status Table */}
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
            <h3 className="card-title">Mine Zone Geotechnical Status Summary</h3>
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
            7 Monitored Sectors
          </span>
        </div>

        <div className="command-table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table className="command-table">
            <thead>
              <tr>
                <th>Zone ID</th>
                <th>Sector Name & Benches</th>
                <th>Elevation</th>
                <th>Slope Angle</th>
                <th>Risk Level</th>
                <th>Status</th>
                <th>Active Sensors</th>
                <th>Last Update</th>
                <th style={{ textAlign: 'right' }}>GIS Inspect</th>
              </tr>
            </thead>
            <tbody>
              {zones.map(z => (
                <tr
                  key={z.id}
                  className="clickable-row"
                  onClick={() => selectZoneById(z.id)}
                >
                  <td style={{ fontWeight: 700, color: 'var(--text-accent)', fontFamily: 'var(--font-mono)' }}>
                    {z.id}
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: '#FFFFFF' }}>{z.name}</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>{z.lithology}</div>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{z.elevation}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>{z.slopeAngle}</td>
                  <td>
                    <RiskBadge level={z.riskLevel} score={z.riskScore} size="sm" />
                  </td>
                  <td>
                    <span style={{
                      fontSize: '11px',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 600,
                      color: z.riskLevel === 'CRITICAL' ? '#EF4444' : z.riskLevel === 'HIGH' ? '#F97316' : '#10B981'
                    }}>
                      {z.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                      {z.sensors.slice(0, 2).map((s, i) => (
                        <span key={i} style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', padding: '1px 5px', borderRadius: '3px', backgroundColor: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                          {s}
                        </span>
                      ))}
                      {z.sensors.length > 2 && (
                        <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-tertiary)' }}>+{z.sensors.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>{z.lastUpdate}</td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        border: '1px solid rgba(56, 189, 248, 0.3)',
                        color: '#38BDF8',
                        fontSize: '11px',
                        fontWeight: 600
                      }}
                    >
                      Map View
                    </button>
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

export default OverviewView;
