import React, { useState } from 'react';
import {
  Settings,
  Palette,
  Bell,
  Sliders,
  Database,
  Shield,
  Layers,
  Radio,
  CheckCircle2,
  AlertCircle,
  Save,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import { apiService } from '../services/api';

export function SettingsView() {
  const {
    settings,
    setSettings,
    isDemoMode,
    setIsDemoMode,
    activeScenario,
    applyScenario
  } = useMineGuard();

  const [apiUrl, setApiUrl] = useState(settings.apiBaseUrl);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionResult, setConnectionResult] = useState(null);
  const [savedNotice, setSavedNotice] = useState(false);

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setConnectionResult(null);
    const res = await apiService.testConnection(apiUrl);
    setTestingConnection(false);
    setConnectionResult(res);
  };

  const handleSaveSettings = () => {
    setSettings(prev => ({
      ...prev,
      apiBaseUrl: apiUrl
    }));
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 3000);
  };

  const handleThemeChange = (themeName) => {
    setSettings(prev => ({ ...prev, theme: themeName }));
    document.body.classList.remove('theme-midnight', 'theme-tactical');
    if (themeName === 'midnight') document.body.classList.add('theme-midnight');
    if (themeName === 'tactical') document.body.classList.add('theme-tactical');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Header */}
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
            <Settings size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                Command Center Configuration & Geotechnical Parameters
              </h2>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Configure telemetry sampling rates, geotechnical alert thresholds, theme styling, and future API connectivity.
            </p>
          </div>
        </div>

        <button
          onClick={handleSaveSettings}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            backgroundColor: savedNotice ? '#10B981' : '#F59E0B',
            color: '#090D14',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 700,
            transition: 'all 0.2s ease'
          }}
        >
          {savedNotice ? <CheckCircle2 size={15} /> : <Save size={15} />}
          <span>{savedNotice ? 'Preferences Saved' : 'Save Preferences'}</span>
        </button>
      </div>

      {/* Grid of Settings Sections */}
      <div className="grid-two-column">
        {/* Section 1: Command Theme & Display Settings */}
        <div className="command-card">
          <div className="card-header-row">
            <div className="card-title-group">
              <Palette size={16} color="var(--text-accent)" />
              <h3 className="card-title">Theme & Interface Display</h3>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                Color Theme Profile
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                {[
                  { id: 'graphite', label: 'Dark Graphite', desc: 'Standard (#0B0F17)' },
                  { id: 'midnight', label: 'True Midnight', desc: 'Deep (#030712)' },
                  { id: 'tactical', label: 'Tactical Obsidian', desc: 'High Contrast (#0D1117)' }
                ].map(t => (
                  <button
                    key={t.id}
                    onClick={() => handleThemeChange(t.id)}
                    style={{
                      padding: '10px',
                      borderRadius: '6px',
                      backgroundColor: settings.theme === t.id ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-card-subtle)',
                      border: `1px solid ${settings.theme === t.id ? '#38BDF8' : 'var(--border-subtle)'}`,
                      color: settings.theme === t.id ? '#FFFFFF' : 'var(--text-secondary)',
                      textAlign: 'left'
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: '12px' }}>{t.label}</div>
                    <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '2px' }}>{t.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <div style={{ paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
              <label style={{ fontSize: '12px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '10px' }}>
                GIS Map Overlay Layers
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '13px', color: '#FFFFFF', cursor: 'pointer' }}>
                  <span>Render InSAR Radar Displacement Heatmap</span>
                  <input
                    type="checkbox"
                    checked={settings.showHeatmap}
                    onChange={e => setSettings(prev => ({ ...prev, showHeatmap: e.target.checked }))}
                    style={{ width: '16px', height: '16px', accentColor: '#38BDF8' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '13px', color: '#FFFFFF', cursor: 'pointer' }}>
                  <span>Display Geotechnical Sensor Nodes On Map</span>
                  <input
                    type="checkbox"
                    checked={settings.showSensorsOnMap}
                    onChange={e => setSettings(prev => ({ ...prev, showSensorsOnMap: e.target.checked }))}
                    style={{ width: '16px', height: '16px', accentColor: '#38BDF8' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '13px', color: '#FFFFFF', cursor: 'pointer' }}>
                  <span>Highlight Haul Road Transit Corridors</span>
                  <input
                    type="checkbox"
                    checked={settings.showHaulRoads}
                    onChange={e => setSettings(prev => ({ ...prev, showHaulRoads: e.target.checked }))}
                    style={{ width: '16px', height: '16px', accentColor: '#38BDF8' }}
                  />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Demo Mode & Simulation Controls */}
        <div className="command-card">
          <div className="card-header-row">
            <div className="card-title-group">
              <Sliders size={16} color="#F59E0B" />
              <h3 className="card-title">Demo Mode & Telemetry Frequency</h3>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: '13px', color: '#FFFFFF' }}>Demo Mode Simulation Engine</div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Runs high-frequency virtual sensor fluctuations and scenario anomalies in browser.
                </div>
              </div>
              <input
                type="checkbox"
                checked={isDemoMode}
                onChange={e => setIsDemoMode(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: '#F59E0B' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                Virtual Telemetry Update Frequency
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                {[
                  { label: 'Fast (1.0s)', val: 1000 },
                  { label: 'Normal (2.0s)', val: 2000 },
                  { label: 'Power Save (5.0s)', val: 5000 }
                ].map(item => (
                  <button
                    key={item.val}
                    onClick={() => setSettings(prev => ({ ...prev, refreshRate: item.val }))}
                    style={{
                      padding: '8px',
                      borderRadius: '6px',
                      backgroundColor: settings.refreshRate === item.val ? 'rgba(245, 158, 11, 0.15)' : 'var(--bg-card-subtle)',
                      border: `1px solid ${settings.refreshRate === item.val ? '#F59E0B' : 'var(--border-subtle)'}`,
                      color: settings.refreshRate === item.val ? '#F59E0B' : 'var(--text-secondary)',
                      fontSize: '12px',
                      fontWeight: 600
                    }}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ fontSize: '12px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                Active Scenario Preset
              </label>
              <select
                value={activeScenario}
                onChange={e => applyScenario(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: 'var(--bg-card-subtle)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  fontSize: '12px',
                  outline: 'none'
                }}
              >
                <option value="normal">1. Normal Baseline (Stable Slopes, Low Risk 18%)</option>
                <option value="storm">2. Monsoon Storm (Heavy Inflow, Warning Alert 52%)</option>
                <option value="microseismic">3. Micro-Seismic Pulse (High PPV Surge, Risk 72%)</option>
                <option value="rockfall_hazard">4. Critical Rockfall Hazard (East Highwall 88%, Siren Trigger)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Geotechnical Threshold Settings */}
      <div className="command-card">
        <div className="card-header-row">
          <div className="card-title-group">
            <Shield size={16} color="var(--risk-critical)" />
            <h3 className="card-title">Geotechnical Safety Warning Threshold Calibration</h3>
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
            SIH 2026 Standards
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '12px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
            <label style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Vibration Alert Limit (PPV)
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
              <input
                type="number"
                value={settings.vibrationThreshold}
                onChange={e => setSettings(prev => ({ ...prev, vibrationThreshold: parseFloat(e.target.value) || 8 }))}
                style={{ width: '80px', padding: '6px 8px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: '#FFFFFF', fontFamily: 'var(--font-mono)' }}
              />
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>mm/s</span>
            </div>
          </div>

          <div style={{ padding: '12px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
            <label style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Rainfall Inflow Alert Limit
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
              <input
                type="number"
                value={settings.rainfallThreshold}
                onChange={e => setSettings(prev => ({ ...prev, rainfallThreshold: parseFloat(e.target.value) || 20 }))}
                style={{ width: '80px', padding: '6px 8px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: '#FFFFFF', fontFamily: 'var(--font-mono)' }}
              />
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>mm/h</span>
            </div>
          </div>

          <div style={{ padding: '12px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
            <label style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Extensometer Displacement Limit
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
              <input
                type="number"
                value={settings.displacementThreshold}
                onChange={e => setSettings(prev => ({ ...prev, displacementThreshold: parseFloat(e.target.value) || 3.5 }))}
                style={{ width: '80px', padding: '6px 8px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: '#FFFFFF', fontFamily: 'var(--font-mono)' }}
              />
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>mm</span>
            </div>
          </div>

          <div style={{ padding: '12px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
            <label style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Pore Water Pressure Limit
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
              <input
                type="number"
                value={settings.porePressureThreshold}
                onChange={e => setSettings(prev => ({ ...prev, porePressureThreshold: parseFloat(e.target.value) || 160 }))}
                style={{ width: '80px', padding: '6px 8px', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '4px', color: '#FFFFFF', fontFamily: 'var(--font-mono)' }}
              />
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>kPa</span>
            </div>
          </div>
        </div>
      </div>

      {/* API Endpoint & Integration Layer */}
      <div className="command-card">
        <div className="card-header-row">
          <div className="card-title-group">
            <Database size={16} color="#38BDF8" />
            <h3 className="card-title">Backend API Service Integration</h3>
          </div>
          <span style={{ fontSize: '10px', color: '#38BDF8', fontFamily: 'var(--font-mono)' }}>
            VITE_API_BASE_URL READY
          </span>
        </div>

        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '14px', lineHeight: 1.5 }}>
          When copying this frontend into the full MineGuard-AI repository, configure the backend REST API & WebSocket endpoint below or in <code>.env</code>. The application automatically falls back to client mock data when offline.
        </p>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={apiUrl}
            onChange={e => setApiUrl(e.target.value)}
            placeholder="http://localhost:8000/api/v1"
            style={{
              flex: 1,
              minWidth: '260px',
              padding: '8px 12px',
              backgroundColor: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              color: '#FFFFFF',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px'
            }}
          />

          <button
            onClick={handleTestConnection}
            disabled={testingConnection}
            className="topbar-btn"
            style={{ padding: '8px 16px', fontWeight: 600 }}
          >
            {testingConnection ? <RefreshCw size={14} className="spin-animate" /> : <Radio size={14} />}
            <span>{testingConnection ? 'Testing...' : 'Test Backend Connection'}</span>
          </button>
        </div>

        {connectionResult && (
          <div style={{
            marginTop: '12px',
            padding: '10px 14px',
            borderRadius: '6px',
            backgroundColor: connectionResult.success ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
            border: `1px solid ${connectionResult.success ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px'
          }}>
            {connectionResult.success ? (
              <>
                <CheckCircle2 size={16} color="#10B981" />
                <span style={{ color: '#10B981' }}>Connected successfully to live MineGuard AI backend at <code>{connectionResult.url}</code></span>
              </>
            ) : (
              <>
                <AlertCircle size={16} color="#F59E0B" />
                <span style={{ color: '#F59E0B' }}>
                  No backend response at <code>{connectionResult.url}</code>. Operating smoothly in <strong>Standalone Client Demo Mode</strong>.
                </span>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SettingsView;
