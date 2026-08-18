import React, { useState } from 'react';

export function TelemetryMultiChart({ 
  data = [], 
  height = 260, 
  activeMetric = 'all', 
  timeRange = '24H', 
  onTimeRangeChange = null,
  onMetricChange = null
}) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!data || data.length < 2) {
    return (
      <div style={{ height: `${height}px`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-tertiary)' }}>
        Loading historical telemetry stream...
      </div>
    );
  }

  const metricsConfig = {
    vibration: { label: 'Vibration (PPV)', unit: 'mm/s', color: '#F97316', max: 20 },
    rainfall: { label: 'Rainfall', unit: 'mm/h', color: '#38BDF8', max: 50 },
    displacement: { label: 'Displacement', unit: 'mm', color: '#EF4444', max: 8 },
    porePressure: { label: 'Pore Pressure', unit: 'kPa', color: '#A855F7', max: 260 },
    slopeStability: { label: 'Factor of Safety', unit: 'FoS', color: '#10B981', max: 2.2 }
  };

  const padding = { top: 25, right: 35, bottom: 35, left: 50 };
  const viewBoxWidth = 720;
  const viewBoxHeight = height;
  const chartWidth = viewBoxWidth - padding.left - padding.right;
  const chartHeight = viewBoxHeight - padding.top - padding.bottom;

  // Render a normalized line path for a given metric
  const renderMetricPath = (key, color, maxVal) => {
    const points = data.map((d, i) => {
      const val = d[key] || 0;
      const x = padding.left + (i / (data.length - 1)) * chartWidth;
      const y = padding.top + (1 - Math.min(maxVal, val) / maxVal) * chartHeight;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    return (
      <path
        key={key}
        d={`M ${points.join(' L ')}`}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    );
  };

  const activeMetricsList = activeMetric === 'all' 
    ? ['vibration', 'rainfall', 'displacement', 'porePressure'] 
    : [activeMetric];

  const hoveredData = hoveredIndex !== null ? data[hoveredIndex] : null;

  return (
    <div>
      {/* Top Header & Range Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '12px' }}>
        {/* Metric Selector Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <button
            onClick={() => onMetricChange && onMetricChange('all')}
            style={{
              padding: '3px 8px',
              borderRadius: '4px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 600,
              backgroundColor: activeMetric === 'all' ? 'rgba(255,255,255,0.15)' : 'var(--bg-card)',
              color: activeMetric === 'all' ? '#FFFFFF' : 'var(--text-tertiary)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            All Parameters
          </button>
          {Object.entries(metricsConfig).map(([k, cfg]) => {
            const isSelected = activeMetric === k;
            return (
              <button
                key={k}
                onClick={() => onMetricChange && onMetricChange(k)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 600,
                  backgroundColor: isSelected ? `${cfg.color}22` : 'var(--bg-card)',
                  color: isSelected ? cfg.color : 'var(--text-secondary)',
                  border: `1px solid ${isSelected ? cfg.color : 'var(--border-subtle)'}`
                }}
              >
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: cfg.color }} />
                <span>{cfg.label}</span>
              </button>
            );
          })}
        </div>

        {/* Time-range Selector (1H, 6H, 24H, 7D) */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', backgroundColor: 'var(--bg-card-subtle)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
          {['1H', '6H', '24H', '7D'].map(range => (
            <button
              key={range}
              onClick={() => onTimeRangeChange && onTimeRangeChange(range)}
              style={{
                padding: '3px 8px',
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                backgroundColor: timeRange === range ? '#F59E0B' : 'transparent',
                color: timeRange === range ? '#090D14' : 'var(--text-secondary)'
              }}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* SVG Canvas */}
      <svg
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        style={{ width: '100%', height: 'auto', overflow: 'visible', display: 'block' }}
        onMouseLeave={() => setHoveredIndex(null)}
      >
        {/* Horizontal grid */}
        {[0, 0.25, 0.5, 0.75, 1].map(ratio => {
          const y = padding.top + ratio * chartHeight;
          return (
            <line
              key={ratio}
              x1={padding.left}
              y1={y}
              x2={viewBoxWidth - padding.right}
              y2={y}
              stroke="rgba(255, 255, 255, 0.05)"
              strokeDasharray="2 2"
            />
          );
        })}

        {/* Active Metric Lines */}
        {activeMetricsList.map(m => renderMetricPath(m, metricsConfig[m].color, metricsConfig[m].max))}

        {/* X Axis Time Labels */}
        {data.filter((_, idx) => idx % Math.ceil(data.length / 6) === 0 || idx === data.length - 1).map((d, i) => {
          const idxInOrig = data.indexOf(d);
          const x = padding.left + (idxInOrig / (data.length - 1)) * chartWidth;
          return (
            <text
              key={i}
              x={x}
              y={viewBoxHeight - 10}
              fill="var(--text-tertiary)"
              fontSize="10"
              fontFamily="var(--font-mono)"
              textAnchor="middle"
            >
              {d.time}
            </text>
          );
        })}

        {/* Invisible vertical hover slices */}
        {data.map((_, idx) => {
          const x = padding.left + (idx / (data.length - 1)) * chartWidth;
          return (
            <line
              key={idx}
              x1={x}
              y1={padding.top}
              x2={x}
              y2={padding.top + chartHeight}
              stroke="transparent"
              strokeWidth={Math.max(10, chartWidth / data.length)}
              style={{ cursor: 'crosshair' }}
              onMouseEnter={() => setHoveredIndex(idx)}
            />
          );
        })}

        {/* Hover Crosshair line */}
        {hoveredIndex !== null && (
          <line
            x1={padding.left + (hoveredIndex / (data.length - 1)) * chartWidth}
            y1={padding.top}
            x2={padding.left + (hoveredIndex / (data.length - 1)) * chartWidth}
            y2={padding.top + chartHeight}
            stroke="rgba(255, 255, 255, 0.3)"
            strokeDasharray="3 3"
          />
        )}
      </svg>

      {/* Hover Information Ribbon */}
      {hoveredData ? (
        <div style={{
          marginTop: '10px',
          padding: '8px 12px',
          backgroundColor: 'var(--bg-card-subtle)',
          borderRadius: '6px',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)'
        }}>
          <span style={{ color: '#FFFFFF', fontWeight: 700 }}>
            TIME: {hoveredData.time}
          </span>
          <span style={{ color: '#F97316' }}>
            Vibration: <strong>{hoveredData.vibration} mm/s</strong>
          </span>
          <span style={{ color: '#38BDF8' }}>
            Rain: <strong>{hoveredData.rainfall} mm/h</strong>
          </span>
          <span style={{ color: '#EF4444' }}>
            Disp: <strong>{hoveredData.displacement} mm</strong>
          </span>
          <span style={{ color: '#A855F7' }}>
            Pore: <strong>{hoveredData.porePressure} kPa</strong>
          </span>
          <span style={{ color: '#10B981' }}>
            FoS: <strong>{hoveredData.slopeStability}</strong>
          </span>
        </div>
      ) : (
        <div style={{ marginTop: '10px', fontSize: '10px', color: 'var(--text-tertiary)', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
          Hover anywhere on the timeline to inspect multi-parameter values
        </div>
      )}
    </div>
  );
}

export default TelemetryMultiChart;
