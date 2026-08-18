import React, { useState } from 'react';

export function RiskTrendChart({ data = [], height = 240, title = 'Risk Probability Trend (24H)' }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!data || data.length < 2) {
    return (
      <div style={{ height: `${height}px`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)' }}>
        Loading risk trend telemetry...
      </div>
    );
  }

  const padding = { top: 20, right: 30, bottom: 35, left: 45 };
  const viewBoxWidth = 700;
  const viewBoxHeight = height;
  const chartWidth = viewBoxWidth - padding.left - padding.right;
  const chartHeight = viewBoxHeight - padding.top - padding.bottom;

  // Max scale is 100%
  const maxVal = 100;
  const minVal = 0;

  const points = data.map((d, index) => {
    const x = padding.left + (index / (data.length - 1)) * chartWidth;
    const y = padding.top + (1 - d.riskScore / maxVal) * chartHeight;
    return { x, y, data: d };
  });

  const pathD = `M ${points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' L ')}`;
  const fillD = `${pathD} L ${points[points.length - 1].x},${padding.top + chartHeight} L ${points[0].x},${padding.top + chartHeight} Z`;

  // Threshold Y positions
  const yCritical = padding.top + (1 - 80 / maxVal) * chartHeight;
  const yHigh = padding.top + (1 - 60 / maxVal) * chartHeight;
  const yMod = padding.top + (1 - 35 / maxVal) * chartHeight;

  return (
    <div style={{ width: '100%', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <span style={{ fontFamily: 'var(--font-heading)', fontSize: '13px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
          {title}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '10px', fontFamily: 'var(--font-mono)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--risk-critical)' }}>
            <span style={{ width: '8px', height: '2px', backgroundColor: 'var(--risk-critical)' }} />
            Critical (80%)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--risk-high)' }}>
            <span style={{ width: '8px', height: '2px', backgroundColor: 'var(--risk-high)' }} />
            High (60%)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--risk-moderate)' }}>
            <span style={{ width: '8px', height: '2px', backgroundColor: 'var(--risk-moderate)' }} />
            Moderate (35%)
          </span>
        </div>
      </div>

      <svg 
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`} 
        style={{ width: '100%', height: 'auto', overflow: 'visible', display: 'block' }}
        onMouseLeave={() => setHoveredPoint(null)}
      >
        <defs>
          <linearGradient id="riskAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" stopOpacity="0.45" />
            <stop offset="40%" stopColor="#F97316" stopOpacity="0.30" />
            <stop offset="80%" stopColor="#F59E0B" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#10B981" stopOpacity="0.02" />
          </linearGradient>
        </defs>

        {/* Grid lines & Y Axis values */}
        {[0, 25, 50, 75, 100].map(val => {
          const y = padding.top + (1 - val / maxVal) * chartHeight;
          return (
            <g key={val}>
              <line 
                x1={padding.left} 
                y1={y} 
                x2={viewBoxWidth - padding.right} 
                y2={y} 
                stroke="rgba(255, 255, 255, 0.05)" 
                strokeDasharray="3 3" 
              />
              <text 
                x={padding.left - 8} 
                y={y + 3} 
                fill="var(--text-tertiary)" 
                fontSize="10" 
                fontFamily="var(--font-mono)" 
                textAnchor="end"
              >
                {val}%
              </text>
            </g>
          );
        })}

        {/* Threshold Reference Lines */}
        <line 
          x1={padding.left} 
          y1={yCritical} 
          x2={viewBoxWidth - padding.right} 
          y2={yCritical} 
          stroke="rgba(239, 68, 68, 0.4)" 
          strokeWidth="1" 
          strokeDasharray="4 2" 
        />
        <line 
          x1={padding.left} 
          y1={yHigh} 
          x2={viewBoxWidth - padding.right} 
          y2={yHigh} 
          stroke="rgba(249, 115, 22, 0.35)" 
          strokeWidth="1" 
          strokeDasharray="4 2" 
        />

        {/* Area fill */}
        <path d={fillD} fill="url(#riskAreaGradient)" />

        {/* Main Line stroke */}
        <path 
          d={pathD} 
          fill="none" 
          stroke="#F97316" 
          strokeWidth="2.5" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
        />

        {/* X Axis Time Labels (Show ~6 evenly spaced) */}
        {points.filter((_, idx) => idx % Math.ceil(points.length / 6) === 0 || idx === points.length - 1).map((p, i) => (
          <text 
            key={i} 
            x={p.x} 
            y={viewBoxHeight - 10} 
            fill="var(--text-tertiary)" 
            fontSize="10" 
            fontFamily="var(--font-mono)" 
            textAnchor="middle"
          >
            {p.data.time}
          </text>
        ))}

        {/* Interactive Hover Nodes */}
        {points.map((p, idx) => (
          <circle
            key={idx}
            cx={p.x}
            cy={p.y}
            r={hoveredPoint?.idx === idx ? 5 : 2}
            fill={p.data.riskScore >= 80 ? '#EF4444' : p.data.riskScore >= 60 ? '#F97316' : '#F59E0B'}
            stroke="#090D14"
            strokeWidth={1.5}
            style={{ cursor: 'pointer', transition: 'r 0.15s ease' }}
            onMouseEnter={() => setHoveredPoint({ ...p, idx })}
          />
        ))}

        {/* Tooltip Overlay */}
        {hoveredPoint && (
          <g transform={`translate(${Math.min(viewBoxWidth - 140, Math.max(padding.left, hoveredPoint.x - 60))}, ${Math.max(10, hoveredPoint.y - 45)})`}>
            <rect 
              width="120" 
              height="38" 
              rx="4" 
              fill="#0F172A" 
              stroke="rgba(255, 255, 255, 0.2)" 
              strokeWidth="1" 
              filter="drop-shadow(0 4px 6px rgba(0,0,0,0.5))"
            />
            <text x="60" y="15" fill="#9CA3AF" fontSize="9" fontFamily="var(--font-mono)" textAnchor="middle">
              {hoveredPoint.data.time}
            </text>
            <text x="60" y="30" fill="#FFFFFF" fontSize="11" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">
              Risk: {hoveredPoint.data.riskScore}%
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}

export default RiskTrendChart;
