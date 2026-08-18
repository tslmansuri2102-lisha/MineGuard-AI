import React, { useState } from 'react';
import {
  Map,
  Layers,
  Search,
  Filter,
  Radio,
  AlertTriangle,
  Info,
  Navigation,
  Compass
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import MineMap from '../components/map/MineMap';
import { RiskBadge } from '../components/common/StatusBadge';

export function MineMapView() {
  const { zones, selectZoneById, selectedZone } = useMineGuard();
  const [search, setSearch] = useState('');

  const filteredZones = search.trim()
    ? zones.filter(z => z.id.toLowerCase().includes(search.toLowerCase()) || z.name.toLowerCase().includes(search.toLowerCase()) || z.sector.toLowerCase().includes(search.toLowerCase()))
    : zones;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Controls Ribbon */}
      <div style={{
        padding: '14px 18px',
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
          <div style={{ padding: '6px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>
            <Compass size={18} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                Open-Pit Mine Topographic GIS Workbench
              </h2>
              <span style={{
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                color: '#38BDF8',
                backgroundColor: 'rgba(56, 189, 248, 0.12)',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                DEMO MINE MAP
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Vector topographic projection of Kadapa Open-Pit Mine Sector 4. Coordinates & contours are simulated for demonstration.
            </p>
          </div>
        </div>

        {/* Search / Zone Jump */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px',
          width: 'min(300px, 100%)'
        }}>
          <Search size={14} color="var(--text-tertiary)" />
          <input
            type="text"
            placeholder="Search pit zone (e.g. Zone A-03)..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: '12px',
              color: '#FFFFFF',
              width: '100%'
            }}
          />
        </div>
      </div>

      {/* Main Interactive Map Viewport */}
      <MineMap height={560} />

      {/* Zone Quick-Selection Cards Bar */}
      <div>
        <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-tertiary)', textTransform: 'uppercase', marginBottom: '10px', letterSpacing: '0.6px', fontFamily: 'var(--font-heading)' }}>
          SECTOR ZONE SELECTOR ({filteredZones.length} ZONES)
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          {filteredZones.map(zone => {
            const isSelected = selectedZone?.id === zone.id;
            return (
              <div
                key={zone.id}
                onClick={() => selectZoneById(zone.id)}
                className={`command-card ${zone.riskLevel === 'CRITICAL' ? 'hazard-highlight' : ''}`}
                style={{
                  cursor: 'pointer',
                  borderColor: isSelected ? 'var(--text-accent)' : undefined,
                  backgroundColor: isSelected ? 'var(--bg-card-hover)' : undefined
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '12px', color: 'var(--text-accent)' }}>
                    {zone.id}
                  </span>
                  <RiskBadge level={zone.riskLevel} score={zone.riskScore} size="sm" />
                </div>

                <div style={{ fontWeight: 600, fontSize: '12px', color: '#FFFFFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {zone.name}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '8px', fontFamily: 'var(--font-mono)' }}>
                  <span>{zone.benchLevels}</span>
                  <span>{zone.elevation}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default MineMapView;
