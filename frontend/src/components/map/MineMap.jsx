import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, Layers, Eye, EyeOff, Radio, AlertOctagon, ShieldAlert, Navigation } from 'lucide-react';
import { useMineGuard } from '../../context/MineGuardContext';
import MineLegend from './MineLegend';
import ZoneDetailDrawer from './ZoneDetailDrawer';

export function MineMap({ height = 540, fullScreen = false }) {
  const { zones, selectedZone, setSelectedZone, sensors, alerts } = useMineGuard();

  // Map Controls State
  const [zoomLevel, setZoomLevel] = useState(1);
  const [hoveredZoneId, setHoveredZoneId] = useState(null);
  const [hoveredSensor, setHoveredSensor] = useState(null);
  const [filterQuery, setFilterQuery] = useState('');

  // Layer Toggles
  const [showBenches, setShowBenches] = useState(true);
  const [showSensors, setShowSensors] = useState(true);
  const [showHaulRoads, setShowHaulRoads] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);

  const getRiskColor = (level) => {
    switch (level) {
      case 'CRITICAL': return '#EF4444';
      case 'HIGH': return '#F97316';
      case 'MODERATE': return '#F59E0B';
      default: return '#10B981';
    }
  };

  // Sensor node coordinates across pit
  const sensorCoords = {
    'DISP-E01': { x: 710, y: 280, name: 'DISP-E01' },
    'VIB-E04': { x: 670, y: 350, name: 'VIB-E04' },
    'PIEZ-E02': { x: 620, y: 270, name: 'PIEZ-E02' },
    'RADAR-01': { x: 760, y: 230, name: 'RADAR-01' },
    'VIB-SW01': { x: 190, y: 270, name: 'VIB-SW01' },
    'DISP-SW03': { x: 250, y: 220, name: 'DISP-SW03' },
    'RAIN-01': { x: 260, y: 120, name: 'RAIN-01' },
    'INCL-02': { x: 210, y: 320, name: 'INCL-02' }
  };

  const filteredZones = filterQuery 
    ? zones.filter(z => z.id.toLowerCase().includes(filterQuery.toLowerCase()) || z.name.toLowerCase().includes(filterQuery.toLowerCase()))
    : zones;

  return (
    <div className="command-card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', height: fullScreen ? 'calc(100vh - 160px)' : `${height}px` }}>
      {/* Top Map Control Bar */}
      <div style={{
        padding: '12px 18px',
        backgroundColor: 'var(--bg-topbar)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        zIndex: 10
      }}>
        {/* Left: Title & Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Navigation size={16} color="#38BDF8" />
            <span style={{ fontFamily: 'var(--font-heading)', fontSize: '13px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
              Open-Pit Geotechnical GIS Map
            </span>
          </div>

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

        {/* Center: Layer Toggles */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              backgroundColor: showHeatmap ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-card)',
              color: showHeatmap ? '#EF4444' : 'var(--text-tertiary)',
              border: `1px solid ${showHeatmap ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-subtle)'}`
            }}
          >
            <Layers size={12} />
            <span>Radar Heatmap</span>
          </button>

          <button
            onClick={() => setShowSensors(!showSensors)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              backgroundColor: showSensors ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-card)',
              color: showSensors ? '#38BDF8' : 'var(--text-tertiary)',
              border: `1px solid ${showSensors ? 'rgba(56, 189, 248, 0.3)' : 'var(--border-subtle)'}`
            }}
          >
            <Radio size={12} />
            <span>Sensors ({sensors.length})</span>
          </button>

          <button
            onClick={() => setShowHaulRoads(!showHaulRoads)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              backgroundColor: showHaulRoads ? 'rgba(245, 158, 11, 0.15)' : 'var(--bg-card)',
              color: showHaulRoads ? '#F59E0B' : 'var(--text-tertiary)',
              border: `1px solid ${showHaulRoads ? 'rgba(245, 158, 11, 0.3)' : 'var(--border-subtle)'}`
            }}
          >
            <span>Haul Roads</span>
          </button>
        </div>

        {/* Right: Zoom & Reset Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => setZoomLevel(prev => Math.min(1.6, prev + 0.15))}
            className="topbar-btn"
            style={{ padding: '4px 8px' }}
            title="Zoom In"
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={() => setZoomLevel(prev => Math.max(0.8, prev - 0.15))}
            className="topbar-btn"
            style={{ padding: '4px 8px' }}
            title="Zoom Out"
          >
            <ZoomOut size={14} />
          </button>
          <button
            onClick={() => setZoomLevel(1)}
            className="topbar-btn"
            style={{ padding: '4px 8px' }}
            title="Reset Zoom"
          >
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {/* Main SVG Vector Canvas Viewport */}
      <div style={{
        flex: 1,
        position: 'relative',
        backgroundColor: '#070B12',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {/* Subtle grid pattern background */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'radial-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
          opacity: 0.6
        }} />

        <div style={{
          transform: `scale(${zoomLevel})`,
          transformOrigin: 'center center',
          transition: 'transform 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
          width: '100%',
          maxWidth: '920px',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative'
        }}>
          <svg
            viewBox="0 0 900 520"
            style={{ width: '100%', height: '100%', maxHeight: '520px', overflow: 'visible' }}
          >
            <defs>
              {/* Bench terrain textures */}
              <radialGradient id="pitDepthGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#0B1324" />
                <stop offset="50%" stopColor="#10182E" />
                <stop offset="85%" stopColor="#18233C" />
                <stop offset="100%" stopColor="#0D1525" />
              </radialGradient>

              {/* Hazard Radar Heatmap Glow */}
              <radialGradient id="hazardHeatmapE03" cx="70%" cy="50%" r="35%">
                <stop offset="0%" stopColor="#EF4444" stopOpacity="0.55" />
                <stop offset="50%" stopColor="#F97316" stopOpacity="0.30" />
                <stop offset="80%" stopColor="#F59E0B" stopOpacity="0.10" />
                <stop offset="100%" stopColor="transparent" stopOpacity="0" />
              </radialGradient>

              <radialGradient id="hazardHeatmapB02" cx="25%" cy="55%" r="30%">
                <stop offset="0%" stopColor="#F97316" stopOpacity="0.45" />
                <stop offset="60%" stopColor="#F59E0B" stopOpacity="0.20" />
                <stop offset="100%" stopColor="transparent" stopOpacity="0" />
              </radialGradient>

              {/* Drop Shadow for labels */}
              <filter id="labelGlow">
                <feDropShadow dx="0" dy="1" stdDeviation="2" floodColor="#000000" floodOpacity="0.9" />
              </filter>
            </defs>

            {/* Base Pit Bowl Geometry */}
            <path
              d="M 80,60 Q 450,20 820,70 Q 860,260 810,460 Q 450,510 90,460 Q 40,260 80,60 Z"
              fill="url(#pitDepthGradient)"
              stroke="rgba(255, 255, 255, 0.15)"
              strokeWidth="2"
            />

            {/* Concentric Bench Contours (Levels 1 to 7) */}
            {showBenches && (
              <g stroke="rgba(255, 255, 255, 0.08)" strokeWidth="1.2" fill="none">
                {/* Bench Level 1 */}
                <path d="M 110,85 Q 450,45 790,95 Q 820,260 780,435 Q 450,480 120,435 Q 75,260 110,85 Z" />
                {/* Bench Level 2 */}
                <path d="M 150,115 Q 450,80 750,125 Q 780,260 740,405 Q 450,445 160,405 Q 115,260 150,115 Z" />
                {/* Bench Level 3 */}
                <path d="M 200,150 Q 450,115 700,160 Q 730,260 690,370 Q 450,410 210,370 Q 160,260 200,150 Z" strokeDasharray="3 3" />
                {/* Bench Level 4 */}
                <path d="M 250,190 Q 450,155 650,195 Q 680,260 640,335 Q 450,370 260,335 Q 210,260 250,190 Z" />
                {/* Bench Level 5 */}
                <path d="M 300,230 Q 450,200 600,235 Q 620,260 590,300 Q 450,330 310,300 Q 270,260 300,230 Z" strokeDasharray="2 2" />
                {/* Pit Floor L7 */}
                <ellipse cx="440" cy="270" rx="90" ry="40" stroke="rgba(56, 189, 248, 0.25)" strokeWidth="1.5" />
              </g>
            )}

            {/* Radar Heatmap Overlay */}
            {showHeatmap && (
              <g pointerEvents="none">
                <circle cx="680" cy="280" r="140" fill="url(#hazardHeatmapE03)" />
                <circle cx="210" cy="280" r="110" fill="url(#hazardHeatmapB02)" />
              </g>
            )}

            {/* Switchback Haul Roads */}
            {showHaulRoads && (
              <g stroke="#F59E0B" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.85">
                {/* Surface entrance down to Bench 3 */}
                <path d="M 120,70 L 380,90 L 640,115 L 760,180 L 580,220 L 340,250 L 220,290 L 320,340 L 460,300" strokeDasharray="6 3" />
                {/* Road label */}
                <text x="390" y="82" fill="#F59E0B" fontSize="9" fontFamily="var(--font-mono)" fontWeight="700" filter="url(#labelGlow)">
                  HAUL ROAD 1 (MAIN ACCESS)
                </text>
                <text x="230" y="305" fill="#F59E0B" fontSize="9" fontFamily="var(--font-mono)" fontWeight="700" filter="url(#labelGlow)">
                  SWITCHBACK 2
                </text>
              </g>
            )}

            {/* Interactive Mine Zone Polygons */}
            <g>
              {filteredZones.map(zone => {
                const isSelected = selectedZone?.id === zone.id;
                const isHovered = hoveredZoneId === zone.id;
                const riskCol = getRiskColor(zone.riskLevel);

                return (
                  <g
                    key={zone.id}
                    onClick={() => setSelectedZone(zone)}
                    onMouseEnter={() => setHoveredZoneId(zone.id)}
                    onMouseLeave={() => setHoveredZoneId(null)}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Zone Boundary polygon */}
                    <path
                      d={zone.path}
                      fill={riskCol}
                      fillOpacity={isSelected ? 0.45 : isHovered ? 0.35 : 0.18}
                      stroke={riskCol}
                      strokeWidth={isSelected ? 3 : isHovered ? 2.5 : 1.5}
                      strokeDasharray={zone.riskLevel === 'CRITICAL' ? '4 2' : 'none'}
                      style={{ transition: 'all 0.2s ease' }}
                    />

                    {/* Zone ID and Risk Tag Pill */}
                    <g transform={`translate(${zone.coordinates.x + zone.coordinates.width / 2}, ${zone.coordinates.y + zone.coordinates.height / 2})`}>
                      <rect
                        x="-44"
                        y="-14"
                        width="88"
                        height="28"
                        rx="4"
                        fill="#090D14"
                        fillOpacity="0.88"
                        stroke={riskCol}
                        strokeWidth={isSelected ? 2 : 1}
                        filter="url(#labelGlow)"
                      />
                      <text
                        x="0"
                        y="-2"
                        fill="#FFFFFF"
                        fontSize="10"
                        fontWeight="700"
                        fontFamily="var(--font-mono)"
                        textAnchor="middle"
                      >
                        {zone.id}
                      </text>
                      <text
                        x="0"
                        y="9"
                        fill={riskCol}
                        fontSize="9"
                        fontWeight="700"
                        fontFamily="var(--font-heading)"
                        textAnchor="middle"
                      >
                        {zone.riskLevel} ({zone.riskScore}%)
                      </text>
                    </g>
                  </g>
                );
              })}
            </g>

            {/* Critical Hazard Animated Beacons */}
            <g pointerEvents="none">
              {/* Zone A-03 Beacon */}
              <circle cx="680" cy="270" r="8" fill="#EF4444">
                <animate attributeName="r" values="6;22;6" dur="2s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.9;0.1;0.9" dur="2s" repeatCount="indefinite" />
              </circle>
              <circle cx="680" cy="270" r="5" fill="#EF4444" stroke="#FFFFFF" strokeWidth="1.5" />

              {/* Zone B-02 Beacon */}
              <circle cx="210" cy="280" r="7" fill="#F97316">
                <animate attributeName="r" values="5;18;5" dur="2.4s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.8;0.1;0.8" dur="2.4s" repeatCount="indefinite" />
              </circle>
              <circle cx="210" cy="280" r="4" fill="#F97316" stroke="#FFFFFF" strokeWidth="1" />
            </g>

            {/* Geotechnical Sensor Markers */}
            {showSensors && (
              <g>
                {sensors.map(s => {
                  const coord = sensorCoords[s.id];
                  if (!coord) return null;
                  const isHovered = hoveredSensor?.id === s.id;
                  const isCritical = s.status === 'CRITICAL_ALERT';

                  return (
                    <g
                      key={s.id}
                      transform={`translate(${coord.x}, ${coord.y})`}
                      onMouseEnter={() => setHoveredSensor(s)}
                      onMouseLeave={() => setHoveredSensor(null)}
                      style={{ cursor: 'pointer' }}
                    >
                      <circle
                        r={isHovered ? 6 : 4}
                        fill={isCritical ? '#EF4444' : '#38BDF8'}
                        stroke="#090D14"
                        strokeWidth="1.5"
                      />
                      {/* Sensor mini label */}
                      <text
                        x="7"
                        y="3"
                        fill={isCritical ? '#EF4444' : '#38BDF8'}
                        fontSize="8"
                        fontFamily="var(--font-mono)"
                        fontWeight="700"
                        filter="url(#labelGlow)"
                      >
                        {s.id}
                      </text>
                    </g>
                  );
                })}
              </g>
            )}
          </svg>

          {/* Sensor Hover Tooltip Card */}
          {hoveredSensor && (
            <div style={{
              position: 'absolute',
              bottom: '20px',
              left: '20px',
              padding: '10px 14px',
              backgroundColor: '#0F172A',
              border: '1px solid var(--border-medium)',
              borderRadius: '6px',
              boxShadow: 'var(--shadow-lg)',
              zIndex: 25,
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              pointerEvents: 'none'
            }}>
              <div style={{ color: '#38BDF8', fontWeight: 700 }}>{hoveredSensor.id} — {hoveredSensor.type}</div>
              <div style={{ color: '#FFFFFF', marginTop: '2px' }}>Reading: <strong>{hoveredSensor.reading}</strong> ({hoveredSensor.readingType})</div>
              <div style={{ color: 'var(--text-tertiary)', marginTop: '2px' }}>Location: {hoveredSensor.location}</div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Map Legend & Quick Zone Filter */}
      <div style={{
        padding: '10px 18px',
        backgroundColor: 'var(--bg-topbar)',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <MineLegend />

        {/* Click notice */}
        <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontStyle: 'italic' }}>
          * Click any zone polygon or sensor pin to inspect detailed geotechnical telemetry & response protocols.
        </span>
      </div>

      {/* Zone Detail Side Inspector Drawer */}
      {selectedZone && (
        <ZoneDetailDrawer zone={selectedZone} onClose={() => setSelectedZone(null)} />
      )}
    </div>
  );
}

export default MineMap;
