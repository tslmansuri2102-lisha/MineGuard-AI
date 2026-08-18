import React from 'react';
import { Zap, Play, ShieldAlert, CloudRain, Activity, CheckCircle, ArrowRight } from 'lucide-react';
import { useMineGuard } from '../../context/MineGuardContext';

export function ScenarioRunner() {
  const { activeScenario, applyScenario, setCurrentTab, setSelectedZone, zones } = useMineGuard();

  const scenarios = [
    {
      id: 'normal',
      name: '1. Normal Baseline',
      desc: 'Stable slopes, baseline vibrations (1.8 mm/s), low risk (18%)',
      icon: CheckCircle,
      color: '#10B981'
    },
    {
      id: 'storm',
      name: '2. Monsoon Storm',
      desc: 'Rainfall surge (38mm/h), pore water rise, warning alert',
      icon: CloudRain,
      color: '#F59E0B'
    },
    {
      id: 'microseismic',
      name: '3. Micro-Seismic Pulse',
      desc: 'Subsurface geophone tremor (16.5 mm/s), creep on Bench 3',
      icon: Activity,
      color: '#F97316'
    },
    {
      id: 'rockfall_hazard',
      name: '4. Critical Rockfall Hazard',
      desc: 'Planar shear strain spike in Zone A-03 (88% Critical), siren trigger',
      icon: ShieldAlert,
      color: '#EF4444'
    }
  ];

  return (
    <div className="scenario-runner-card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '6px',
          backgroundColor: 'rgba(245, 158, 11, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#F59E0B',
          flexShrink: 0
        }}>
          <Zap size={18} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontFamily: 'var(--font-heading)', fontWeight: 700, fontSize: '13px', color: '#FFFFFF', letterSpacing: '0.3px' }}>
              SIH 2026 DEMO SCENARIO CONTROLLER
            </span>
            <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
              Interactive Sandbox
            </span>
          </div>
          <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Trigger live geotechnical hazard events to demonstrate system reaction across Telemetry, AI Risk, Alerts, and Mine Map.
          </p>
        </div>
      </div>

      <div className="scenario-pills-group">
        {scenarios.map(sc => {
          const Icon = sc.icon;
          const isActive = activeScenario === sc.id;
          return (
            <button
              key={sc.id}
              onClick={() => applyScenario(sc.id)}
              className={`scenario-pill-btn ${isActive ? 'active' : ''}`}
              title={sc.desc}
              style={{
                borderColor: isActive ? sc.color : 'var(--border-subtle)',
                backgroundColor: isActive ? sc.color : 'var(--bg-card)',
                color: isActive ? '#090D14' : 'var(--text-primary)'
              }}
            >
              <Icon size={13} />
              <span>{sc.name}</span>
            </button>
          );
        })}

        {/* Quick Shortcut to Map or Alerts during critical scenario */}
        {activeScenario === 'rockfall_hazard' && (
          <button
            onClick={() => {
              const zoneA3 = zones.find(z => z.id === 'Zone A-03');
              if (zoneA3) setSelectedZone(zoneA3);
              setCurrentTab('mine-map');
            }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '11px',
              fontWeight: 700,
              backgroundColor: 'rgba(239, 68, 68, 0.2)',
              color: '#EF4444',
              border: '1px solid rgba(239, 68, 68, 0.5)',
              cursor: 'pointer'
            }}
          >
            <span>Inspect Zone A-03 on Map</span>
            <ArrowRight size={13} />
          </button>
        )}
      </div>
    </div>
  );
}

export default ScenarioRunner;
