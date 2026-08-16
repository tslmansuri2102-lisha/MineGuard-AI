import React, { useState } from 'react';
import { HistoricalTelemetryPoint } from '../../types/telemetry';
import { formatNumber } from '../../utils/formatting';

interface RollingMetricChartProps {
  title: string;
  metricKey: keyof HistoricalTelemetryPoint;
  unit: string;
  history: HistoricalTelemetryPoint[];
  strokeColor: string;
  fillColor: string;
  fixedMin?: number;
  fixedMax?: number;
  height?: number;
}

export const RollingMetricChart: React.FC<RollingMetricChartProps> = ({
  title,
  metricKey,
  unit,
  history,
  strokeColor,
  fillColor,
  fixedMin,
  fixedMax,
  height = 130,
}) => {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  const dataPoints = history.map((item) => {
    const val = item[metricKey];
    return typeof val === 'number' ? val : 0;
  });

  const latestVal = dataPoints.length > 0 ? dataPoints[dataPoints.length - 1] : 0;

  // Calculate dynamic bounds
  const rawMin = Math.min(...(dataPoints.length > 0 ? dataPoints : [0]));
  const rawMax = Math.max(...(dataPoints.length > 0 ? dataPoints : [100]));

  const minY = fixedMin !== undefined ? fixedMin : Math.max(0, Math.floor(rawMin * 0.9));
  const maxY = fixedMax !== undefined ? fixedMax : Math.max(minY + 1, Math.ceil(rawMax * 1.15));
  const yRange = maxY - minY || 1;

  // SVG dimensions
  const svgWidth = 400;
  const svgHeight = height;
  const padding = { top: 12, bottom: 20, left: 10, right: 10 };
  const chartWidth = svgWidth - padding.left - padding.right;
  const chartHeight = svgHeight - padding.top - padding.bottom;

  // Generate coordinates
  const points = dataPoints.map((val, idx) => {
    const total = Math.max(2, dataPoints.length);
    const x = padding.left + (idx / (total - 1)) * chartWidth;
    const normY = Math.min(1, Math.max(0, (val - minY) / yRange));
    const y = padding.top + chartHeight - normY * chartHeight;
    return { x, y, val, time: history[idx]?.timeLabel || '' };
  });

  const linePath = points.length > 0
    ? points.reduce((acc, pt, i) => (i === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`), '')
    : '';

  const areaPath = points.length > 0
    ? `${linePath} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${points[0].x} ${padding.top + chartHeight} Z`
    : '';

  const hoverPt = hoverIndex !== null && points[hoverIndex] ? points[hoverIndex] : null;

  return (
    <div style={{
      background: 'var(--bg-panel-elevated)',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-subtle)',
      padding: '12px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    }}>
      {/* Chart Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <div>
          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
            {title}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '1.1rem',
            fontWeight: 800,
            color: strokeColor,
          }}>
            {formatNumber(latestVal, metricKey === 'strain' || metricKey === 'vibration_g' ? 2 : 1)}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{unit}</span>
        </div>
      </div>

      {/* SVG Canvas */}
      <div style={{ width: '100%', position: 'relative' }}>
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          style={{ width: '100%', height: `${height}px`, overflow: 'visible' }}
          onMouseLeave={() => setHoverIndex(null)}
        >
          <defs>
            <linearGradient id={`grad-${String(metricKey)}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={fillColor} stopOpacity="0.45" />
              <stop offset="100%" stopColor={fillColor} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Horizontal Grid lines */}
          <line
            x1={padding.left}
            y1={padding.top}
            x2={svgWidth - padding.right}
            y2={padding.top}
            stroke="var(--border-subtle)"
            strokeDasharray="3 3"
          />
          <line
            x1={padding.left}
            y1={padding.top + chartHeight / 2}
            x2={svgWidth - padding.right}
            y2={padding.top + chartHeight / 2}
            stroke="var(--border-subtle)"
            strokeDasharray="3 3"
          />
          <line
            x1={padding.left}
            y1={padding.top + chartHeight}
            x2={svgWidth - padding.right}
            y2={padding.top + chartHeight}
            stroke="var(--border-subtle)"
          />

          {/* Area & Line */}
          {areaPath && <path d={areaPath} fill={`url(#grad-${String(metricKey)})`} />}
          {linePath && (
            <path
              d={linePath}
              fill="none"
              stroke={strokeColor}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Hover tracker line & point */}
          {hoverPt && (
            <>
              <line
                x1={hoverPt.x}
                y1={padding.top}
                x2={hoverPt.x}
                y2={padding.top + chartHeight}
                stroke="var(--text-accent)"
                strokeDasharray="2 2"
              />
              <circle
                cx={hoverPt.x}
                cy={hoverPt.y}
                r="4.5"
                fill={strokeColor}
                stroke="#0f172a"
                strokeWidth="2"
              />
            </>
          )}

          {/* Invisible hover overlay triggers */}
          {points.map((pt, idx) => {
            const stepWidth = chartWidth / (points.length || 1);
            return (
              <rect
                key={idx}
                x={pt.x - stepWidth / 2}
                y={padding.top}
                width={stepWidth}
                height={chartHeight}
                fill="transparent"
                onMouseEnter={() => setHoverIndex(idx)}
                style={{ cursor: 'crosshair' }}
              />
            );
          })}
        </svg>

        {/* Floating Tooltip */}
        {hoverPt && (
          <div
            style={{
              position: 'absolute',
              top: '6px',
              left: `${(hoverPt.x / svgWidth) * 100}%`,
              transform: 'translateX(-50%)',
              background: 'rgba(15, 23, 42, 0.95)',
              border: '1px solid var(--border-medium)',
              borderRadius: 'var(--radius-sm)',
              padding: '2px 8px',
              fontSize: '0.68rem',
              color: '#f8fafc',
              fontFamily: 'var(--font-mono)',
              pointerEvents: 'none',
              whiteSpace: 'nowrap',
              boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
            }}
          >
            {formatNumber(hoverPt.val, metricKey === 'strain' || metricKey === 'vibration_g' ? 2 : 1)} {unit} ({hoverPt.time})
          </div>
        )}
      </div>

      {/* Axis Scale Range */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '0.65rem',
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-mono)',
      }}>
        <span>Min: {formatNumber(minY, 0)} {unit}</span>
        <span>Points: {history.length}</span>
        <span>Max: {formatNumber(maxY, 0)} {unit}</span>
      </div>
    </div>
  );
};
