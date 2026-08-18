import React from 'react';
import { MineGuardProvider, useMineGuard } from './context/MineGuardContext';
import Sidebar from './components/layout/Sidebar';
import Topbar from './components/layout/Topbar';
import FooterDisclaimer from './components/layout/FooterDisclaimer';
import DemoBanner from './components/common/DemoBanner';

// Views
import OverviewView from './views/OverviewView';
import LiveMonitoringView from './views/LiveMonitoringView';
import RiskAnalysisView from './views/RiskAnalysisView';
import MineMapView from './views/MineMapView';
import AlertCenterView from './views/AlertCenterView';
import TelemetryView from './views/TelemetryView';
import PredictionHistoryView from './views/PredictionHistoryView';
import SystemStatusView from './views/SystemStatusView';
import SettingsView from './views/SettingsView';

function AppContent() {
  const { currentTab } = useMineGuard();

  const renderActiveView = () => {
    switch (currentTab) {
      case 'overview':
        return <OverviewView />;
      case 'monitoring':
        return <LiveMonitoringView />;
      case 'risk-analysis':
        return <RiskAnalysisView />;
      case 'mine-map':
        return <MineMapView />;
      case 'alerts':
        return <AlertCenterView />;
      case 'telemetry':
        return <TelemetryView />;
      case 'predictions':
        return <PredictionHistoryView />;
      case 'system-status':
        return <SystemStatusView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <OverviewView />;
    }
  };

  return (
    <div className="app-container">
      {/* Fixed Left Industrial Navigation Sidebar */}
      <Sidebar />

      {/* Main Command Workspace */}
      <div className="main-content-wrapper">
        {/* Topbar with site status and alarm notifications */}
        <Topbar />

        {/* Demo Mode Notice & Simulation Controls */}
        <DemoBanner />

        {/* Dynamic Active View Content Area */}
        <main className="view-content-area">
          {renderActiveView()}
        </main>

        {/* Unobtrusive Safety Disclaimer Footer */}
        <FooterDisclaimer />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <MineGuardProvider>
      <AppContent />
    </MineGuardProvider>
  );
}
