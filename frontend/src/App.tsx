import React from 'react';
import { Header } from './components/layout/Header';
import { Footer } from './components/layout/Footer';
import { MainRiskPanel } from './components/risk/MainRiskPanel';
import { RiskContributors } from './components/risk/RiskContributors';
import { RecommendedAction } from './components/risk/RecommendedAction';
import { SensorGrid } from './components/sensors/SensorGrid';
import { DegradedStateBanner } from './components/sensors/DegradedStateBanner';
import { LiveChartsPanel } from './components/charts/LiveChartsPanel';
import { MineZoneView } from './components/map/MineZoneView';
import { AlertCenter } from './components/alerts/AlertCenter';
import { SimulationControls } from './components/controls/SimulationControls';
import { useWebSocket } from './hooks/useWebSocket';
import { useSimulation } from './hooks/useSimulation';
import { useAlerts } from './hooks/useAlerts';

export const App: React.FC = () => {
  // 1. Live WebSocket Telemetry & Risk Stream
  const { connectionState, telemetry, risk, history, lastError } = useWebSocket();

  // 2. REST Simulation Controls & Backend Health Polling
  const {
    status: simStatus,
    loading: simLoading,
    backendOnline,
    startScenario,
    stopSimulation,
  } = useSimulation();

  // 3. Historical & Real-Time Alert Store
  const { alerts, loading: alertsLoading, refreshAlerts } = useAlerts(risk, telemetry);

  const activeScenario = simStatus?.scenario || 'NORMAL';

  return (
    <div className="app-container">
      {/* 1. Command Center Header */}
      <Header
        backendOnline={backendOnline}
        wsState={connectionState}
        simStatus={simStatus}
        activeScenario={activeScenario}
        lastTimestamp={telemetry.timestamp}
      />

      {/* 2. Main Dashboard Content Grid */}
      <main className="dashboard-main">
        {/* Sensor Fault / Degraded Data Warning Banner */}
        <DegradedStateBanner status={risk.status} confidence={risk.confidence} />

        {/* Top Operational Row: Risk Gauge, 6-Sensor Telemetry, Factors & Mitigation */}
        <div className="grid-top-row">
          {/* Main Risk Gauge */}
          <MainRiskPanel risk={risk} telemetry={telemetry} />

          {/* 6 In-Situ Sensor Telemetry Cards */}
          <SensorGrid sensors={telemetry.sensors} status={risk.status} />

          {/* Contributing Factors & Mitigation Recommendation */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <RecommendedAction risk={risk} />
            <RiskContributors factors={risk.factors} />
          </div>
        </div>

        {/* Middle Operational Row: 5 Rolling Time-Series Telemetry Charts */}
        <div style={{ width: '100%' }}>
          <LiveChartsPanel history={history} />
        </div>

        {/* Lower Row: Mine Zone Schematic & Geotechnical Alert Center */}
        <div className="grid-bottom-row">
          {/* Schematic Mine Map & Monitored Zone */}
          <MineZoneView risk={risk} telemetry={telemetry} />

          {/* Geotechnical Safety Alert Center */}
          <AlertCenter alerts={alerts} loading={alertsLoading} onRefresh={refreshAlerts} />
        </div>

        {/* Bottom Operational Row: Physics Simulation Control Panel */}
        <div style={{ width: '100%' }}>
          <SimulationControls
            status={simStatus}
            loading={simLoading}
            onStart={startScenario}
            onStop={stopSimulation}
          />
        </div>
      </main>

      {/* 3. Command Center Footer & Model Disclosure */}
      <Footer />
    </div>
  );
};

export default App;
