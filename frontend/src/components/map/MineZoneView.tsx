import React from 'react';
import { MapPin, Navigation, Radio, Maximize2, Shield } from 'lucide-react';
import { NormalizedRiskAssessment, SensorTelemetryPayload } from '../../types/telemetry';
import { RISK_LEVEL_CONFIG } from '../../utils/constants';

interface MineZoneViewProps {
  risk: NormalizedRiskAssessment;
  telemetry: SensorTelemetryPayload;
}

export const MineZoneView: React.FC<MineZoneViewProps> = ({ risk, telemetry }) => {
  const config = RISK_LEVEL_CONFIG[risk.level] || RISK_LEVEL_CONFIG.LOW;
  const isCritical = risk.level === 'CRITICAL';
  const isHigh = risk.level === 'HIGH';

  return (
    <div className="cmd-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="cmd-panel-header">
        <div className="cmd-panel-title">
          <Navigation size={16} color="#38bdf8" />
          <span>Mine Schematic & Geotechnical Zone Map</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge" style={{ background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', fontSize: '0.65rem' }}>
            DEM/GIS INTEGRATION READY
          </span>
        </div>
      </div>

      <div
        className="cmd-panel-body"
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          gap: '12px',
        }}
      >
        {/* Schematic SVG Open-Pit Mine Bench Model */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '210px',
            background: 'radial-gradient(ellipse at center, #162036 0%, #0b0f17 100%)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
            overflow: 'hidden',
          }}
        >
          <svg
            viewBox="0 0 460 210"
            style={{ width: '100%', height: '100%' }}
          >
            <defs>
              {/* Radial gradient for zone glow */}
              <radialGradient id="zoneGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor={config.color} stopOpacity="0.45" />
                <stop offset="70%" stopColor={config.color} stopOpacity="0.1" />
                <stop offset="100%" stopColor={config.color} stopOpacity="0" />
              </radialGradient>
            </defs>

            {/* Open Pit Bench Contours (Simulated Topography) */}
            <path
              d="M 20 180 Q 230 200 440 180 L 440 210 L 20 210 Z"
              fill="#0d1527"
              stroke="#1e293b"
              strokeWidth="1.5"
            />
            <path
              d="M 40 145 Q 230 170 420 145 L 420 180 Q 230 200 40 180 Z"
              fill="#111c33"
              stroke="#1e293b"
              strokeWidth="1.5"
            />
            <path
              d="M 70 110 Q 230 135 390 110 L 390 145 Q 230 170 70 145 Z"
              fill="#16233f"
              stroke="#334155"
              strokeWidth="1.5"
            />
            <path
              d="M 100 75 Q 230 98 360 75 L 360 110 Q 230 135 100 110 Z"
              fill="#1c2d52"
              stroke="#475569"
              strokeWidth="1.5"
            />
            {/* Pit Crest Top Bench */}
            <path
              d="M 140 40 Q 230 60 320 40 L 320 75 Q 230 98 140 75 Z"
              fill="#223663"
              stroke="#64748b"
              strokeWidth="1.5"
            />

            {/* Non-Monitored Inactive Bench Zones (for spatial reference) */}
            <polygon
              points="150,45 210,48 205,72 145,70"
              fill="rgba(100, 116, 139, 0.15)"
              stroke="rgba(100, 116, 139, 0.4)"
              strokeDasharray="2 2"
            />
            <text x="155" y="62" fill="#64748b" fontSize="8" fontFamily="var(--font-mono)">ZONE-001</text>

            <polygon
              points="250,48 310,45 315,70 255,72"
              fill="rgba(100, 116, 139, 0.15)"
              stroke="rgba(100, 116, 139, 0.4)"
              strokeDasharray="2 2"
            />
            <text x="260" y="62" fill="#64748b" fontSize="8" fontFamily="var(--font-mono)">ZONE-002</text>

            {/* ACTIVE MONITORED ZONE: ZONE-003 (Bench #3 Highwall Sector) */}
            <polygon
              points="160,80 300,80 320,135 140,135"
              fill="url(#zoneGlow)"
              stroke={config.color}
              strokeWidth={isCritical ? '2.5' : '1.5'}
              strokeDasharray={isCritical ? '4 2' : 'none'}
              style={{
                transition: 'stroke 0.4s ease, fill 0.4s ease',
              }}
            />

            {/* Active Zone Label */}
            <rect x="180" y="88" width="100" height="18" rx="3" fill="rgba(15, 23, 42, 0.85)" stroke={config.color} strokeWidth="1" />
            <text x="230" y="101" fill={config.textColor} fontSize="9" fontWeight="bold" fontFamily="var(--font-mono)" textAnchor="middle">
              ZONE-003 [ACTIVE]
            </text>

            {/* SENSOR-003 Deployment Node Position */}
            <circle cx="230" cy="120" r={isCritical ? "8" : "6"} fill={config.color} opacity="0.85">
              {isCritical && <animate attributeName="r" values="6;10;6" dur="1.2s" repeatCount="indefinite" />}
            </circle>
            <circle cx="230" cy="120" r="3" fill="#ffffff" />
            <text x="230" y="142" fill="#38bdf8" fontSize="9" fontWeight="bold" fontFamily="var(--font-mono)" textAnchor="middle">
              SENSOR-003 (In-Situ Node)
            </text>

            {/* Compass Rose */}
            <g transform="translate(420, 30)">
              <circle cx="0" cy="0" r="14" fill="rgba(15, 23, 42, 0.7)" stroke="#334155" />
              <polygon points="0,-10 3,0 0,2 -3,0" fill="#f87171" />
              <polygon points="0,10 3,0 0,-2 -3,0" fill="#94a3b8" />
              <text x="0" y="-12" fill="#f87171" fontSize="7" fontWeight="bold" textAnchor="middle">N</text>
            </g>
          </svg>

          {/* Overlay Coordinates & Identification Badges */}
          <div
            style={{
              position: 'absolute',
              top: '8px',
              left: '10px',
              display: 'flex',
              flexDirection: 'column',
              gap: '2px',
              fontSize: '0.68rem',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
              background: 'rgba(15, 23, 42, 0.75)',
              padding: '4px 8px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <span>MINE: <strong style={{ color: 'var(--text-primary)' }}>{telemetry.mine_id}</strong></span>
            <span>ZONE: <strong style={{ color: config.textColor }}>{telemetry.zone_id}</strong></span>
            <span>NODE: <strong style={{ color: '#38bdf8' }}>{telemetry.sensor_id}</strong></span>
          </div>

          <div
            style={{
              position: 'absolute',
              bottom: '8px',
              right: '10px',
              fontSize: '0.65rem',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
              background: 'rgba(15, 23, 42, 0.75)',
              padding: '2px 6px',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            Grid: 23°48'N, 86°22'E (Open-Pit Sector)
          </div>
        </div>

        {/* Spatial Status Information */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '8px',
            fontSize: '0.72rem',
            background: 'var(--bg-panel-elevated)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Monitored Sector:</span>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>North Highwall Bench #3</div>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Geotechnical Risk:</span>
            <div style={{ fontWeight: 700, color: config.textColor }}>{config.badgeText}</div>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)' }}>Coverage:</span>
            <div style={{ fontWeight: 700, color: '#38bdf8' }}>1 Node Active (Extensible)</div>
          </div>
        </div>
      </div>
    </div>
  );
};
