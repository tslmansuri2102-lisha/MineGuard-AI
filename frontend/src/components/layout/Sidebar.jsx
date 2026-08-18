import React, { useState } from 'react';
import {
  LayoutDashboard,
  Activity,
  BrainCircuit,
  Map,
  Bell,
  Gauge,
  History,
  Server,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  Zap,
  HardHat
} from 'lucide-react';
import { useMineGuard } from '../../context/MineGuardContext';

export function Sidebar() {
  const { currentTab, setCurrentTab, alerts } = useMineGuard();
  const [collapsed, setCollapsed] = useState(false);

  const activeAlertsCount = alerts.filter(a => a.status === 'ACTIVE').length;
  const criticalCount = alerts.filter(a => a.severity === 'CRITICAL' && a.status === 'ACTIVE').length;

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, section: 'COMMAND' },
    { id: 'monitoring', label: 'Live Monitoring', icon: Activity, section: 'COMMAND' },
    { id: 'risk-analysis', label: 'Risk Analysis', icon: BrainCircuit, section: 'AI ENGINE' },
    { id: 'mine-map', label: 'Mine Map', icon: Map, section: 'AI ENGINE' },
    { id: 'alerts', label: 'Alert Center', icon: Bell, badge: activeAlertsCount, badgeType: criticalCount > 0 ? 'critical' : 'normal', section: 'EARLY WARNING' },
    { id: 'telemetry', label: 'Telemetry', icon: Gauge, section: 'EARLY WARNING' },
    { id: 'predictions', label: 'Prediction History', icon: History, section: 'INTELLIGENCE' },
    { id: 'system-status', label: 'System Status', icon: Server, section: 'INTELLIGENCE' },
    { id: 'settings', label: 'Settings', icon: Settings, section: 'CONFIG' }
  ];

  let lastSection = '';

  return (
    <aside className={`command-sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Sidebar Header & Brand Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo-group">
          <div className="sidebar-logo-icon">
            <Shield size={20} strokeWidth={2.4} />
          </div>
          {!collapsed && (
            <div className="sidebar-brand-text">
              <span className="sidebar-brand-title">MINEGUARD AI</span>
              <span className="sidebar-brand-tagline">SIH 2026 PROTOTYPE</span>
            </div>
          )}
        </div>

        <button
          className="sidebar-collapse-btn"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Navigation List */}
      <nav className="sidebar-nav">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          const showSectionLabel = !collapsed && item.section !== lastSection;
          if (showSectionLabel) lastSection = item.section;

          return (
            <React.Fragment key={item.id}>
              {showSectionLabel && (
                <div className="nav-section-label">
                  {item.section}
                </div>
              )}

              <button
                className={`nav-item-btn ${isActive ? 'active' : ''}`}
                onClick={() => setCurrentTab(item.id)}
                title={collapsed ? item.label : undefined}
              >
                <Icon size={18} className="nav-item-icon" />
                {!collapsed && <span>{item.label}</span>}

                {!collapsed && item.badge > 0 && (
                  <span className={`nav-badge-pill ${item.badgeType === 'critical' ? 'critical' : ''}`}>
                    {item.badge}
                  </span>
                )}
              </button>
            </React.Fragment>
          );
        })}
      </nav>

      {/* Footer Geotechnical Operator info */}
      {!collapsed && (
        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: 'rgba(56, 189, 248, 0.15)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#38BDF8'
            }}>
              <HardHat size={16} />
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#FFFFFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                Geotech Command
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
                Shift #01 (Active)
              </div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;
